Campus Lost & Found -GROUP 15 ( THIS IS RUNNING AND WORKING WITHOUT AI MATCHING SO THIS IS OUR PROGRESS WEEK 8-9)
====================================

(ONGOING- WE WLL JUST ADD FEATURES WHICH IS AI MATCHING AND OUR PROGRAM IS READY TO DEMO IN PRESENTATION AND WE WILL UPDATE THE PROGRESS IN WEEK 9-11)

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

Demo account: (OR YOU CAN LOGIN VIA REGISTER AND LOGIN ACCOUTN)
- Email: demo@school.edu
- Password: password123

Notes:
- Uploaded images are saved to static/uploads/. Files are limited to 4MB.
- If you want to clear sample data, delete campus_lost_and_found.db and restart the app.
