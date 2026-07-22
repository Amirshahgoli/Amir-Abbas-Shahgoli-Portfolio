from app import app, db, Skill, Course, Profile, User

with app.app_context():
    # ۱. پاک کردن دیتابیس قبلی و ساخت مجدد تمام جداول (شامل جدول user)
    db.drop_all()
    db.create_all()

    # ۲. ساخت کاربر ادمین
    admin_user = User(username='admin')
    admin_user.set_password('admin123')  # رمز عبور دلخواهت رو اینجا بنویس
    db.session.add(admin_user)

    # ۳. افزودن اطلاعات شخصی اولیه
    my_profile = Profile(
        full_name="فرناز احمدی",
        title="Industrial Engineer",
        bio="دانشجوی مهندسی صنایع با علاقه به بهینه‌سازی و طراحی سیستم‌های هوشمند.",
        email="f.ahmadi@example.com",
        github="github.com/farnaz",
        linkedin="linkedin.com/in/farnaz"
    )
    db.session.add(my_profile)

    # ۴. افزودن نمونه مهارت‌ها
    skills = [
        Skill(title="تحقیق در عملیات", percent=90, category="technical"),
        Skill(title="Python", percent=85, category="tool"),
        Skill(title="حل مسئله", percent=95, category="soft")
    ]
    db.session.add_all(skills)

    # ۵. افزودن نمونه نمره‌ها
    courses = [
        Course(title="تحقیق در عملیات ۱", grade=19.5, unit=3, term="ترم ۳"),
        Course(title="آمار مهندسی", grade=18.2, unit=3, term="ترم ۳")
    ]
    db.session.add_all(courses)

    # ذخیره در دیتابیس
    db.session.commit()
    print("دیتابیس از نو بازسازی شد و جدول User به همراه اکانت admin اضافه گردید!")