from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os

# ---------------------------
# Configuration
# ---------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "secret123")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///campus_lost_and_found.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024  # 4MB limit

db = SQLAlchemy(app)

# ---------------------------
# Models
# ---------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False)  # 'lost' or 'found'
    owner_email = db.Column(db.String(200), nullable=False)
    image_filename = db.Column(db.String(300), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ---------------------------
# Helpers
# ---------------------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def current_user():
    user_email = session.get('user')
    if not user_email:
        return None
    return User.query.filter_by(email=user_email).first()

# ---------------------------
# Create DB and sample data (Flask 3.x compatible)
# ---------------------------
with app.app_context():
    db.create_all()
    # create a sample user + sample items if none exist (for demo)
    if not User.query.filter_by(email='demo@school.edu').first():
        demo = User(email='demo@school.edu', password_hash=generate_password_hash('password123'))
        db.session.add(demo)
        db.session.commit()
    if Item.query.count() == 0:
        demo_user = User.query.filter_by(email='demo@school.edu').first()
        sample1 = Item(title='Black Umbrella', description='Left near library stairs', status='lost', owner_email=demo_user.email)
        sample2 = Item(title='Set of Keys', description='Found in Canteen', status='found', owner_email=demo_user.email)
        db.session.add_all([sample1, sample2])
        db.session.commit()

# ---------------------------
# Routes - Authentication
# ---------------------------
@app.route('/')
def login_page():
    if current_user():
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email','').strip().lower()
    password = request.form.get('password','')
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password_hash, password):
        session['user'] = user.email
        flash("Logged in successfully.", "success")
        return redirect(url_for('dashboard'))
    else:
        flash("Invalid email or password.", "danger")
        return redirect(url_for('login_page'))

@app.route('/register')
def register_page():
    if current_user():
        return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/register_user', methods=['POST'])
def register_user():
    email = request.form.get('email','').strip().lower()
    password = request.form.get('password','')
    password2 = request.form.get('password2','')
    if not email or not password:
        flash("Email and password are required.", "danger")
        return redirect(url_for('register_page'))
    if password != password2:
        flash("Passwords do not match.", "danger")
        return redirect(url_for('register_page'))
    if User.query.filter_by(email=email).first():
        flash("Account already exists.", "danger")
        return redirect(url_for('register_page'))
    user = User(email=email, password_hash=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()
    flash("Registration successful! You can now log in.", "success")
    return redirect(url_for('login_page'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully.", "info")
    return redirect(url_for('login_page'))

# ---------------------------
# Dashboard & Items (CRUD) with Image Upload
# ---------------------------
@app.route('/dashboard')
def dashboard():
    if not current_user():
        flash("Please log in first.", "warning")
        return redirect(url_for('login_page'))
    status_filter = request.args.get('status','all')
    if status_filter in ('lost','found'):
        items = Item.query.filter_by(status=status_filter).order_by(Item.created_at.desc()).all()
    else:
        items = Item.query.order_by(Item.created_at.desc()).all()
    return render_template('dashboard.html', items=items, user=current_user(), status_filter=status_filter)

@app.route('/item/create', methods=['GET','POST'])
def create_item():
    if not current_user():
        flash("Please log in first.", "warning")
        return redirect(url_for('login_page'))
    if request.method == 'POST':
        title = request.form.get('title','').strip()
        description = request.form.get('description','').strip()
        status = request.form.get('status','lost')
        owner_email = current_user().email
        if not title:
            flash("Title is required.", "danger")
            return redirect(url_for('create_item'))
        image_file = request.files.get('image')
        filename = None
        if image_file and image_file.filename != '':
            if allowed_file(image_file.filename):
                filename = secure_filename(f"{int(datetime.utcnow().timestamp())}_{image_file.filename}")
                image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                flash("File type not allowed. Use png/jpg/jpeg/gif.", "danger")
                return redirect(url_for('create_item'))
        item = Item(title=title, description=description, status=status, owner_email=owner_email, image_filename=filename)
        db.session.add(item)
        db.session.commit()
        flash("Item created.", "success")
        return redirect(url_for('dashboard'))
    return render_template('create_item.html')

@app.route('/item/<int:item_id>')
def view_item(item_id):
    if not current_user():
        flash("Please log in first.", "warning")
        return redirect(url_for('login_page'))
    item = Item.query.get_or_404(item_id)
    return render_template('item_view.html', item=item)

@app.route('/item/<int:item_id>/edit', methods=['GET','POST'])
def edit_item(item_id):
    if not current_user():
        flash("Please log in first.", "warning")
        return redirect(url_for('login_page'))
    item = Item.query.get_or_404(item_id)
    if request.method == 'POST':
        item.title = request.form.get('title','').strip()
        item.description = request.form.get('description','').strip()
        item.status = request.form.get('status','lost')
        image_file = request.files.get('image')
        if image_file and image_file.filename != '':
            if allowed_file(image_file.filename):
                if item.image_filename:
                    try:
                        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], item.image_filename))
                    except Exception:
                        pass
                filename = secure_filename(f"{int(datetime.utcnow().timestamp())}_{image_file.filename}")
                image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                item.image_filename = filename
            else:
                flash("File type not allowed.", "danger")
                return redirect(url_for('edit_item', item_id=item.id))
        db.session.commit()
        flash("Item updated.", "success")
        return redirect(url_for('view_item', item_id=item.id))
    return render_template('edit_item.html', item=item)

@app.route('/item/<int:item_id>/delete', methods=['POST'])
def delete_item(item_id):
    if not current_user():
        flash("Please log in first.", "warning")
        return redirect(url_for('login_page'))
    item = Item.query.get_or_404(item_id)
    if item.image_filename:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], item.image_filename))
        except Exception:
                            pass
    db.session.delete(item)
    db.session.commit()
    flash("Item deleted.", "info")
    return redirect(url_for('dashboard'))

@app.route('/search')
def search():
    if not current_user():
        flash("Please log in first.", "warning")
        return redirect(url_for('login_page'))
    q = request.args.get('q','').strip()
    results = []
    if q:
        results = Item.query.filter(
            (Item.title.ilike(f"%{q}%")) | (Item.description.ilike(f"%{q}%"))
        ).order_by(Item.created_at.desc()).all()
    return render_template('search.html', query=q, results=results)

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)





