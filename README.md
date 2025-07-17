<<<<<<< HEAD
# Made by Najeeb Alsheikh

# متجر الأردن الإلكتروني - Jordan E-commerce Store

A complete e-commerce website built with Flask for selling products in Jordan, featuring Arabic RTL support, admin panel, and WhatsApp integration.

## 🌟 Features

### Customer Features
- **Arabic RTL Design**: Full Arabic language support with right-to-left layout
- **Product Catalog**: Browse products with images, descriptions, and pricing
- **Shopping Cart**: Add products to cart and manage quantities
- **Checkout System**: Complete order placement with customer information
- **WhatsApp Integration**: Direct contact with store via WhatsApp
- **Responsive Design**: Mobile-friendly interface for all devices
- **Cash on Delivery**: Payment upon delivery option

### Admin Features
- **Admin Dashboard**: Comprehensive statistics and overview
- **Product Management**: Add, edit, delete products with images and YouTube videos
- **Order Management**: View, update, and track customer orders
- **Admin Management**: Super admin can manage other administrators
- **Real-time Updates**: Live order notifications and status updates
- **Arabic Interface**: Fully localized admin panel in Arabic

## 🛠 Technology Stack

- **Backend**: Flask 2.3.3 (Python web framework)
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **Authentication**: Flask-Login with session management
- **Forms**: Flask-WTF with CSRF protection
- **Styling**: Custom Arabic RTL CSS with Bootstrap
- **Deployment**: Gunicorn WSGI server for production

## 📋 Prerequisites

Before running this project, ensure you have:

- Python 3.8 or higher
- pip (Python package installer)
- Git (for version control)
- A modern web browser

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/jordan-ecommerce.git
cd jordan-ecommerce
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python app.py
```

### 4. Access the Website
- **Main Website**: http://localhost:5000
- **Admin Panel**: http://localhost:5000/admin/login
- **Default Admin**: Username: `admin`, Password: `admin123`

## 📁 Project Structure

```
ecommerce_app/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── Procfile              # Railway deployment configuration
├── .env                  # Environment variables
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Homepage
│   ├── product_detail.html
│   ├── cart.html
│   ├── checkout.html
│   ├── order_success.html
│   └── admin/            # Admin templates
│       ├── base.html
│       ├── login.html
│       ├── dashboard.html
│       ├── products.html
│       ├── add_product.html
│       ├── edit_product.html
│       ├── orders.html
│       ├── order_detail.html
│       ├── admins.html
│       └── add_admin.html
├── static/               # Static files (CSS, JS, images)
└── ecommerce.db         # SQLite database (auto-created)
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-change-this-in-production
DATABASE_URL=sqlite:///ecommerce.db
FLASK_ENV=development
FLASK_DEBUG=True
```

### Database Configuration

The application automatically creates the database and tables on first run. For production, update the `DATABASE_URL` to use PostgreSQL:

```env
DATABASE_URL=postgresql://username:password@host:port/database
```

## 👤 Default Admin Account

The application creates a default admin account on first run:
- **Username**: admin
- **Password**: admin123
- **Type**: Super Admin

**⚠️ Important**: Change the default password immediately after deployment!

## 🎨 Customization

### Adding Products
1. Login to admin panel
2. Navigate to "المنتجات" (Products)
3. Click "إضافة منتج جديد" (Add New Product)
4. Fill in product details:
   - Product name (Arabic/English)
   - Description (Arabic/English)
   - Price in Jordanian Dinars
   - Discount percentage
   - Product image URL
   - YouTube video URL (optional)

### Managing Orders
1. Access "الطلبات" (Orders) from admin panel
2. View order details and customer information
3. Update order status (Pending/Completed/Deleted)
4. Contact customers via WhatsApp or phone

### Adding Administrators
1. Super admins can access "المديرين" (Admins)
2. Click "إضافة مدير جديد" (Add New Admin)
3. Set username, password, and admin type
4. Regular admins can manage products and orders
5. Super admins have full system access

## 📱 Mobile Responsiveness

The website is fully responsive and optimized for:
- Desktop computers (1200px+)
- Tablets (768px - 1199px)
- Mobile phones (320px - 767px)

All features work seamlessly across devices with touch-friendly interfaces.

## 🌐 Arabic Language Support

The application provides comprehensive Arabic language support:
- Right-to-left (RTL) text direction
- Arabic fonts and typography
- Localized date and number formats
- Arabic navigation and interface elements
- Bilingual product support (Arabic/English)

## 🔒 Security Features

- CSRF protection on all forms
- Password hashing with Werkzeug
- Session-based authentication
- SQL injection prevention with SQLAlchemy
- XSS protection with template escaping
- Secure admin access controls

## 📊 Admin Dashboard Features

The admin dashboard provides:
- Real-time statistics (products, orders, revenue)
- Recent orders overview
- Quick action buttons
- Order status management
- Customer contact integration
- Product inventory tracking

## 🛒 Shopping Cart Features

- Session-based cart storage
- Add/remove products
- Quantity management
- Price calculations with discounts
- Persistent cart across page visits
- Clear cart functionality

## 📞 WhatsApp Integration

Direct WhatsApp integration allows:
- Customer support contact
- Order inquiries
- Product questions
- Automated message templates
- Click-to-chat functionality

## 🎯 SEO Optimization

The website includes:
- Meta tags for all pages
- Arabic language declarations
- Semantic HTML structure
- Clean URL patterns
- Mobile-friendly design
- Fast loading times

## 🔄 Order Management Workflow

1. **Customer Places Order**: Through checkout form
2. **Order Created**: Stored in database with "Pending" status
3. **Admin Notification**: New order appears in admin panel
4. **Order Processing**: Admin reviews and contacts customer
5. **Status Update**: Mark as "Completed" or "Deleted"
6. **Customer Contact**: WhatsApp/phone integration for updates

## 📈 Performance Optimization

- Optimized database queries
- Efficient template rendering
- Compressed static assets
- Minimal JavaScript dependencies
- Fast server response times
- Scalable architecture

## 🐛 Troubleshooting

### Common Issues

**Database Connection Error**
```bash
# Ensure database URL is correct in .env file
DATABASE_URL=sqlite:///ecommerce.db
```

**Admin Login Issues**
```bash
# Reset admin password by running:
python -c "from app import *; admin = Admin.query.filter_by(username='admin').first(); admin.set_password('newpassword'); db.session.commit()"
```

**Port Already in Use**
```bash
# Change port in app.py or kill existing process:
lsof -ti:5000 | xargs kill -9
```

**Missing Dependencies**
```bash
# Reinstall requirements:
pip install -r requirements.txt --force-reinstall
```

## 📝 License

This project is licensed under the MIT License. See LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Contact via WhatsApp integration
- Email: support@jordanstore.com

## 🔄 Version History

- **v1.0.0**: Initial release with core e-commerce functionality
- Arabic RTL support
- Admin panel
- WhatsApp integration
- Mobile responsiveness

---

**Built with ❤️ for Jordan's e-commerce community**

=======
# Website_1
>>>>>>> 29bc84376eab4365f1c4e8f778ad336a5ede6460
