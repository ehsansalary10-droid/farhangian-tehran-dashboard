import sqlite3
import os

DATABASE_FILE = os.path.join(
    "data",
    "university.db"
)

connection = sqlite3.connect(
    DATABASE_FILE
)

cursor = connection.cursor()

cursor.execute("""
    INSERT OR IGNORE INTO users
    (
        username,
        password,
        full_name,
        position,
        role
    )
    VALUES (?, ?, ?, ?, ?)
""", (
    "admin",
    "123456",
    "مدیر سامانه",
    "مدیر سامانه ارزیابی و پایش",
    "admin"
))
connection.commit()
connection.close()

print()
print("===================================")
print("کاربر مدیر با موفقیت ایجاد شد")
print("نام کاربری: admin")
print("رمز عبور: 123456")
print("نقش: admin")
print("===================================")