from flask import Flask, render_template, request, redirect, url_for, session
from config import Config
from models import db, User
from models import Student, Drive, Application
from flask import flash
from models import Company
from datetime import datetime



app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)


#DB and Admin
with app.app_context():
    db.create_all()

    admin = User.query.filter_by(email="admin@placement.com").first()
    if not admin:
        admin = User(
            email="admin@placement.com",
            password="admin123",
            role="admin",
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()


# Home Route
@app.route("/")
def home():
    return redirect(url_for("login"))


# Login Route
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if not user:
            error = "Account not found"

        elif not user.is_active:
            error = "Your account is blocked"

        elif user.password != password:
            error = "Incorrect password"

        else:
            # extra role-based checks
            if user.role == "student":
                student = Student.query.filter_by(user_id=user.id).first()
                if student and not student.is_active:
                    error = "Your student account is blacklisted"
                    return render_template("login.html", error=error)

            if user.role == "company":
                company = Company.query.filter_by(user_id=user.id).first()
                if company and not company.is_active:
                    error = "Your company account is blacklisted"
                    return render_template("login.html", error=error)

            session["user_id"] = user.id
            session["role"] = user.role

            if user.role == "admin":
                return redirect(url_for("admin_dashboard"))
            elif user.role == "student":
                return redirect(url_for("student_dashboard"))
            elif user.role == "company":
                return redirect(url_for("company_dashboard"))

    return render_template("login.html", error=error)





# Admin Dashboard
@app.route("/admin")
def admin_dashboard():
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    total_students = Student.query.count()
    total_companies = Company.query.count()
    total_drives = Drive.query.count()
    total_applications = Application.query.count()

    return render_template(
        "admin_dashboard.html",
        total_students=total_students,
        total_companies=total_companies,
        total_drives=total_drives,
        total_applications=total_applications
    )

@app.route("/admin/students")
def admin_students():
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    q = request.args.get("q")

    if q:
        students = Student.query.filter(
            (Student.name.ilike(f"%{q}%")) 
            (Student.id == q)
        ).all()
    else:
        students = Student.query.all()

    return render_template("admin_students.html", students=students, q=q)




# Student Dashboard
@app.route("/student")
def student_dashboard():
    if "user_id" not in session or session.get("role") != "student":
        return redirect(url_for("login"))
    return render_template("student_dashboard.html")

@app.route("/student/profile", methods=["GET", "POST"])
def student_profile():
    if session.get("role") != "student":
        return redirect(url_for("login"))

    student = Student.query.filter_by(user_id=session["user_id"]).first()

    if request.method == "POST":
        student.name = request.form.get("name")
        student.branch = request.form.get("branch")
        student.cgpa = request.form.get("cgpa")

        db.session.commit()
        return redirect(url_for("student_profile"))

    return render_template("student_profile.html", student=student)


@app.route("/student/drives")
def student_drives():
    if "user_id" not in session or session.get("role") != "student":
        return redirect(url_for("login"))

    drives = Drive.query.filter_by(approved=True).all()
    return render_template("student_drives.html", drives=drives)

@app.route("/student/applications")
def student_applications():
    if "user_id" not in session or session.get("role") != "student":
        return redirect(url_for("login"))

    student = Student.query.filter_by(user_id=session["user_id"]).first()
    applications = Application.query.filter_by(student_id=student.id).all()

    return render_template(
        "student_applications.html",
        applications=applications
    )

@app.route("/register/student", methods=["GET", "POST"])
def student_register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        name = request.form.get("name")
        branch = request.form.get("branch")
        cgpa = request.form.get("cgpa")

        existing = User.query.filter_by(email=email).first()
        if existing:
            return "Student already registered"

        user = User(email=email, password=password, role="student", is_active=True)
        db.session.add(user)
        db.session.commit()

        student = Student(
            user_id=user.id,
            name=name,
            branch=branch,
            cgpa=cgpa
        )
        db.session.add(student)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("student_register.html")

@app.route("/admin/student/toggle/<int:student_id>")
def toggle_student(student_id):
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    student = Student.query.get(student_id)
    student.is_active = not student.is_active
    db.session.commit()

    return redirect(url_for("admin_students"))




@app.route("/admin/company/toggle/<int:company_id>")
def toggle_company(company_id):
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    company = Company.query.get(company_id)
    company.is_active = not company.is_active
    db.session.commit()

    return redirect(url_for("admin_companies"))



# Company Dashboard
@app.route("/company")
def company_dashboard():
    if "user_id" not in session or session.get("role") != "company":
        return redirect(url_for("login"))
    return render_template("company_dashboard.html")

@app.route("/register/company", methods=["GET", "POST"])
def company_register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        company_name = request.form.get("company_name")

        if User.query.filter_by(email=email).first():
            return "Company already exists"

        user = User(
            email=email,
            password=password,
            role="company",
            is_active=True
        )
        db.session.add(user)
        db.session.commit()

        company = Company(
            user_id=user.id,
            company_name=company_name,
            approved=False   # IMPORTANT
        )
        db.session.add(company)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("company_register.html")




@app.route("/student/apply/<int:drive_id>")
def apply_drive(drive_id):
    if "user_id" not in session or session.get("role") != "student":
        return redirect(url_for("login"))

    student = Student.query.filter_by(user_id=session["user_id"]).first()

    already = Application.query.filter_by(
        student_id=student.id,
        drive_id=drive_id
    ).first()

    if already:
        return "You have already applied for this drive"

    application = Application(
        student_id=student.id,
        drive_id=drive_id,
        status="Applied"
    )
    db.session.add(application)
    db.session.commit()

    return redirect(url_for("student_applications"))


@app.route("/admin/companies")
def admin_companies():
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    q = request.args.get("q")

    if q:
        companies = Company.query.filter(
            (Company.company_name.ilike(f"%{q}%")) |
            (Company.id == q)
        ).all()
    else:
        companies = Company.query.all()

    return render_template(
        "admin_companies.html",
        companies=companies,
        q=q
    )



@app.route("/admin/company/approve/<int:company_id>")
def approve_company(company_id):
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    company = Company.query.get(company_id)
    company.approved = True
    db.session.commit()

    return redirect(url_for("admin_companies"))


@app.route("/company/drives", methods=["GET", "POST"])
def company_drives():
    if session.get("role") != "company":
        return redirect(url_for("login"))

    company = Company.query.filter_by(user_id=session["user_id"]).first()

    if not company.approved:
        return "Your company is not approved yet"
    
    if not company.is_active:
        return redirect(url_for("logout"))


    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")

        # ✅ DEFINE deadline_str FIRST
        deadline_str = request.form.get("deadline")

        # ✅ THEN convert it
        deadline = datetime.strptime(deadline_str, "%Y-%m-%d").date()

        drive = Drive(
            company_id=company.id,
            title=title,
            description=description,
            deadline=deadline,
            approved=False
        )

        db.session.add(drive)
        db.session.commit()

    drives = Drive.query.filter_by(company_id=company.id).all()
    return render_template("company_drives.html", drives=drives)

@app.route("/company/applications")
def company_applications():
    if session.get("role") != "company":
        return redirect(url_for("login"))

    company = Company.query.filter_by(user_id=session["user_id"]).first()
    q = request.args.get("q")

    query = (
        db.session.query(Application, Student, Drive)
        .join(Drive, Application.drive_id == Drive.id)
        .join(Student, Application.student_id == Student.id)
        .filter(Drive.company_id == company.id)
    )

    if q:
        query = query.filter(
            (Student.name.ilike(f"%{q}%")) |
            (Student.id == q)
        )

    applications = query.all()

    return render_template(
        "company_applications.html",
        applications=applications,
        q=q
    )


@app.route("/company/application/update/<int:app_id>/<status>")
def update_application_status(app_id, status):
    if session.get("role") != "company":
        return redirect(url_for("login"))

    application = Application.query.get(app_id)

    if application:
        application.status = status
        db.session.commit()

    return redirect(url_for("company_applications"))

@app.route("/admin/company/deactivate/<int:company_id>")
def deactivate_company(company_id):
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    company = Company.query.get(company_id)

    if company:
        company.is_active = False
        db.session.commit()

    return redirect(url_for("admin_companies"))



@app.route("/admin/drives")
def admin_drives():
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    drives = Drive.query.all()
    return render_template("admin_drives.html", drives=drives)

@app.route("/admin/drive/approve/<int:drive_id>")
def approve_drive(drive_id):
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    drive = Drive.query.get(drive_id)
    drive.approved = True
    db.session.commit()

    return redirect(url_for("admin_drives"))


# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
