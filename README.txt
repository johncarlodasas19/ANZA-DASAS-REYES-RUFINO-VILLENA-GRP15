Campus Lost & Found - Final (Dasas)
====================================

This is a Flask-based Campus Lost & Found system with:
- User registration and login.
- Create, Read, Update, Delete (CRUD) for items.
- Image upload for items (stored in static/uploads).
- SQLite database (campus_lost_and_found.db).
- Bootstrap 5 frontend with soft blue theme.

How to run (Windows - Visual Studio / VS Code):
1. Extract the ZIP folder.
2. Open terminal in the project folder.
3. (Optional but recommended) Create virtual environment:
   python -m venv venv
   venv\Scripts\activate
4. Install dependencies:
   pip install -r requirements.txt
5. Run the app:
   python app.py
6. Open in browser:
   http://127.0.0.1:5000

Demo account:
- Email: demo@school.edu
- Password: password123

Notes:
- Uploaded images are saved to static/uploads/. Files are limited to 4MB.
- If you want to clear sample data, delete campus_lost_and_found.db and restart the app.
