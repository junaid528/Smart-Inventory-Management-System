import os
from flask import render_template, request, redirect, url_for, flash, session

from werkzeug.security import generate_password_hash, check_password_hash
from app import create_app, db  # Import the initialized app and db from app/__init__.py
from scripts.recommendation_system import generate_product_recommendations
from app.models.product import Product
from app.models.user_behavior import UserBehavior
from werkzeug.utils import secure_filename
from app.models.user import User  # Import the User model from a separate file
from flask import Flask

app = Flask(__name__)




# Initialize the Flask app
app = create_app()

# Set the upload folder and allowed file extensions
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/upload_image/<int:product_id>', methods=['POST'])
def upload_image(product_id):
    product = Product.query.get_or_404(product_id)
    
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        
        # Save the file to the uploads folder
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        # Save the filename to the product
        product.save_image(filename)
        
        flash('Image successfully uploaded')
        return redirect(url_for('product_details', product_id=product_id))
    
    flash('Invalid file format')
    return redirect(request.url)

with app.app_context():
    db.create_all()

# Delete old database file if it exists (for development/testing purposes)
def delete_old_database():
    db_path = 'users.db'
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Deleted existing database: {db_path}")
    else:
        print("No existing database found.")

# Uncomment the line below to delete the database during initialization

# delete_old_database()

# Define routes
@app.route('/')
def home():
    products = Product.query.all()  # Fetch all products from the database
    recommended_products = []
    if 'user_id' in session:  # Generate recommendations only if the user is logged in
        recommended_products = generate_product_recommendations(user_id=session['user_id'])
    return render_template('home.html', products=products, recommendations=recommended_products)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['user_type']  # Changed from 'role' to 'user_type'
        security_code = request.form.get('security_code')  # Only for admin users

        # Find the user by email
        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):  # Use hashed password check
            flash('Invalid email or password.')
            return redirect(url_for('login'))

        # Check if user_type matches the user's type
        if user.user_type != user_type:  # Ensure the user_type matches the database
            flash('User type does not match.')
            return redirect(url_for('login'))

        # Handle role-based redirection
        if user_type == 'admin':
            if security_code != 'Admin@ivms':  # Verify admin security code
                flash('Invalid admin security code.')
                return redirect(url_for('login'))
            else:
                flash('Welcome, Admin!')
                return redirect(url_for('admin_dashboard'))  # Redirect to admin dashboard
        elif user_type == 'customer':
            flash('Welcome, Customer!')
            return redirect(url_for('customer_dashboard'))  # Redirect to customer dashboard

    return render_template('login.html')


@app.route('/admin-dashboard')
def admin_dashboard():
    # Admin-specific logic
    return render_template('admin_dashboard.html')

@app.route('/customer-dashboard')
def customer_dashboard():
    # Customer-specific logic
    return render_template('customer_dashboard.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        age = request.form['age']
        gender = request.form['gender']
        number = request.form['number']
        user_type = request.form['user_type']

        # Check if email already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('register'))

        # Hash the password before saving it
        password_hash = generate_password_hash(password, method='pbkdf2:sha256')

        # Save the user
        new_user = User(
            name=name,
            email=email,
            password_hash=password_hash,  # Save the hashed password
            age=age,
            gender=gender,
            number=number,
             user_type=user_type 
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:  # Check if user_id exists in the session
        flash('Login required!', 'danger')
        return redirect(url_for('login'))  # Redirect to login page if not logged in

    try:
        user = db.session.get(User, session['user_id'])
         # Fetch the logged-in user's information
        if user is None:
            flash('User not found!', 'danger')
            return redirect(url_for('logout'))

        # Fetch all products (or just those you want to display)
        products = Product.query.all()

        # Fetch recommended products for the logged-in user
        recommended_products = generate_product_recommendations(user_id=session['user_id'])  

        if not recommended_products:
            flash('No recommendations available at the moment.', 'info')

        return render_template(
            'dashboard.html', 
            user=user, 
            products=products, 
            recommendations=recommended_products
        )

    except Exception as e:
        print(f"Error in dashboard route: {e}")
        flash('An error occurred while loading the dashboard. Please try again later.', 'danger')
        return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove user ID from session
    flash('Logged out!', 'success')
    return redirect(url_for('login'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/manage-product')
def manage_product():
    products = Product.query.all()
    return render_template('manage.html', products=products)



 # Assuming you have a template for this
@app.route('/add-product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        price = float(request.form['price'])
        description = request.form['description']

        # Handle image file upload
        if 'image' not in request.files:
            # Handle case when no file is selected
            return redirect(request.url)
        
        image = request.files['image']
        
        # If the user does not select a file, the browser submits an empty part without a filename
        if image.filename == '':
            return redirect(request.url)
        
        if image and allowed_file(image.filename):
            # Secure the filename and save it in the uploads folder
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            # Create a product and store the image filename
            new_product = Product(name=name, category=category, price=price, description=description, image_filename=filename)
            db.session.add(new_product)
            db.session.commit()
        
            return redirect(url_for('manage_product'))

    return render_template('add_product.html')
@app.route('/recommended_product')
def recommended_product():
    try:
        user_id = session.get('user_id')
        if not user_id:
            flash("You need to log in to see recommendations.", "danger")
            return redirect(url_for('login'))

        # Fetch recommendations
        recommended_products = generate_product_recommendations(user_id)
        if not recommended_products:
            flash("No recommendations available.", "info")

        return render_template(
            'recommended_product.html',
            recommendations=recommended_products
        )

    except Exception as e:
        print(f"Error in recommended_product route: {e}")
        flash("Unable to load recommendations. Please try again later.", "danger")
        return redirect(url_for('dashboard'))

@app.route('/recommendations')
def recommendations():
    if 'user_id' in session:
        recommended_products = generate_product_recommendations(user_id=session['user_id'])
        return render_template('recommendations.html', recommendations=recommended_products)
    else:
        flash('Please log in to see recommendations!', 'danger')
        return redirect(url_for('login'))

if __name__ == "__main__":
    app.secret_key = 'super secret key'  # Replace with a secure key for production
    app.run(debug=True)
