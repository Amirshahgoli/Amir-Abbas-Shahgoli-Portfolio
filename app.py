from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# کلید امنیتی برای مدیریت نشست‌ها (Session) - در محیط واقعی رمز پیچیده‌تری بگذارید
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'

# تنظیمات دیتابیس SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# تنظیمات سیستم مدیریت ورود (Flask-Login)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# ---------------------------------------------------------
# تعریف مدل‌های دیتابیس (Tables)
# ---------------------------------------------------------

# ۱. جدول ادمین برای ورود به سیستم
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# ۲. جدول اطلاعات شخصی و بیوگرافی
class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100))
    title = db.Column(db.String(100))
    bio = db.Column(db.Text)
    email = db.Column(db.String(100))
    github = db.Column(db.String(100))
    linkedin = db.Column(db.String(100))


# ۳. جدول مهارت‌ها
class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    percent = db.Column(db.Integer, nullable=True)
    category = db.Column(db.String(50), nullable=False)  # technical, tool, soft


# ۴. جدول دروس و نمرات
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    grade = db.Column(db.Float, nullable=False)
    unit = db.Column(db.Integer, nullable=False)
    term = db.Column(db.String(50), nullable=True)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ---------------------------------------------------------
# مسیرهای اصلی (Public Routes)
# ---------------------------------------------------------

@app.route('/')
def home():
    profile = Profile.query.first()
    tech_skills = Skill.query.filter_by(category='technical').all()
    tool_skills = Skill.query.filter_by(category='tool').all()
    soft_skills = Skill.query.filter_by(category='soft').all()
    courses = Course.query.all()

    return render_template(
        'index.html',
        profile=profile,
        tech_skills=tech_skills,
        tool_skills=tool_skills,
        soft_skills=soft_skills,
        courses=courses
    )


# ---------------------------------------------------------
# مسیرهای احراز هویت (Authentication Routes)
# ---------------------------------------------------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('admin'))
        else:
            flash('نام کاربری یا رمز عبور نادرست است!')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# ---------------------------------------------------------
# مسیرهای پنل مدیریت - حفاظت شده با @login_required
# ---------------------------------------------------------

@app.route('/admin')
@login_required
def admin():
    profile = Profile.query.first()
    skills = Skill.query.all()
    courses = Course.query.all()
    return render_template('admin.html', profile=profile, skills=skills, courses=courses)


# بروزرسانی پروفایل
@app.route('/admin/profile', methods=['POST'])
@login_required
def update_profile():
    profile = Profile.query.first()
    if not profile:
        profile = Profile()
        db.session.add(profile)

    profile.full_name = request.form.get('full_name')
    profile.title = request.form.get('title')
    profile.bio = request.form.get('bio')
    profile.email = request.form.get('email')
    profile.github = request.form.get('github')
    profile.linkedin = request.form.get('linkedin')

    db.session.commit()
    return redirect(url_for('admin'))


# مدیریت مهارت‌ها
@app.route('/admin/skill/add', methods=['POST'])
@login_required
def add_skill():
    title = request.form.get('title')
    percent = request.form.get('percent')
    category = request.form.get('category')

    new_skill = Skill(title=title, percent=int(percent) if percent else 0, category=category)
    db.session.add(new_skill)
    db.session.commit()
    return redirect(url_for('admin'))


@app.route('/admin/skill/delete/<int:id>')
@login_required
def delete_skill(id):
    skill = Skill.query.get_or_404(id)
    db.session.delete(skill)
    db.session.commit()
    return redirect(url_for('admin'))


# مدیریت نمرات و دروس
@app.route('/admin/course/add', methods=['POST'])
@login_required
def add_course():
    title = request.form.get('title')
    grade = request.form.get('grade')
    unit = request.form.get('unit')
    term = request.form.get('term')

    new_course = Course(title=title, grade=float(grade), unit=int(unit), term=term)
    db.session.add(new_course)
    db.session.commit()
    return redirect(url_for('admin'))


@app.route('/admin/course/delete/<int:id>')
@login_required
def delete_course(id):
    course = Course.query.get_or_404(id)
    db.session.delete(course)
    db.session.commit()
    return redirect(url_for('admin'))


if __name__ == '__main__':
    app.run(debug=True)