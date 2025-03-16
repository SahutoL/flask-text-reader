from flask import Flask, g, render_template
from config import Config
from routes.auth import auth_bp
from routes.files import files_bp
from routes.main import main_bp
import os
from models import init_db

def create_app(config_class=Config):
    """アプリケーションファクトリ関数"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # アップロードディレクトリの確認
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # ブループリントの登録
    app.register_blueprint(auth_bp)
    app.register_blueprint(files_bp, url_prefix='/files')
    app.register_blueprint(main_bp)

    # セッションの設定
    app.secret_key = app.config['SECRET_KEY']

    # エラーハンドラー
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('error/500.html'), 500

    return app

app = create_app()

if __name__ == '__main__':
    # データベースの初期化
    try:
        init_db(Config.DATABASE_URL)
        print("データベースが初期化されました")
    except Exception as e:
        print(f"データベース初期化エラー: {e}")

    app.run(debug=app.config['DEBUG'], host='0.0.0.0')
