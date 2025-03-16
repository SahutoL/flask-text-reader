from flask import Blueprint, request, render_template, redirect, url_for, flash, session, g
from models import User, get_db_session
from auth import PasswordManager
from config import Config
import re

auth_bp = Blueprint('auth', __name__)
password_manager = PasswordManager()

@auth_bp.before_request
def load_logged_in_user():
    """リクエスト前にログインユーザー情報をロードする"""
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        db_session = get_db_session(Config.DATABASE_URL)
        g.user = db_session.query(User).filter(User.id == user_id).first()
        db_session.close()

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """ユーザー登録機能"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        error = None
        
        # 入力検証
        if not username:
            error = 'ユーザー名は必須です'
        elif not email:
            error = 'メールアドレスは必須です'
        elif not password:
            error = 'パスワードは必須です'
        elif password != confirm_password:
            error = 'パスワードが一致しません'
        elif not re.match(r'^[a-zA-Z0-9_]+$', username):
            error = 'ユーザー名は英数字とアンダースコアのみ使用できます'
        elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            error = '有効なメールアドレスを入力してください'
        elif len(password) < 8:
            error = 'パスワードは8文字以上必要です'
            
        if error is None:
            db_session = get_db_session(Config.DATABASE_URL)
            
            # ユーザー名とメールアドレスの重複チェック
            existing_user = db_session.query(User).filter(
                (User.username == username) | (User.email == email)
            ).first()
            
            if existing_user:
                if existing_user.username == username:
                    error = 'そのユーザー名は既に使用されています'
                else:
                    error = 'そのメールアドレスは既に登録されています'
            else:
                # パスワードのハッシュ化
                password_hash = password_manager.hash_password(password)
                
                # 新規ユーザーの作成
                new_user = User(
                    username=username,
                    email=email,
                    password_hash=password_hash
                )
                
                db_session.add(new_user)
                db_session.commit()
                db_session.close()
                
                flash('アカウントが作成されました。ログインしてください。', 'success')
                return redirect(url_for('auth.login'))
            
            db_session.close()
        
        flash(error, 'error')
    
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """ログイン機能"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        error = None
        
        if not username:
            error = 'ユーザー名は必須です'
        elif not password:
            error = 'パスワードは必須です'
            
        if error is None:
            db_session = get_db_session(Config.DATABASE_URL)
            user = db_session.query(User).filter(User.username == username).first()
            
            if user is None:
                error = 'ユーザー名またはパスワードが正しくありません'
            elif not password_manager.verify_password(user.password_hash, password):
                error = 'ユーザー名またはパスワードが正しくありません'
            else:
                # セッションのクリアとユーザーIDの設定
                session.clear()
                session['user_id'] = user.id
                
                # パスワードハッシュの再ハッシュが必要かチェック
                if password_manager.check_needs_rehash(user.password_hash):
                    user.password_hash = password_manager.hash_password(password)
                    db_session.commit()
                
                db_session.close()
                return render_template('files/my_files.html')
                return redirect(url_for('main.index'))
            
            db_session.close()
        
        flash(error, 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    """ログアウト機能"""
    session.clear()
    flash('ログアウトしました', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
def profile():
    """ユーザープロフィール表示"""
    if g.user is None:
        return redirect(url_for('auth.login'))
    
    return render_template('auth/profile.html', user=g.user)
