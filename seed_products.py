from app import create_app
from extensions import db
from models import Product

app = create_app()

with app.app_context():
    # Create tables if they don't exist (models.py updates are reflected here)
    db.create_all()

    # Check if products exist
    if Product.query.count() == 0:
        products = [
            Product(name="High-Performance Laptop", description="A powerful laptop for all your computing needs.", price=1200.00, image_file="laptop.jpg"),
            Product(name="Smartphone X", description="The latest smartphone with cutting-edge features.", price=800.00, image_file="phone.jpg"),
            Product(name="Wireless Headphones", description="Noise-cancelling headphones for immersive sound.", price=150.00, image_file="headphones.jpg"),
            Product(name="Smart Watch", description="Track your fitness and stay connected.", price=250.00, image_file="watch.jpg"),
            Product(name="4K Monitor", description="Crystal clear display for work and play.", price=300.00, image_file="monitor.jpg"),
            Product(name="Mechanical Keyboard", description="Tactile typing experience.", price=100.00, image_file="keyboard.jpg"),
        ]
        
        db.session.bulk_save_objects(products)
        db.session.commit()
        print("Products seeded successfully!")
    else:
        print("Products already exist.")
