from read_excel import read_excel_data
from database import get_connection, create_database


# ساخت دیتابیس
create_database()


# خواندن اطلاعات Excel
rows = read_excel_data()


connection = get_connection()
cursor = connection.cursor()


# پاک کردن اطلاعات قبلی برای جلوگیری از تکراری شدن
cursor.execute("DELETE FROM posts")


count = 0


for row in rows:

    if len(row) < 6:
        continue

    unit_type = row[0]
    unit = row[1]
    department = row[2]
    post_title = row[3]
    person_name = row[4]
    status = row[5]

    cursor.execute("""
        INSERT INTO posts
        (
            unit_type,
            unit,
            department,
            post_title,
            person_name,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        unit_type,
        unit,
        department,
        post_title,
        person_name,
        status
    ))

    count += 1


connection.commit()
connection.close()


print()
print("===================================")
print("انتقال اطلاعات با موفقیت انجام شد")
print("تعداد رکوردهای منتقل شده:", count)
print("===================================")