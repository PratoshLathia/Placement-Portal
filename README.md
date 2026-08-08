# 🎓 Placement Portal Application

A centralized web-based campus recruitment platform built with **Flask** and **SQLAlchemy**, enabling structured interaction between Admin, Company, and Student users with approval workflows and application tracking.

---

## 📋 Table of Contents

- [About the Project](#about-the-project)
- [Tech Stack](#tech-stack)
- [Database Schema](#database-schema)
- [Features](#features)
- [API Endpoints](#api-endpoints)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Limitations & Future Enhancements](#limitations--future-enhancements)
- [Author](#author)

---

## About the Project

Institutes require efficient systems to manage campus recruitment processes involving students, companies, and placement drives. This Placement Portal provides a centralized system with role-based access control for three user types:

- **Admin** — Approves companies, jobs, and manages all users
- **Company** — Posts jobs and manages applicant status
- **Student** — Searches jobs and tracks applications

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python |
| Backend Framework | Flask 3.1.3 |
| ORM | SQLAlchemy 2.0.48 / Flask-SQLAlchemy 3.1.1 |
| Database | SQLite |
| Template Engine | Jinja2 3.1.6 |
| Frontend | HTML, CSS, Bootstrap 5 |
| Auth & Sessions | Werkzeug 3.1.7 |

> Full dependency list: see [`requirements.txt`](requirements.txt)

---

## Database Schema

The application uses **5 tables** with the following relationships:

```
users
 ├── student_profiles   (One-to-One via user_id)
 └── company_profiles   (One-to-One via user_id)
          └── jobs      (One-to-Many via company_id)
                └── applications  (Many-to-Many bridge: student ↔ job)
```

### Tables

**`users`** — Base user table for all roles  
`id` · `name` · `email` · `password` · `role` · `is_active` · `is_approved` · `created_at`

**`student_profiles`** — Extended student info  
`id` · `user_id (FK)` · `department` · `cgpa` · `skills` · `resume`

**`company_profiles`** — Extended company info  
`id` · `user_id (FK)` · `company_name` · `industry` · `website` · `location`

**`jobs`** — Job postings by companies  
`id` · `company_id (FK)` · `title` · `description` · `skills` · `experience` · `salary` · `is_approved` · `is_closed` · `posted_at`

**`applications`** — Association table (Student ↔ Job many-to-many)  
`id` · `job_id (FK)` · `student_id (FK)` · `status` · `applied_at`

> Application status values: `Applied` → `Shortlisted` → `Selected` / `Rejected`

---

## Features

### 🔐 Admin
- Approve / reject company registrations
- Approve / reject job postings
- Blacklist / unblacklist students and companies
- Dashboard with statistics and search

### 🏢 Company
- Create and update company profile
- Post, edit, open/close job listings
- View applicants per job
- Manage application status (shortlist / select / reject)

### 🎓 Student
- Create and update student profile (with resume upload)
- Search jobs by company name, title, or skills
- Apply to jobs (duplicate prevention enforced)
- Track real-time application status

### ⚙️ System
- Role-based session management
- Multi-stage approval workflows
- Safe job deletion with confirmation
- Responsive UI with Bootstrap 5

---

## API Endpoints

### Authentication
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/` | Home page |
| GET/POST | `/register` | User registration |
| GET/POST | `/login` | Login |
| GET | `/logout` | Logout |

### Student
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/student_dashboard` | View and search jobs |
| GET/POST | `/student_profile` | Create/update profile |
| POST | `/apply-job/<job_id>` | Apply to a job |
| GET | `/my_applications/<student_id>` | View own applications |

### Company
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/company_dashboard` | Company dashboard |
| GET/POST | `/company_profile` | Create/update profile |
| GET/POST | `/post-job` | Post a new job |
| GET/POST | `/edit-job/<job_id>` | Edit job |
| POST | `/delete-job/<job_id>` | Safe delete job |
| POST | `/confirm-delete/<job_id>` | Force delete job |
| POST | `/toggle-job/<job_id>` | Open/close job |
| GET | `/job-applications/<job_id>` | View applicants |
| GET | `/company/student/<student_id>` | View student profile |

### Admin
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/admin_dashboard` | Admin overview |
| POST | `/admin/user/<user_id>/toggle` | Activate/deactivate user |
| POST | `/admin/company/<user_id>/approve` | Approve company |
| POST | `/admin/company/<user_id>/reject` | Reject company |
| POST | `/admin/company/<user_id>/blacklist` | Blacklist company |
| POST | `/admin/company/<user_id>/unblacklist` | Unblacklist company |
| POST | `/admin/job/<job_id>/approve` | Approve job |
| POST | `/admin/job/<job_id>/reject` | Reject job |
| POST | `/admin/student/<user_id>/blacklist` | Blacklist student |
| POST | `/admin/student/<user_id>/unblacklist` | Unblacklist student |

### Application Management
| Method | Route | Description |
|--------|-------|-------------|
| POST | `/toggle-status/<app_id>/<action>` | Update status (`shortlist` / `select` / `reject`) |

---

## Project Structure

```
placement-portal/
│
├── app.py                  # Main application — routes & models
├── requirements.txt        # Python dependencies
│
├── templates/              # Jinja2 HTML templates
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── admin/
│   ├── company/
│   └── student/
│
└── static/                 # CSS, Bootstrap, JS assets
```

---

## Getting Started

### Prerequisites
- Python 3.8+
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/placement-portal.git
cd placement-portal

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate        # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python app.py
```

The app will be available at `http://127.0.0.1:5000/`

---

## Limitations & Future Enhancements

### Current Limitations
- Passwords stored in plain text (no hashing)
- No email notifications
- No REST API support

### Planned Enhancements
- [ ] Password hashing (e.g., bcrypt)
- [ ] Email notifications for application updates
- [ ] REST API development
- [ ] Advanced frontend with React / AJAX

---

## Author

**Pratosh Lathia**  
Roll No: 23f3003255  
📧 [23f3003255@ds.study.iitm.ac.in](mailto:23f3003255@ds.study.iitm.ac.in)  
🎓 IIT Madras — BS in Data Science and Applications

---

## 📹 Video Demo

[Watch the demo on Google Drive](https://drive.google.com/file/d/1Ld2UnuPSQIH9BzyEVdWShCnESGN7YMaA/view?usp=drive_link)
