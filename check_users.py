from app import create_app
from models import User
from extensions import db

app = create_app()

with app.app_context():
    users = User.query.all()
    print(f"Total users: {len(users)}")
    for u in users:
        print(f"User: {u.email}, ID: {u.id}, Is Admin: {u.is_admin}")
