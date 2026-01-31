# 📚 Modern AI Library Management System (v4.0)

![License](https://img.shields.io/badge/license-MIT-blue.svg) ![Python](https://img.shields.io/badge/python-3.x-blue) ![React](https://img.shields.io/badge/react-18-cyan) ![PWA](https://img.shields.io/badge/PWA-Ready-purple)

A state-of-the-art Library Management System that modernizes a legacy Python backend with a stunning, AI-powered React frontend. 

## 🚀 Features

### ✨ Modern UI/UX
- **Glassmorphism Design**: Sleek, modern interface with frosted glass effects.
- **Dark/Light Mode**: Fully adaptive theming with persistent preferences.
- **Responsive & PWA**: Mobile-first design that can be installed as an App on your phone.

### 🤖 AI-Powered
- **AI Librarian Chatbot**: Ask "Who is Sherlock Holmes?" or "Recommend a mystery book" and get context-aware answers.
- **Smart Recommendations**: Visual "Recommended for You" section based on reading patterns.
- **Explainable AI**: Visual badges explaining *why* a book was recommended.

### 🛠️ Advanced Management
- **Role-Based Access Control (RBAC)**:
  - **Admin**: Full control, manage books (Add/Delete/Issue/Return), view all history.
  - **Librarian**: Issue/Return books, view history.
  - **Student**: View profile, search books, get recommendations.
- **Visual Analytics**: Interactive dashboard with charts and real-time statistics.
- **Audit Logs**: Full transaction history tracking.

## 🏗️ Architecture

This project uses a unique "Backend Adapter" pattern to modernize a legacy system without rewriting it:
- **Backend**: Python (Flask) acts as a wrapper around the legacy `LMS` class, mocking CLI inputs to expose a RESTful API.
- **Frontend**: React (No-Build) using ES Modules, Tailwind CSS, and Framer Motion directly in the browser.

## 📦 Installation & Deployment

### Local Setup
1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/library-management-system.git
   cd library-management-system
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Server**
   ```bash
   python server.py
   ```
   The app will start at `http://127.0.0.1:5000`.

### Web Deployment (Heroku / Render)
This project is configured for cloud deployment.
- `Procfile` included for Gunicorn.
- `requirements.txt` ready.
- Just push to your platform of choice!

## 🔑 Default Credentials

| Role | Username / Email | Password / Mobile |
| :--- | :--- | :--- |
| **Administrator** | - | `admin123` |
| **Librarian** | - | `lib123` |
| **Student** | `student@uni.edu` | `1234567890` |

## 📸 Screenshots
*(Add your screenshots here)*

---
**v4.0 Update Notes**:
- Added PWA Manifest and Service Worker support.
- Implemented Librarian role.
- Added `/api/history` endpoint and UI.
