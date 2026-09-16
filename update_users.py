import sqlite3
import os

DATABASE_FILE = os.path.join(
    "data",
    "university.db"
)

connection = sqlite3.connect(DATABASE_FILE)
cursor = connection.cursor()

# اضافه کردن نام واقعی
try:
    cursor.execute(
        "ALTER TABLE users ADD COLUMN full_name TEXT"
    )
except sqlite3.OperationalError:
    pass

# اضافه کردن سمت
try:
    cursor.execute(
        "ALTER TABLE users ADD COLUMN position TEXT"
    )
except sqlite3.OperationalError:
    pass

connection.commit()
connection.close()

print()
print("===================================")
print("اطلاعات کاربران به‌روزرسانی شد")
print("نام واقعی و سمت اضافه شد")
print("===================================")