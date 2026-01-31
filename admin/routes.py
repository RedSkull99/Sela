from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from extensions import db
from models import Product, Category, Order, User, OrderItem
from . import bp
from werkzeug.utils import secure_filename
import os
from datetime import datetime

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.before_request
@login_required
def require_admin():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('main.home'))

@bp.route('/')
def dashboard():
    product_count = Product.query.count()
    category_count = Category.query.count()
    order_count = Order.query.count()
    user_count = User.query.count()
    recent_orders = Order.query.order_by(Order.date_ordered.desc()).limit(5).all()
    return render_template('admin/dashboard.html', 
                           product_count=product_count, 
                           category_count=category_count, 
                           order_count=order_count, 
                           user_count=user_count,
                           recent_orders=recent_orders)

# --- Category Management ---
@bp.route('/categories')
def categories():
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)

@bp.route('/categories/add', methods=['GET', 'POST'])
def add_category():
    if request.method == 'POST':
        name = request.form.get('name')
        if not name:
            flash('Category name is required.')
            return redirect(url_for('admin.add_category'))
        
        if Category.query.filter_by(name=name).first():
            flash('Category already exists.')
            return redirect(url_for('admin.add_category'))

        new_category = Category(name=name)
        db.session.add(new_category)
        db.session.commit()
        flash('Category added successfully!')
        return redirect(url_for('admin.categories'))
    return render_template('admin/add_category.html')

@bp.route('/categories/delete/<int:id>', methods=['POST'])
def delete_category(id):
    category = Category.query.get_or_404(id)
    # Check if category has products
    if category.products:
        flash('Cannot delete category with associated products.')
        return redirect(url_for('admin.categories'))
    
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted.')
    return redirect(url_for('admin.categories'))

# --- Product Management ---
@bp.route('/products')
def products():
    products = Product.query.all()
    return render_template('admin/products.html', products=products)

@bp.route('/products/add', methods=['GET', 'POST'])
def add_product():
    categories = Category.query.all()
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        category_id = request.form.get('category_id')
        
        if not category_id:
            flash('Please select a category.')
            return render_template('admin/add_product.html', categories=categories)

        image_file = request.files.get('image')
        image_filename = 'default_product.jpg'

        if image_file and image_file.filename != '' and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
            prod_img_path = os.path.join(current_app.root_path, 'static/product_images')
            if not os.path.exists(prod_img_path):
                os.makedirs(prod_img_path)
            
            image_file.save(os.path.join(prod_img_path, unique_filename))
            image_filename = unique_filename

        new_product = Product(name=name, description=description, price=price, 
                              image_file=image_filename, category_id=category_id)
        db.session.add(new_product)
        db.session.commit()
        flash('Product added successfully!')
        return redirect(url_for('admin.products'))
    return render_template('admin/add_product.html', categories=categories)

@bp.route('/products/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    product = Product.query.get_or_404(id)
    categories = Category.query.all()
    
    if request.method == 'POST':
        product.name = request.form['name']
        product.description = request.form['description']
        product.price = float(request.form['price'])
        product.category_id = request.form.get('category_id')
        
        image_file = request.files.get('image')
        if image_file and image_file.filename != '' and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
            prod_img_path = os.path.join(current_app.root_path, 'static/product_images')
            if not os.path.exists(prod_img_path):
                os.makedirs(prod_img_path)
            
            image_file.save(os.path.join(prod_img_path, unique_filename))
            product.image_file = unique_filename
            
        db.session.commit()
        flash('Product updated successfully!')
        return redirect(url_for('admin.products'))
        
    return render_template('admin/edit_product.html', product=product, categories=categories)

@bp.route('/products/delete/<int:id>', methods=['POST'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted.')
    return redirect(url_for('admin.products'))

# --- Order Management ---
@bp.route('/orders')
def orders():
    orders = Order.query.order_by(Order.date_ordered.desc()).all()
    return render_template('admin/orders.html', orders=orders)

@bp.route('/orders/<int:id>', methods=['GET', 'POST'])
def order_details(id):
    order = Order.query.get_or_404(id)
    if request.method == 'POST':
        new_status = request.form.get('status')
        if new_status:
            order.status = new_status
            db.session.commit()
            flash(f'Order status updated to {new_status}.')
            return redirect(url_for('admin.order_details', id=id))
            
    return render_template('admin/order_details.html', order=order)
