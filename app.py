from flask import Flask, render_template, request, redirect, url_for, session
import pyodbc
from dotenv import load_dotenv
import os
from datetime import timedelta
import bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
load_dotenv()

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

app.secret_key = os.environ.get("FLASK_SECRET_KEY")
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True  
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  

DB_UID = os.environ.get("DB_UID")
DB_PWD = os.environ.get("DB_PWD")
DB_SERVER = os.environ.get("DB_SERVER")
DB_SERVER_DB = os.environ.get("DB_SERVER_DB")

@app.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def login():
    if request.method == "POST":
        UID_REQUEST = request.form["username"]
        PWD_REQUEST = request.form["password"]
        
        if not UID_REQUEST or not PWD_REQUEST:
            return render_template("login.html", error="Invalid credentials")
        
        try:
            conn_str = (
                f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                f'SERVER={DB_SERVER}:1434;'
                f'DATABASE={DB_SERVER_DB};'
                f'UID={DB_UID};'
                f'PWD={DB_PWD};' 
                f'TrustServerCertificate=yes;'
            )
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT password FROM Users WHERE username = ?
            """, (UID_REQUEST,))
            user_record = cursor.fetchone()

            if user_record:
                stored_hash = user_record[0]
                if isinstance(stored_hash, str):
                    stored_hash = stored_hash.encode('utf-8')    
            
                if bcrypt.checkpw(PWD_REQUEST.encode('utf-8'), stored_hash):
                    session.clear()  
                    session['username'] = UID_REQUEST
                    session.permanent = True
                    return redirect(url_for("index"))
                
            return render_template("login.html", error="Invalid credentials")
                
        except Exception as e:
            app.logger.error(f"Database error during login: {e}")
            return render_template("login.html", error="Login temporarily unavailable")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for("login"))

@app.route("/")
def index():
    if not session.get('username'):
        return redirect(url_for('login'))
    
    conn_str = (
                f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                f'SERVER={DB_SERVER}:1434;'
                f'DATABASE={DB_SERVER_DB};'
                f'UID={DB_UID};'
                f'PWD={DB_PWD};'
                f'TrustServerCertificate=yes;'
            )
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM v_WebDisplay
    """)
    rows = cursor.fetchall()
    
    columns = [column[0] for column in cursor.description]
    
    conn.close()
    return render_template("table.html", rows=rows, columns=columns)

@app.route("/update_status", methods=["POST"])
def update_status():
    id = request.form.get("ID")
    logged_in_user = session.get('username', 'Unknown')

    conn_str = (
                f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                f'SERVER={DB_SERVER}:1434;'
                f'DATABASE={DB_SERVER_DB};'
                f'UID={DB_UID};'
                f'PWD={DB_PWD};'
                f'TrustServerCertificate=yes;'
            )
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO FileStatuses VALUES(?, null, null, 'Demanded', GETDATE(), ?)",
        (id, logged_in_user)
    )
    cursor.commit()
    conn.close()
    
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
    # app.run(debug=True)