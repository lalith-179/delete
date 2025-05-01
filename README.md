# BookMyTicket

## Instructions After Unzipping

### 1. Navigate to the Project Directory
```bash
cd bookmyticket
```

### 2. Set Up Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows
venv\Scripts\activate

# On macOS/Linux
# source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup
```bash
# Only if db.sqlite3 is NOT included in the zip:
# Apply migrations
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser
```

### 5. Run the Application
```bash
python manage.py runserver
```

### 6. Access the Application
- Main website: http://localhost:8000/
- Admin login: http://localhost:8000/accounts/adminlogin/
- User login: http://localhost:8000/accounts/usersignin/
