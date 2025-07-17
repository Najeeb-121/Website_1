import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import json
from dotenv import load_dotenv
import re

load_dotenv()

def get_youtube_video_id(url):
    """Extracts the YouTube video ID from a URL."""
    if not url:
        return None
    
    # Regex to find video ID in various YouTube URL formats
    regex = r"(?:https?://)?(?:www\.)?(?:youtube\.com/|youtu\.be/)(?:watch\?v=|embed/|v/|)(?P<video_id>[\w-]{11})"
    
    match = re.search(regex, url)
    
    if match:
        return match.group("video_id")
    
    return None


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///ecommerce.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(os.path.join(app.root_path, app.config['UPLOAD_FOLDER']), exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

# Database Models
class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_super_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_ar = db.Column(db.String(200), nullable=False)
    name_en = db.Column(db.String(200), nullable=True)
    description_ar = db.Column(db.Text, nullable=False)
    description_en = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=True)  # None means "contact for price"
    image_url = db.Column(db.String(500), nullable=True)
    youtube_url = db.Column(db.String(500), nullable=True)
    discount_percentage = db.Column(db.Float, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    additional_images = db.relationship('ProductImage', backref='product', lazy=True, cascade="all, delete-orphan")

    @property
    def discounted_price(self):
        if self.price and self.discount_percentage > 0:
            return self.price * (1 - self.discount_percentage / 100)
        return self.price

class ProductImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    customer_location = db.Column(db.String(500), nullable=False)
    customer_city = db.Column(db.String(50), nullable=False)
    items = db.Column(db.Text, nullable=False)  # JSON string of cart items
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, completed, deleted
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)

class Setting(db.Model):
    key = db.Column(db.String(100), primary_key=True)
    value = db.Column(db.Text, nullable=True)

def get_setting(key, default=None):
    setting = Setting.query.filter_by(key=key).first()
    return setting.value if setting else default

def set_setting(key, value):
    setting = Setting.query.filter_by(key=key).first()
    if setting:
        setting.value = value
    else:
        setting = Setting(key=key, value=value)
        db.session.add(setting)
    db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    products = Product.query.filter_by(is_active=True).all()
    homepage_video_url = get_setting('homepage_video_url', '')
    show_homepage_video = get_setting('show_homepage_video', '1') == '1'
    return render_template('index.html', products=products, homepage_video_url=homepage_video_url, show_homepage_video=show_homepage_video)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_detail.html', product=product)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product_id = request.json.get('product_id')
    quantity = request.json.get('quantity', 1)
    
    product = Product.query.get_or_404(product_id)
    
    if 'cart' not in session:
        session['cart'] = {}
    
    cart = session['cart']
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        cart[product_id_str]['quantity'] += quantity
    else:
        cart[product_id_str] = {
            'name': product.name_ar,
            'price': product.discounted_price,
            'quantity': quantity,
            'image_url': product.image_url
        }
    
    session['cart'] = cart
    session.modified = True
    
    return jsonify({'success': True, 'cart_count': sum(item['quantity'] for item in cart.values())})

@app.route('/cart')
def cart():
    cart = session.get('cart', {})
    cart_items = []
    total = 0
    
    for product_id, item in cart.items():
        if item['price']:  # Only add items with prices to cart
            cart_items.append({
                'id': product_id,
                'name': item['name'],
                'price': item['price'],
                'quantity': item['quantity'],
                'subtotal': item['price'] * item['quantity'],
                'image_url': item['image_url']
            })
            total += item['price'] * item['quantity']
    
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    product_id = request.json.get('product_id')
    
    if 'cart' in session and str(product_id) in session['cart']:
        del session['cart'][str(product_id)]
        session.modified = True
    
    return jsonify({'success': True})

@app.route('/checkout')
def checkout():
    cart = session.get('cart', {})
    if not cart:
        flash('سلة التسوق فارغة', 'warning')
        return redirect(url_for('index'))
    
    cart_items = []
    total = 0
    
    for product_id, item in cart.items():
        if item['price']:
            cart_items.append({
                'id': product_id,
                'name': item['name'],
                'price': item['price'],
                'quantity': item['quantity'],
                'subtotal': item['price'] * item['quantity']
            })
            total += item['price'] * item['quantity']
    
    cities = ['عمان', 'إربد', 'الزرقاء', 'العقبة', 'السلط', 'مادبا', 'الكرك', 'معان', 'الطفيلة', 'جرش', 'عجلون', 'المفرق']
    
    return render_template('checkout.html', cart_items=cart_items, total=total, cities=cities)

@app.route('/place_order', methods=['POST'])
def place_order():
    cart = session.get('cart', {})
    if not cart:
        flash('سلة التسوق فارغة', 'error')
        return redirect(url_for('index'))
    
    # Get form data
    customer_name = request.form.get('name')
    customer_email = request.form.get('email')
    customer_phone = request.form.get('phone')
    customer_location = request.form.get('location')
    customer_city = request.form.get('city')
    
    # Calculate total
    total = 0
    order_items = []
    
    for product_id, item in cart.items():
        if item['price']:
            order_items.append({
                'product_id': product_id,
                'name': item['name'],
                'price': item['price'],
                'quantity': item['quantity'],
                'subtotal': item['price'] * item['quantity']
            })
            total += item['price'] * item['quantity']
    
    # Create order
    order = Order(
        customer_name=customer_name,
        customer_email=customer_email,
        customer_phone=customer_phone,
        customer_location=customer_location,
        customer_city=customer_city,
        items=json.dumps(order_items),
        total_amount=total
    )
    
    db.session.add(order)
    db.session.commit()
    
    # Clear cart
    session.pop('cart', None)
    
    flash('تم إرسال طلبك بنجاح! سنتواصل معك قريباً', 'success')
    return redirect(url_for('order_success', order_id=order.id))

@app.route('/order_success/<int:order_id>')
def order_success(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('order_success.html', order=order)

# Admin Routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and admin.check_password(password):
            login_user(admin)
            return redirect(url_for('admin_dashboard'))
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin_dashboard():
    products_count = Product.query.count()
    orders_count = Order.query.filter_by(status='pending').count()
    total_orders = Order.query.count()
    
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                         products_count=products_count,
                         orders_count=orders_count,
                         total_orders=total_orders,
                         recent_orders=recent_orders)

@app.route('/admin/products')
@login_required
def admin_products():
    products = Product.query.order_by(Product.created_at.desc()).all()
    return render_template('admin/products.html', products=products)

@app.route('/admin/products/add', methods=['GET', 'POST'])
@login_required
def admin_add_product():
    if request.method == 'POST':
        image_filename = None
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file.filename != '':
                image_filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))


        product = Product(
            name_ar=request.form.get('name_ar'),
            name_en=request.form.get('name_en'),
            description_ar=request.form.get('description_ar'),
            description_en=request.form.get('description_en'),
            price=float(request.form.get('price')) if request.form.get('price') else None,
            image_url=f"uploads/{image_filename}" if image_filename else None,
            youtube_url=get_youtube_video_id(request.form.get('youtube_url')),
            discount_percentage=float(request.form.get('discount_percentage', 0))
        )
        db.session.add(product)
        db.session.commit()

        additional_images = request.files.getlist('additional_images')
        for image in additional_images:
            if image.filename != '':
                additional_filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], additional_filename))
                new_image = ProductImage(product_id=product.id, image_url=f"uploads/{additional_filename}")
                db.session.add(new_image)

        db.session.commit()
        
        flash('تم إضافة المنتج بنجاح', 'success')
        return redirect(url_for('admin_products'))
    
    return render_template('admin/add_product.html')

@app.route('/admin/products/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        product.name_ar = request.form.get('name_ar')
        product.name_en = request.form.get('name_en')
        product.description_ar = request.form.get('description_ar')
        product.description_en = request.form.get('description_en')
        product.price = float(request.form.get('price')) if request.form.get('price') else None
        product.youtube_url = get_youtube_video_id(request.form.get('youtube_url'))
        product.discount_percentage = float(request.form.get('discount_percentage', 0))
        product.updated_at = datetime.utcnow()

        if 'image_file' in request.files:
            file = request.files['image_file']
            if file.filename != '':
                image_filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
                product.image_url = f"uploads/{image_filename}"

        # Handle additional images
        additional_images = request.files.getlist('additional_images')
        for image in additional_images:
            if image.filename != '':
                additional_filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], additional_filename))
                new_image = ProductImage(product_id=product.id, image_url=f"uploads/{additional_filename}")
                db.session.add(new_image)

        # Handle deletion of existing additional images
        images_to_delete = request.form.getlist('delete_image_ids')
        for img_id in images_to_delete:
            image_to_delete = ProductImage.query.get(img_id)
            if image_to_delete:
                # Optionally delete file from disk
                try:
                    os.remove(os.path.join(app.root_path, 'static', image_to_delete.image_url))
                except OSError:
                    pass # File might not exist or already deleted
                db.session.delete(image_to_delete)

        db.session.commit()
        
        flash('تم تحديث المنتج بنجاح', 'success')
        return redirect(url_for('admin_products'))
    
    return render_template('admin/edit_product.html', product=product)

@app.route('/admin/products/delete/<int:product_id>', methods=['POST'])
@login_required
def admin_delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    
    flash('تم حذف المنتج بنجاح', 'success')
    return redirect(url_for('admin_products'))

@app.route('/admin/orders')
@login_required
def admin_orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=orders)

@app.route('/admin/orders/<int:order_id>')
@login_required
def admin_order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    order_items = json.loads(order.items)
    return render_template('admin/order_detail.html', order=order, order_items=order_items)

@app.route('/admin/orders/update_status/<int:order_id>', methods=['POST'])
@login_required
def admin_update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    notes = request.form.get('notes')
    
    order.status = new_status
    order.notes = notes
    
    db.session.commit()
    
    flash('تم تحديث حالة الطلب بنجاح', 'success')
    return redirect(url_for('admin_order_detail', order_id=order_id))

@app.route('/admin/admins')
@login_required
def admin_admins():
    if not current_user.is_super_admin:
        flash('ليس لديك صلاحية للوصول لهذه الصفحة', 'error')
        return redirect(url_for('admin_dashboard'))
    
    admins = Admin.query.all()
    return render_template('admin/admins.html', admins=admins)

@app.route('/admin/admins/add', methods=['GET', 'POST'])
@login_required
def admin_add_admin():
    if not current_user.is_super_admin:
        flash('ليس لديك صلاحية للوصول لهذه الصفحة', 'error')
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        is_super_admin = request.form.get('is_super_admin') == 'on'
        
        if Admin.query.filter_by(username=username).first():
            flash('اسم المستخدم موجود بالفعل', 'error')
        else:
            admin = Admin(username=username, is_super_admin=is_super_admin)
            admin.set_password(password)
            
            db.session.add(admin)
            db.session.commit()
            
            flash('تم إضافة المدير بنجاح', 'success')
            return redirect(url_for('admin_admins'))
    
    return render_template('admin/add_admin.html')

@app.route('/admin/settings/homepage_video', methods=['GET', 'POST'])
@login_required
def admin_homepage_video_settings():
    if not current_user.is_authenticated:
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        url = request.form.get('homepage_video_url', '').strip()
        show = request.form.get('show_homepage_video', '0') == '1'
        set_setting('homepage_video_url', url)
        set_setting('show_homepage_video', '1' if show else '0')
        flash('تم تحديث إعدادات الفيديو بنجاح', 'success')
        return redirect(url_for('admin_homepage_video_settings'))
    homepage_video_url = get_setting('homepage_video_url', '')
    show_homepage_video = get_setting('show_homepage_video', '1') == '1'
    return render_template('admin/homepage_video_settings.html', homepage_video_url=homepage_video_url, show_homepage_video=show_homepage_video)

# Initialize database and create default admin
def create_tables():
    with app.app_context():
        db.create_all()
        
        # Create default admin if none exists
        if not Admin.query.first():
            admin = Admin(username='admin', is_super_admin=True)
            admin.set_password('admin121121')
            db.session.add(admin)
            db.session.commit()

if __name__ == '__main__':
    create_tables()
    app.run(host='0.0.0.0', port=5000, debug=True)

