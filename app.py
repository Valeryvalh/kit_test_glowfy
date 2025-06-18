from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, send_file
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from flask_babel import Babel, gettext as _
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
import uuid
import datetime
import numpy as np
from io import BytesIO
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import base64
from functools import wraps
from flask import Flask, jsonify
from flask import Request

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=7)

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.example.com'  # Replace with your SMTP server
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your-email@example.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'your-password'  # Replace with your password
app.config['MAIL_DEFAULT_SENDER'] = 'your-email@example.com'  # Replace with your email
mail = Mail(app)

# Configure Flask-Babel
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
babel = Babel(app)

# Admin registration key
ADMIN_KEY = "spa_admin_2023"  # Change this in production!

# Mock database (in a real app, use a proper database)
users_db = {}
quiz_results_db = []

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, email, password, is_admin=False):
        self.id = id
        self.email = email
        self.password = password
        self.is_admin = is_admin

@login_manager.user_loader
def load_user(user_id):
    if user_id in users_db:
        user_data = users_db[user_id]
        return User(user_id, user_data['email'], user_data['password'], user_data.get('is_admin', False))
    return None

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash(_('You need to be an admin to view this page.'))
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Quiz questions
questions = [
    {"id": 1, "text": "Do you often deal with clients who miss appointments?", "category": "Appointment Management"},
    {"id": 2, "text": "Do you manually remind clients before their session?", "category": "Client Communication"},
    {"id": 3, "text": "Do you sometimes double-book or forget bookings?", "category": "Scheduling Efficiency"},
    {"id": 4, "text": "Do your staff members know about new bookings immediately?", "category": "Staff Coordination"},
    {"id": 5, "text": "Do you have a client referral system?", "category": "Business Growth"}
]

# TOPSIS implementation
def topsis_analysis(scores):
    # Define weights for each question (equal weights for simplicity)
    weights = np.array([0.2, 0.2, 0.2, 0.2, 0.2])
    
    # Define ideal solutions (all 1's for positive ideal, all 0's for negative ideal)
    # Note: For questions where "No" is better, we'll invert the score
    ideal_positive = np.array([0, 0, 0, 1, 1])  # Ideal answers (0=No for Q1-3, 1=Yes for Q4-5)
    ideal_negative = np.array([1, 1, 1, 0, 0])  # Worst answers
    
    # Convert user scores to match ideal format (invert where necessary)
    normalized_scores = np.array([
        1 - scores[0],  # Invert Q1 (No is better)
        1 - scores[1],  # Invert Q2 (No is better)
        1 - scores[2],  # Invert Q3 (No is better)
        scores[3],      # Keep Q4 (Yes is better)
        scores[4]       # Keep Q5 (Yes is better)
    ])
    
    # Apply weights
    weighted_scores = normalized_scores * weights
    weighted_positive = ideal_positive * weights
    weighted_negative = ideal_negative * weights
    
    # Calculate distances
    positive_distance = np.sqrt(np.sum((weighted_scores - weighted_positive) ** 2))
    negative_distance = np.sqrt(np.sum((weighted_scores - weighted_negative) ** 2))
    
    # Calculate TOPSIS score
    topsis_score = negative_distance / (positive_distance + negative_distance)
    
    return topsis_score

# Generate recommendations based on scores
def generate_recommendations(scores):
    categories = ["Appointment Management", "Client Communication", "Scheduling Efficiency", 
                 "Staff Coordination", "Business Growth"]
    
    recommendations = {}
    
    # Generate specific recommendations for each category
    if scores[0] == 1:  # Yes to Q1
        recommendations["Appointment Management"] = "Implement automated appointment reminders to reduce no-shows."
    else:
        recommendations["Appointment Management"] = "Your no-show rate is good, but automated reminders can help maintain this."
        
    if scores[1] == 1:  # Yes to Q2
        recommendations["Client Communication"] = "Automate client reminders to save staff time and ensure consistency."
    else:
        recommendations["Client Communication"] = "Continue using automated reminders and consider adding personalized messages."
        
    if scores[2] == 1:  # Yes to Q3
        recommendations["Scheduling Efficiency"] = "Implement a centralized booking system to eliminate double-bookings."
    else:
        recommendations["Scheduling Efficiency"] = "Your scheduling system is working well. Consider adding capacity analytics."
        
    if scores[3] == 0:  # No to Q4
        recommendations["Staff Coordination"] = "Implement real-time booking notifications for all staff members."
    else:
        recommendations["Staff Coordination"] = "Your staff communication is good. Consider adding staff performance metrics."
        
    if scores[4] == 0:  # No to Q5
        recommendations["Business Growth"] = "Implement an automated referral system to grow your client base."
    else:
        recommendations["Business Growth"] = "Your referral system is working. Consider adding incentives for multiple referrals."
    
    return recommendations

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/quiz')
def quiz():
    # Initialize or reset quiz session
    session['quiz_started'] = True
    session['current_question'] = 0
    return render_template('quiz.html', questions=questions)

@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    if request.method == 'POST':
        data = request.get_json()
        answers = data.get('answers', [])
        lead_data = data.get('leadData', {})
        
        # Convert answers to binary (Yes=1, No=0)
        binary_answers = [1 if ans == 'Yes' else 0 for ans in answers]
        
        # Calculate score
        score_percentage = (sum(binary_answers) / len(binary_answers)) * 100
        
        # Calculate TOPSIS score
        topsis_score = topsis_analysis(binary_answers)
        
        # Generate recommendations
        recommendations = generate_recommendations(binary_answers)
        
        # Determine result category
        if score_percentage <= 40:
            result_category = "critical"
            icon = "icon_echec.png"
            message = _("Your spa urgently needs our Management Information System (MIS).")
        elif score_percentage <= 70:
            result_category = "needs_improvement"
            icon = "icon_juste.png"
            message = _("Your spa is doing okay, but you would benefit from our MIS.")
        else:
            result_category = "good"
            icon = "icon_bien.png"
            message = _("Your spa is doing well, but our MIS can help you improve further.")
        
        # Save result
        result_id = str(uuid.uuid4())
        result = {
            'id': result_id,
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'answers': binary_answers,
            'score': score_percentage,
            'topsis_score': topsis_score,
            'category': result_category,
            'icon': icon,
            'message': message,
            'recommendations': recommendations,
            'user_id': current_user.id if current_user.is_authenticated else None,
            'lead_data': lead_data
        }
        
        quiz_results_db.append(result)
        session['last_result_id'] = result_id
        
        return jsonify({
            'success': True,
            'result_id': result_id
        })

@app.route('/results/<result_id>')
def results(result_id):
    # Find the result with the given ID
    result = next((r for r in quiz_results_db if r['id'] == result_id), None)
    
    if not result:
        flash(_('Result not found.'))
        return redirect(url_for('index'))
    
    # Calculate category scores
    categories = ["Appointment Management", "Client Communication", "Scheduling Efficiency", 
                 "Staff Coordination", "Business Growth"]
    category_scores = result['answers']
    
    # Get industry average (mock data)
    industry_avg = [0.7, 0.6, 0.8, 0.5, 0.4]
    
    return render_template(
        'results.html',
        result=result,
        categories=categories,
        category_scores=category_scores,
        industry_avg=industry_avg
    )

@app.route('/download_pdf/<result_id>')
def download_pdf(result_id):
    # Find the result with the given ID
    result = next((r for r in quiz_results_db if r['id'] == result_id), None)
    
    if not result:
        flash(_('Result not found.'))
        return redirect(url_for('index'))
    
    # Generate PDF
    buffer = BytesIO()
    with PdfPages(buffer) as pdf:
        # First page - Summary
        plt.figure(figsize=(8.5, 11))
        plt.text(0.5, 0.95, 'Spa Management Assessment Results', ha='center', fontsize=16)
        plt.text(0.5, 0.9, f"Date: {result['timestamp']}", ha='center')
        plt.text(0.5, 0.85, f"Overall Score: {result['score']}%", ha='center')
        
        if result['score'] <= 40:
            plt.text(0.5, 0.8, "Your spa urgently needs our Management Information System (MIS).", ha='center', color='red')
        elif result['score'] <= 70:
            plt.text(0.5, 0.8, "Your spa is doing okay, but you would benefit from our MIS.", ha='center', color='orange')
        else:
            plt.text(0.5, 0.8, "Your spa is doing well, but our MIS can help you improve further.", ha='center', color='green')
        
        # Add recommendations
        plt.text(0.5, 0.7, "Recommendations:", ha='center', fontsize=14)
        y_pos = 0.65
        for category, recommendation in result['recommendations'].items():
            plt.text(0.1, y_pos, f"{category}:", fontweight='bold')
            plt.text(0.1, y_pos-0.05, recommendation, wrap=True)
            y_pos -= 0.1
        
        plt.axis('off')
        pdf.savefig()
        plt.close()
        
        # Second page - Radar Chart
        categories = ["Appointment Management", "Client Communication", "Scheduling Efficiency", 
                     "Staff Coordination", "Business Growth"]
        
        # Convert binary answers to percentages (0 -> 0%, 1 -> 100%)
        values = [score * 100 for score in result['answers']]
        
        # Create radar chart
        plt.figure(figsize=(8.5, 11))
        plt.subplot(polar=True)
        
        # Plot data
        angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False).tolist()
        values += values[:1]  # Close the loop
        angles += angles[:1]  # Close the loop
        
        plt.polar(angles, values)
        plt.fill(angles, values, alpha=0.25)
        
        # Add category labels
        plt.xticks(angles[:-1], categories)
        
        plt.title('Category Performance')
        pdf.savefig()
        plt.close()
    
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"spa_assessment_{result_id}.pdf",
        mimetype='application/pdf'
    )

@app.route('/send_email', methods=['POST'])
def send_email():
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        result_id = data.get('result_id')
        
        # Find the result with the given ID
        result = next((r for r in quiz_results_db if r['id'] == result_id), None)
        
        if not result or not email:
            return jsonify({'success': False, 'message': _('Invalid data')})
        
        try:
            # Generate PDF
            buffer = BytesIO()
            # (PDF generation code similar to download_pdf route)
            
            # Create email
            msg = Message(
                subject=_("Your Spa Management Assessment Results"),
                recipients=[email],
                body=_("Please find your assessment results attached."),
                html=render_template('email_template.html', result=result)
            )
            
            # Attach PDF
            msg.attach(
                filename=f"spa_assessment_{result_id}.pdf",
                content_type="application/pdf",
                data=buffer.getvalue()
            )
            
            # Send email
            mail.send(msg)
            
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Find user by email
        user_id = None
        for uid, user_data in users_db.items():
            if user_data['email'] == email:
                user_id = uid
                break
        
        if user_id and check_password_hash(users_db[user_id]['password'], password):
            user = User(
                user_id, 
                email, 
                users_db[user_id]['password'], 
                users_db[user_id].get('is_admin', False)
            )
            login_user(user)
            
            # Redirect admin users to admin dashboard
            if user.is_admin:
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('dashboard'))
        
        flash(_('Invalid email or password.'))
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        is_admin = 'is_admin' in request.form
        admin_key = request.form.get('admin_key')
        
        # Check if email already exists
        for user_data in users_db.values():
            if user_data['email'] == email:
                flash(_('Email already registered.'))
                return render_template('register.html')
        
        # Validate admin registration
        if is_admin:
            if not admin_key or admin_key != ADMIN_KEY:
                flash(_('Invalid admin registration key.'))
                return render_template('register.html')
        
        # Create new user
        user_id = str(uuid.uuid4())
        users_db[user_id] = {
            'email': email,
            'password': generate_password_hash(password),
            'is_admin': is_admin
        }
        
        # Log in the new user
        user = User(user_id, email, users_db[user_id]['password'], is_admin)
        login_user(user)
        
        # Redirect admin users to admin dashboard
        if is_admin:
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('dashboard'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get user's quiz results
    user_results = [r for r in quiz_results_db if r['user_id'] == current_user.id]
    
    return render_template('dashboard.html', results=user_results)

@app.route('/admin')
@login_required
@admin_required
def admin():
    # Get all quiz results for admin view
    return render_template('admin.html', results=quiz_results_db)

@app.route('/set_language/<language>')
def set_language(language):
    session['language'] = language
    return redirect(request.referrer or url_for('index'))



# Create admin user if it doesn't exist
if 'admin' not in users_db:
    users_db['admin'] = {
        'email': 'admin@example.com',
        'password': generate_password_hash('admin123'),  # Change this in production!
        'is_admin': True
    }


# Vercel expects this to be called "handler"
def handler(request: Request):
    return app(request.environ, lambda status, headers: (status, headers))



if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
    