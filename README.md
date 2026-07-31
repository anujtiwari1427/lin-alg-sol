# 🧮 Linear Algebra Solver

A production-ready educational SaaS web application designed for students, educators, and engineers to perform, visualize, and learn linear algebra operations with step-by-step mathematical explanations.

---

## 🌟 Features

- **Modern Glassmorphic UI/UX**: Inspired by Notion, Linear, and Stripe with dark and light theme modes.
- **Interactive Dashboard**: Modern analytics, quick calculators, and seamless search integration.
- **Responsive Layout**: Designed for mobile, tablet, and desktop viewports.
- **Comprehensive Math Modules** (Phases 1–11):
  - Matrix Operations (Addition, Multiplication, Transpose, Rank, Trace, etc.)
  - Determinants & Matrix Inverses (Cofactor, Adjoint, Step-by-step MathJax rendering)
  - Vector Analysis & Interactive Visualization
  - System of Linear Equations (Gaussian Elimination, Cramer's Rule, Matrix Method)
  - Eigenvalues & Eigenvectors
  - Interactive Learning Center (Theory, Practice, Quizzes, Flashcards)

---

## 🚀 Virtual Environment Setup & Local Development

### 1. Prerequisites
- Python 3.12 or later
- `pip` package manager

### 2. Clone / Navigate to Project Directory
```bash
cd linear-algebra-solver
```

### 3. Create Virtual Environment

#### On Windows (PowerShell / Command Prompt):
```powershell
python -m venv venv
venv\Scripts\activate
```

#### On macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the Application
```bash
python app.py
```
Open your browser and navigate to `http://127.0.0.1:5000`.

---

## 📂 Project Structure

```
linear-algebra-solver/
├── app.py                  # Main Application Entry Point & Factory
├── config.py               # Application Configurations
├── requirements.txt        # Backend Dependencies
├── README.md               # Project Documentation
├── .gitignore              # Git Ignore Directives
├── controllers/            # Request Handlers & Blueprints
│   ├── __init__.py
│   └── main_controller.py  # Dashboard, Landing, & Navigation Routes
├── services/               # Business Logic & Solvers
│   └── __init__.py
├── models/                 # Data Models & Schemas
│   ├── __init__.py
│   └── calculation.py      # Calculation History Model
├── database/               # Database Connection & Schema Setup
│   ├── app.db
│   └── db.py
├── templates/              # Jinja2 Templates
│   ├── base.html           # Master Layout Template
│   ├── landing.html        # Animated SaaS Landing Page
│   ├── dashboard.html      # Glassmorphic User Dashboard
│   ├── components/         # Modular Components
│   │   ├── navbar.html
│   │   ├── sidebar.html
│   │   └── footer.html
│   └── errors/             # Error Templates (404, 500)
│       ├── 404.html
│       └── 500.html
├── static/                 # Static Assets
│   ├── css/
│   │   └── style.css       # Custom Glassmorphism & Theme Styles
│   └── js/
│       ├── main.js         # Theme Switcher, Search & UI Handlers
│       └── dashboard.js    # Chart.js Integration & Dashboard Widgets
└── tests/                  # Automated Test Suite
    └── test_app.py         # Unit Tests
```

---

## 🛠️ Tech Stack

- **Backend**: Python 3.12, Flask, NumPy, SymPy, SQLite, Jinja2
- **Frontend**: HTML5, CSS3, Bootstrap 5, Vanilla JavaScript, Chart.js, MathJax 3, Font Awesome 6
- **Architecture**: MVC (Model-View-Controller), Modular Blueprints, Clean Code Principles
