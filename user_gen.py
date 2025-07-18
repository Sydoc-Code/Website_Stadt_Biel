import bcrypt, os, pymssql
from dotenv import load_dotenv
load_dotenv()

DB_UID = os.environ.get("DB_UID")
DB_PWD = os.environ.get("DB_PWD")
DB_SERVER = os.environ.get("DB_SERVER")
DB_SERVER_DB = os.environ.get("DB_SERVER_DB")

try:
    conn = pymssql.connect(
        server=f"{DB_SERVER}:1433",
        user=DB_UID,
        password=DB_PWD,
        database=DB_SERVER_DB
    )
    cursor = conn.cursor()

    username = input("Username: ")

    password = input("Password: ")
    bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(bytes, salt)

    fullname = input("Full name: ")
    email = input("Email: ")

    cursor.execute("""
        INSERT INTO Users
        VALUES(%s, %s, %s, %s)
    """, (username, hashed_password, fullname, email))
    conn.commit()
    conn.close()
    print(f"New User Registered with attributes: {username, hashed_password, fullname, email}")
except Exception as e:
    print(e)
