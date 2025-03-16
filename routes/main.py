from flask import Blueprint, render_template, g

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """ホームページ表示"""
    return render_template('main/index.html')
