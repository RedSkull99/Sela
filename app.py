from flask import Flask, render_template
from extensions import db, login_manager, jwt
from models import User
import os

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users_v2.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'super-secret-key-change-this'
    app.config['JWT_SECRET_KEY'] = 'jwt-secret-key-change-this'
    
    # Upload Configuration
    UPLOAD_FOLDER = 'static/profile_pics'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    
    # Create upload folder if it doesn't exist
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    jwt.init_app(app)

    from auth import bp as auth_bp
    app.register_blueprint(auth_bp)


    from main import bp as main_bp
    app.register_blueprint(main_bp)

    from admin import bp as admin_bp
    app.register_blueprint(admin_bp)

    from models import CartItem
    from flask_login import current_user
    
    @app.context_processor
    def inject_context():
        cart_count = 0
        if current_user.is_authenticated:
            cart_count = CartItem.query.filter_by(user_id=current_user.id).count()
        return {'cart_count': cart_count}

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html', error=e), 500
    
    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
