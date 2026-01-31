from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from models import User, Product, CartItem, Order, OrderItem
from extensions import db
from datetime import datetime
import os
from werkzeug.utils import secure_filename

bp = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/')
def home():
    products = Product.query.all()
    # Check if user has items in cart to show count badge if needed (optional for now)
    return render_template('home.html', products=products)

@bp.route('/about')
def about():
    return render_template('about.html')

@bp.route('/contact')
def contact():
    return render_template('contact.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@bp.route('/upload_profile_pic', methods=['POST'])
@login_required
def upload_profile_pic():
    if 'profile_pic' not in request.files:
        flash('No file part')
        return redirect(url_for('main.dashboard'))
    file = request.files['profile_pic']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('main.dashboard'))
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.root_path, 'static', 'profile_pics', filename)
        file.save(file_path)
        current_user.profile_pic = filename
        db.session.commit()
        flash('Profile picture uploaded successfully')
    else:
        flash('Allowed image types are - png, jpg, jpeg, gif')
    return redirect(url_for('main.dashboard'))

@bp.route('/product/<int:product_id>')
def product_details(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_details.html', product=product)

@bp.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    quantity = int(request.form.get('quantity', 1))
    
    # Check if item already in cart
    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(user_id=current_user.id, product_id=product_id, quantity=quantity)
        db.session.add(cart_item)
    
    db.session.commit()
    flash(f'{product.name} added to cart!')
    return redirect(url_for('main.home'))

@bp.route('/cart')
@login_required
def cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total_price)

@bp.route('/update_cart/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    if cart_item.user_id != current_user.id:
        return redirect(url_for('main.cart'))
        
    action = request.form.get('action')
    if action == 'increase':
        cart_item.quantity += 1
    elif action == 'decrease':
        cart_item.quantity -= 1
        if cart_item.quantity <= 0:
            db.session.delete(cart_item)
    elif action == 'remove':
        db.session.delete(cart_item)
        
    db.session.commit()
    return redirect(url_for('main.cart'))

@bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash('Your cart is empty.')
        return redirect(url_for('main.home'))
        
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    
    if request.method == 'POST':
        # Process Order
        order = Order(user_id=current_user.id, total_price=total_price)
        db.session.add(order)
        db.session.commit() # Commit to get order ID
        
        for item in cart_items:
            order_item = OrderItem(order_id=order.id, product_id=item.product.id, quantity=item.quantity, price=item.product.price)
            db.session.add(order_item)
            db.session.delete(item) # Remove from cart
            
        db.session.commit()
        flash('Order placed successfully! Thank you for your purchase.')
        return redirect(url_for('main.home'))
        
    return render_template('checkout.html', cart_items=cart_items, total=total_price)

