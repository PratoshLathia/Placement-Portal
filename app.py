import os
from flask import Flask, render_template, redirect, request, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime

UPLOAD_FOLDER = "static/uploads"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///placement.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "secret"

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student_profile = db.relationship("StudentProfile", back_populates="user", uselist=False)

    company_profile = db.relationship("CompanyProfile", back_populates="user", uselist=False)
    

class StudentProfile(db.Model):
    __tablename__ = "student_profiles"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)

    department = db.Column(db.String(100))
    cgpa = db.Column(db.Float)
    skills = db.Column(db.String(200))
    resume = db.Column(db.String(200))

    user = db.relationship("User", back_populates="student_profile")

    applications = db.relationship("Application", back_populates="student")


class CompanyProfile(db.Model):
    __tablename__ = "company_profiles"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)

    company_name = db.Column(db.String(150))
    industry = db.Column(db.String(100))
    website = db.Column(db.String(150))
    location = db.Column(db.String(100))

    user = db.relationship("User", back_populates="company_profile")
    
    jobs = db.relationship("Job", back_populates="company")


class Job(db.Model):
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)

    company_id = db.Column(db.Integer, db.ForeignKey("company_profiles.id"), nullable=False)

    title = db.Column(db.String(150))
    description = db.Column(db.Text)
    skills = db.Column(db.String(200))
    experience = db.Column(db.String(50))
    salary = db.Column(db.String(50))
    is_approved = db.Column(db.Boolean, default=False)
    is_closed = db.Column(db.Boolean, default=False)
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    company = db.relationship("CompanyProfile", back_populates="jobs")
    
    applications = db.relationship("Application", back_populates="job")

class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)

    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
  
    student_id = db.Column(db.Integer, db.ForeignKey("student_profiles.id"), nullable=False)

    status = db.Column(db.String(50), default="Applied")
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
   
    job = db.relationship("Job", back_populates="applications")

    student = db.relationship("StudentProfile", back_populates="applications")





@app.route('/')
def index():
    return render_template('index.html')


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        if role == "admin":
            return "Admin cannot be registered"

        if User.query.filter_by(email=email).first():
            return "Email already registered"

        user = User(name=name, email=email, password=password, role=role, is_approved=False if role == "company" else True)
        db.session.add(user)
        db.session.commit()

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if not user:
            return "No user found"
        
        if user.password != password:
            print(user.password, password)
            return "Wrong password"
        
        if not user.is_active:
            return "You are blacklisted"
        
        session['user_id'] = user.id
        session['role'] = user.role
        
        if user.role == "admin":
            return redirect('admin_dashboard')
            
        elif user.role == "student":
            return redirect('student_dashboard')

        if user.role == "company":
            if not user.is_approved:
                return "You are not approved"
            else:
                return redirect('company_dashboard')
             
    return render_template("login.html")


@app.route('/logout')
def logout():

    session.clear()
    
    return redirect('login')


@app.route("/company_dashboard")
def company_dashboard():

    if not session.get('user_id'):
        return redirect('login')

    user_id = session['user_id']
    company = CompanyProfile.query.filter_by(user_id=user_id).first()

    if company:

        jobs = Job.query.filter_by(company_id=company.id).all()
        job_data = []
        all_shortlisted = []
        all_selected = []

        for job in jobs:
            total_apps = Application.query.filter_by(job_id=job.id).count()
            shortlisted = Application.query.filter_by(job_id=job.id, status="Shortlisted").all()
            all_shortlisted.extend(shortlisted)
            selected = Application.query.filter_by(job_id=job.id, status="Selected").all()
            all_selected.extend(selected)
            job_data.append({"job": job, "total_apps": total_apps})

        return render_template("company_dashboard.html", company=company, jobs=job_data, shortlisted=all_shortlisted, selected=all_selected)
    
    else:
        return render_template("company_dashboard.html")
    
    


@app.route("/company_profile", methods=["GET", "POST"])
def company_profile():

    if not session.get('user_id'):
        return redirect('login')

    # user_id = session['user_id']
    # company = CompanyProfile.query.filter_by(user_id=user_id).first()

    if request.method == "POST":

        user_id = session['user_id']
        company = CompanyProfile.query.filter_by(user_id=user_id).first()

        if company:
            print('Updating Company Profile')
            company.company_name = request.form["company_name"]
            company.industry = request.form["industry"]
            company.website = request.form["website"]
            company.location = request.form["location"]
            db.session.commit()
            return redirect("/company_dashboard")
        
        else:
            print('Inserting Company Profile')
            company = CompanyProfile(user_id=user_id, company_name=request.form["company_name"], industry=request.form["industry"], website=request.form["website"], location=request.form["location"])   
            db.session.add(company)
            db.session.commit()
            return redirect("/company_dashboard")
        
    return render_template("company_profile.html")


@app.route('/post-job',methods=['GET','POST'])
def job_post():

    if not session.get('user_id'):
            return redirect("/login")
    
    # user_id = session['user_id']
    # company = CompanyProfile.query.filter_by(user_id=user_id).first()

    if request.method == 'POST':

        user_id = session['user_id']
        company = CompanyProfile.query.filter_by(user_id=user_id).first()

        if company:
            job = Job(company_id=company.id, title=request.form["title"],  description=request.form["description"], skills=request.form["skills"], experience=request.form["experience"], salary=request.form["salary"])
            db.session.add(job)
            db.session.commit()
            return redirect("/company_dashboard")
        
        else:
            return "Please complete company profile first"

    return render_template('post_job.html')


@app.route("/company/student/<int:student_id>")
def view_student_detail(student_id):

    if "user_id" not in session:
        return redirect("/login")

    if session.get("role") != "company":
        return "Unauthorized", 403

    user_id = session["user_id"]
    company = CompanyProfile.query.filter_by(user_id=user_id).first()

    if not company:
        return "Company profile not found", 404

    student = StudentProfile.query.filter_by(id=student_id).first()

    if not student:
        return "Student not found", 404

    applications = []

    for app in student.applications:
        if app.job.company_id == company.id:
            applications.append(app)

    total_applied = len(applications)

    return render_template("student_detail.html", student=student, applications=applications, total_applied=total_applied)


@app.route("/delete-job/<int:job_id>", methods=["POST"])
def delete_job(job_id):

    if "user_id" not in session:
        return redirect("/login")

    if session.get("role") != "company":
        return "Unauthorized", 403

    user_id = session["user_id"]

    company = CompanyProfile.query.filter_by(user_id=user_id).first()

    if not company:
        return "Company profile not found", 404

    job = Job.query.filter_by(id=job_id, company_id=company.id).first()

    if not job:
        return "Job not found", 404

    application_count = Application.query.filter_by(job_id=job.id).count()

    if application_count > 0:
        return render_template("delete_warning.html", job=job, application_count=application_count)

    db.session.delete(job)
    db.session.commit()

    return redirect("/company_dashboard")


@app.route("/confirm-delete/<int:job_id>", methods=["POST"])
def confirm_delete(job_id):

    if "user_id" not in session:
        return redirect("/login")

    if session.get("role") != "company":
        return "Unauthorized", 403

    user_id = session["user_id"]

    company = CompanyProfile.query.filter_by(user_id=user_id).first()

    if not company:
        return "Company not found", 404

    job = Job.query.filter_by(id=job_id, company_id=company.id).first()

    if not job:
        return "Job not found", 404

    Application.query.filter_by(job_id=job.id).delete()
    db.session.delete(job)
    db.session.commit()

    return redirect("/company_dashboard")


@app.route("/toggle-job/<int:job_id>")
def toggle_job(job_id):

    if "user_id" not in session:
        return redirect("/login")

    if session.get("role") != "company":
        return "Unauthorized", 403

    company = CompanyProfile.query.filter_by(user_id=session["user_id"]).first()

    if not company:
        return "Company not found"

    job = Job.query.filter_by(id=job_id, company_id=company.id).first()

    if not job:
        return "Job not found"

    if job.is_closed:
        job.is_closed = False
    else:
        job.is_closed = True

    db.session.commit()

    return redirect("/company_dashboard")


@app.route("/edit-job/<int:job_id>", methods=["GET", "POST"])
def edit_job(job_id):

    if "user_id" not in session:
        return redirect("/login")

    if session.get("role") != "company":
        return "Unauthorized", 403

    company = CompanyProfile.query.filter_by(user_id=session["user_id"]).first()

    if not company:
        return "Company profile not found"

    job = Job.query.filter_by(id=job_id, company_id=company.id).first()

    if not job:
        return "Job not found"

    if request.method == "POST":

        job.title = request.form["title"]
        job.description = request.form["description"]
        job.skills = request.form["skills"]
        job.experience = request.form["experience"]
        job.salary = request.form["salary"]
        
        job.is_approved = False

        db.session.commit()

        return redirect("/company_dashboard")

    return render_template("edit_job.html", job=job)


@app.route("/company_details/<int:company_id>")
def company_details(company_id):

    company = CompanyProfile.query.filter_by(id=company_id).first()

    if not company:
        return "Company not found", 404

    return render_template("company_details.html", company=company)


@app.route("/student_dashboard")
def student_dashboard():

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]
    student = StudentProfile.query.filter_by(user_id=user_id).first()
    
    search = request.args.get("search")
    jobs_query = Job.query.filter_by(is_approved=True, is_closed=False)

    if search:
        jobs_query = jobs_query.join(CompanyProfile).filter(
            (CompanyProfile.company_name.ilike(f"%{search}%")) |
            (Job.title.ilike(f"%{search}%")) |
            (Job.skills.ilike(f"%{search}%"))
        )

    jobs = jobs_query.all()

    applied_job_ids = []
    status = {}

    if student:
        for app in student.applications:
            applied_job_ids.append(app.job_id)
            status[app.job_id] = app.status

    return render_template("student_dashboard.html", student=student, jobs=jobs, applied_job_ids=applied_job_ids, status=status)
    

@app.route("/student_profile", methods=["GET", "POST"])
def student_profile():

    if "user_id" not in session:
        return redirect("/login")

    # user_id = session["user_id"]
    # student = StudentProfile.query.filter_by(user_id=user_id).first()

    if request.method == "POST":

        user_id = session['user_id']
        student = StudentProfile.query.filter_by(user_id=user_id).first()

        file = request.files.get("resume")

        if file and file.filename != "":
            filename = secure_filename(file.filename)

            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)

        if student:
            print('Updating Student Profile')
            student.department = request.form["department"]
            student.cgpa = request.form["cgpa"]
            student.skills = request.form["skills"]
            student.resume = filename
            db.session.commit()
            return redirect("/student_dashboard")
    
        else:
            print('Inserting Student Profile')
            student = StudentProfile(user_id=user_id, department=request.form["department"], cgpa=request.form["cgpa"], skills=request.form["skills"], resume=filename)
            db.session.add(student)
            db.session.commit()
            return redirect("/student_dashboard")
        
    return render_template("student_profile.html")


@app.route("/apply-job/<int:job_id>")
def apply_job(job_id):

    if "user_id" not in session:
        return redirect("/login")

    student = StudentProfile.query.filter_by(user_id=session["user_id"]).first()

    if not student:
        return "Please complete student profile first"

    existing = Application.query.filter_by(job_id=job_id, student_id=student.id).first()

    if existing:
        return "Already applied!"

    app = Application(job_id=job_id, student_id=student.id)
    db.session.add(app)
    db.session.commit()

    return redirect("/student_dashboard")


@app.route("/job-applications/<int:job_id>")
def view_applications(job_id):

    applications = Application.query.filter_by(job_id=job_id).all()

    return render_template("applications.html", applications=applications)


@app.route("/my_applications/<int:student_id>")
def my_applications(student_id):

    applications = Application.query.filter_by(student_id=student_id).all()

    return render_template("my_applications.html", applications=applications)


@app.route("/toggle-status/<int:app_id>/<string:action>")
def toggle_status(app_id, action):

    if "user_id" not in session:
        return redirect("/login")

    application = Application.query.filter_by(id=app_id).first()
    
    if not application:
        return("Application not found")
    
    else:
        if action == "shortlist":
            if application.status == "Shortlisted":
                application.status = "Applied"
            else:
                application.status = "Shortlisted"

        elif action == "select":
            if application.status == "Selected":
                application.status = "Shortlisted"
            else:
                application.status = "Selected"

        elif action == "reject":
            if application.status == "Rejected":
                application.status = "Applied"
            else:
                application.status = "Rejected"

        db.session.commit()
            
        return redirect(request.referrer)
    

@app.route("/admin_dashboard")
def admin_dashboard():

    if "user_id" not in session or session.get("role") != "admin":
        return redirect("/login")
    
    student_search = request.args.get("student_search")
    company_search = request.args.get("company_search")

    total_students = User.query.filter_by(role="student").count()
    total_companies = User.query.filter_by(role="company").count()
    total_jobs = Job.query.count()
    total_applications = Application.query.count()

    pending_companies = User.query.filter_by(role="company", is_approved=False).all()
    pending_jobs = Job.query.filter_by(is_approved=False).all()

    all_students = User.query.filter_by(role="student").all()
    all_companies = User.query.filter_by(role="company").all()

    students_query = User.query.filter_by(role="student")

    if student_search:
        students_query = students_query.filter(
            (User.name.ilike(f"%{student_search}%")) |
            (User.email.ilike(f"%{student_search}%"))
        )

    all_students = students_query.all()

    companies_query = User.query.filter_by(role="company")

    if company_search:
        companies_query = companies_query.filter(
            (User.name.ilike(f"%{company_search}%")) |
            (User.email.ilike(f"%{company_search}%"))
        )

    all_companies = companies_query.all()

    all_jobs = Job.query.order_by(Job.posted_at.desc()).all()

    return render_template(
        "admin_dashboard.html",
        total_students=total_students,
        total_companies=total_companies,
        total_jobs=total_jobs,
        total_applications=total_applications,
        pending_companies=pending_companies,
        pending_jobs=pending_jobs,
        all_students=all_students,
        all_companies=all_companies,
        all_jobs=all_jobs
    )


@app.route("/admin/user/<int:user_id>/toggle")
def toggle_user(user_id):

    user = User.query.get_or_404(user_id)

    user.is_active = not user.is_active

    db.session.commit()

    return redirect(request.referrer)


# @app.route("/admin/companies")
# def view_companies():

#     search = request.args.get("search")

#     query = CompanyProfile.query

#     if search:
#         query = query.filter(
#             (CompanyProfile.company_name.ilike(f"%{search}%")) |
#             (CompanyProfile.industry.ilike(f"%{search}%"))
#         )

#     companies = query.all()

#     return render_template("admin_companies.html", companies=companies)


@app.route("/admin/company/<int:user_id>")
def admin_view_company(user_id):

    if "user_id" not in session or session.get("role") != "admin":
        return redirect("/login")

    user = User.query.get_or_404(user_id)
    company_profile = CompanyProfile.query.filter_by(user_id=user.id).first()

    jobs = []

    if company_profile:
        jobs = Job.query.filter_by(company_id=company_profile.id).all()

    return render_template("admin_company_detail.html", user=user, company_profile=company_profile, jobs=jobs)


@app.route("/admin/job/<int:job_id>/applications")
def admin_job_applications(job_id):

    if "user_id" not in session or session.get("role") != "admin":
        return redirect("/login")

    job = Job.query.get_or_404(job_id)

    applications = Application.query.filter_by(job_id=job.id).all()

    return render_template("admin_job_applications.html", job=job, applications=applications)


@app.route("/admin/company/<int:user_id>/blacklist")
def blacklist_company(user_id):

    user = User.query.get_or_404(user_id)
    user.is_active = False
    db.session.commit()

    return redirect("/admin_dashboard")


@app.route("/admin/company/<int:user_id>/unblacklist")
def unblacklist_company(user_id):

    user = User.query.get_or_404(user_id)
    user.is_active = True
    db.session.commit()

    return redirect("/admin_dashboard")


@app.route("/admin/company/<int:user_id>/approve")
def approve_company(user_id):

    user = User.query.get_or_404(user_id)
    user.is_approved = True
    db.session.commit()

    return redirect("/admin_dashboard")


@app.route("/admin/company/<int:user_id>/reject")
def reject_company(user_id):

    user = User.query.get_or_404(user_id)
    user.is_approved = False
    db.session.commit()

    return redirect("/admin_dashboard")


@app.route("/admin/job/<int:job_id>/approve")
def approve_job(job_id):

    job = Job.query.get_or_404(job_id)
    job.is_approved = True
    db.session.commit()

    return redirect("/admin_dashboard")


@app.route("/admin/job/<int:job_id>/reject")
def reject_job(job_id):

    job = Job.query.get_or_404(job_id)
    job.is_approved = True
    db.session.commit()

    return redirect("/admin_dashboard")


# @app.route("/admin/students")
# def view_students():

#     search = request.args.get("search")

#     query = User.query.filter_by(role="student")

#     if search:
#         query = query.filter(
#             (User.name.ilike(f"%{search}%")) |
#             (User.email.ilike(f"%{search}%"))
#         )

#     students = query.all()

#     return render_template("admin_students.html", students=students)


@app.route("/admin/student/<int:user_id>")
def admin_view_student(user_id):

    if "user_id" not in session:
        return redirect("/login")

    if session.get("role") != "admin":
        return "Unauthorized", 403

    user = User.query.get_or_404(user_id)

    student= StudentProfile.query.filter_by(user_id=user.id).first()

    applications = []

    if student_profile:
        applications = Application.query.filter_by(student_id=student.id).all()

    return render_template("admin_student_detail.html", user=user, student=student, applications=applications)


@app.route("/admin/student/<int:user_id>/blacklist")
def blacklist_student(user_id):

    user = User.query.get_or_404(user_id)
    user.is_active = False
    db.session.commit()

    return redirect("/admin_dashboard")


@app.route("/admin/student/<int:user_id>/unblacklist")
def unblacklist_student(user_id):

    user = User.query.get_or_404(user_id)
    user.is_active = True
    db.session.commit()

    return redirect("/admin_dashboard")





if __name__ == "__main__":

    with app.app_context():
        db.create_all()

        admin_exist = User.query.filter_by(name='admin').first()
        if not admin_exist:
            admin = User(name="admin", email="admin@gmail.com", password="admin", role="admin", is_approved=True)
            db.session.add(admin)
            db.session.commit()

    app.run(debug=True)