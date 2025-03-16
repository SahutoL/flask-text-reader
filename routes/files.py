from flask import Blueprint, request, render_template, redirect, url_for, flash, session, g, current_app, send_from_directory
from models import User, File, get_db_session
from config import Config
import os
import uuid
from werkzeug.utils import secure_filename
import datetime

files_bp = Blueprint('files', __name__)

@files_bp.before_request
def load_logged_in_user():
    """リクエスト前にログインユーザー情報をロードする"""
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        db_session = get_db_session(Config.DATABASE_URL)
        g.user = db_session.query(User).filter(User.id == user_id).first()
        db_session.close()

def allowed_file(filename):
    """許可されたファイル拡張子かどうかを確認する"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'txt'

@files_bp.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """ファイルアップロード機能"""
    if g.user is None:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('ファイルが選択されていません', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('ファイルが選択されていません', 'error')
            return redirect(request.url)
        
        # ファイルタイプが許可されているか確認
        if file and allowed_file(file.filename):
            # セキュアなファイル名を生成
            original_filename = file.filename
            filename = f"{uuid.uuid4().hex}.txt"
            
            # ファイルの内容を読み込む
            content = file.read().decode('utf-8')
            content = content.replace('\n', '<br />')
            
            # データベースに保存
            db_session = get_db_session(Config.DATABASE_URL)
            new_file = File(
                filename=filename,
                original_filename=original_filename,
                content=content,
                owner_id=g.user.id
            )
            
            db_session.add(new_file)
            db_session.commit()
            db_session.close()
            
            flash('ファイルがアップロードされました', 'success')
            return redirect(url_for('files.my_files'))
        else:
            flash('許可されていないファイル形式です。txtファイルのみアップロード可能です。', 'error')
    
    return render_template('files/upload.html')

@files_bp.route('/my-files')
def my_files():
    """ユーザーのファイル一覧表示"""
    if g.user is None:
        return redirect(url_for('auth.login'))
    
    db_session = get_db_session(Config.DATABASE_URL)
    files = db_session.query(File).filter(File.owner_id == g.user.id).all()
    db_session.close()
    
    return render_template('files/my_files.html', files=files)

@files_bp.route('/edit/<int:file_id>', methods=['GET', 'POST'])
def edit_file(file_id):
    """ファイル名編集機能"""
    if g.user is None:
        return redirect(url_for('auth.login'))
    
    db_session = get_db_session(Config.DATABASE_URL)
    file = db_session.query(File).filter(File.id == file_id, File.owner_id == g.user.id).first()
    
    if file is None:
        db_session.close()
        flash('ファイルが見つかりません', 'error')
        return redirect(url_for('files.my_files'))
    
    if request.method == 'POST':
        new_filename = request.form.get('filename')
        
        if not new_filename:
            flash('ファイル名は必須です', 'error')
        else:
            # セキュアなファイル名を生成
            new_filename = secure_filename(new_filename)
            
            # 拡張子がない場合は追加
            if not new_filename.lower().endswith('.txt'):
                new_filename += '.txt'
            
            file.original_filename = new_filename
            file.updated_at = datetime.datetime.utcnow()
            
            db_session.commit()
            flash('ファイル名が更新されました', 'success')
            return redirect(url_for('files.my_files'))
    
    db_session.close()
    return render_template('files/edit.html', file=file)

@files_bp.route('/delete/<int:file_id>', methods=['POST'])
def delete_file(file_id):
    """ファイル削除機能"""
    if g.user is None:
        return redirect(url_for('auth.login'))
    
    db_session = get_db_session(Config.DATABASE_URL)
    file = db_session.query(File).filter(File.id == file_id, File.owner_id == g.user.id).first()
    
    if file is None:
        db_session.close()
        flash('ファイルが見つかりません', 'error')
        return redirect(url_for('files.my_files'))
    
    db_session.delete(file)
    db_session.commit()
    db_session.close()
    
    flash('ファイルが削除されました', 'success')
    return redirect(url_for('files.my_files'))

@files_bp.route('/read/<int:file_id>')
def read_file(file_id):
    """ファイル閲覧機能"""
    if g.user is None:
        return redirect(url_for('auth.login'))
    
    db_session = get_db_session(Config.DATABASE_URL)
    file = db_session.query(File).filter(File.id == file_id, File.owner_id == g.user.id).first()
    
    if file is None:
        db_session.close()
        flash('ファイルが見つかりません', 'error')
        return redirect(url_for('files.my_files'))
    
    db_session.close()
    return render_template('files/read.html', file=file)
