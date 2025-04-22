# 🏥 SmartCare – Hospital Management System API

SmartCare is a hospital management system API built with Django REST Framework. It provides secure access for both **patients and doctors** with role-based login, appointment booking, and email verification features.

---

## 🚀 Features

- 🔐 Login system for **both Patients and Doctors**
- ✅ Patient registration with **email verification**
- 📅 Appointment booking with doctor integration
- 🩺 Doctor profile management (basic details)
- 🔄 JWT-based authentication
- 📋 Admin dashboard (Django Admin)
- 📬 Email confirmation for registration

---

## 🌟 Upcoming Features

- 🚨 Emergency appointment request button
- 🧑‍⚕️ Advanced doctor dashboard (appointments, patient list)
- 📄 Medical history and prescription records
- 📊 Admin-level analytics & reporting
- 📱 REST API documentation (Swagger/ReDoc)

---

## 🛠 Tech Stack

- Django & Django REST Framework  
- Simple JWT for authentication  
- Django Email Backend  
- SQLite (dev) – PostgreSQL ready

---

## 📦 Installation

```bash
git clone https://github.com/saiful-islam-auny/smart-care-backend.git
cd smartcare
python -m venv env
source env/bin/activate  # or env\Scripts\activate on Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
