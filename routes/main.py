from flask import Blueprint, render_template, session, g
from models import User, get_db_session
from config import Config

main_bp = Blueprint('main', __name__)

@main_bp.before_request
def load_logged_in_user():
    """リクエスト前にログインユーザー情報をロードする"""
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        db_session = get_db_session(Config.DATABASE_URL)
        g.user = db_session.query(User).filter(User.id == user_id).first()
        db_session.close()

@main_bp.route('/')
def index():
    """ホームページ表示"""
    return render_template('main/index.html')
