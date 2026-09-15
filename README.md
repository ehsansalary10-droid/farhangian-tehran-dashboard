from flask import Flask, request, redirect, url_for, session, send_file
import pandas as pd
import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

# =========================================================
# تنظیمات
# =========================================================

app = Flask(__name__)

app.secret_key = "farhangian-tehran-secret-key"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

EXCEL_FILE = os.path.join(BASE_DIR, "structure.xlsx")
DB_FILE = os.path.join(BASE_DIR, "users.db")


# =========================================================
# دیتابیس کاربران
# =========================================================

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            fullname TEXT,
            role TEXT DEFAULT 'user'
        )
    """)

    user = conn.execute(
        "SELECT * FROM users WHERE username = ?",
        ("admin",)
    ).fetchone()

    if not user:
        conn.execute(
            """
            INSERT INTO users
            (username, password, fullname, role)
            VALUES (?, ?, ?, ?)
            """,
            (
                "admin",
                generate_password_hash("1234"),
                "مدیر سامانه",
                "admin"
            )
        )

    conn.commit()
    conn.close()


init_db()


# =========================================================
# ورود
# =========================================================

@app.route("/", methods=["GET", "POST"])
def login():

    error = ""

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        conn = get_db()

        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        conn.close()

        if user and check_password_hash(user["password"], password):

            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["fullname"] = user["fullname"]
            session["role"] = user["role"]

            return redirect(url_for("dashboard"))

        error = "نام کاربری یا رمز عبور اشتباه است."

    return f"""
<!DOCTYPE html>
<html lang="fa" dir="rtl">

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1.0">

<title>ورود به سامانه ارزیابی</title>

<style>

* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    font-family: Tahoma, Arial, sans-serif;
    background: linear-gradient(135deg,#0d47a1,#1976d2);
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
}}

.login-box {{
    width: 380px;
    background: white;
    padding: 40px;
    border-radius: 20px;
    box-shadow: 0 15px 40px rgba(0,0,0,.25);
    text-align: center;
}}

.login-box h1 {{
    color: #0d47a1;
    margin-bottom: 10px;
}}

.login-box p {{
    color: #666;
    margin-bottom: 30px;
}}

input {{
    width: 100%;
    padding: 14px;
    margin: 8px 0;
    border: 1px solid #ddd;
    border-radius: 10px;
    font-size: 15px;
}}

button {{
    width: 100%;
    padding: 14px;
    margin-top: 15px;
    border: none;
    border-radius: 10px;
    background: #0d47a1;
    color: white;
    font-size: 16px;
    cursor: pointer;
}}

button:hover {{
    background: #08306b;
}}

.error {{
    color: #d32f2f;
    margin-top: 15px;
}}

.info {{
    margin-top: 25px;
    color: #888;
    font-size: 12px;
}}

</style>

</head>

<body>

<div class="login-box">

<h1>سامانه هوشمند</h1>

<p>دانشگاه فرهنگیان تهران</p>

<form method="POST">

<input
    name="username"
    placeholder="نام کاربری"
    autocomplete="username"
    required
>

<input
    name="password"
    type="password"
    placeholder="رمز عبور"
    autocomplete="current-password"
    required
>

<button type="submit">
ورود به سامانه
</button>

</form>

<div class="error">
{error}
</div>

<div class="info">
سامانه ارزیابی و پایش دانشگاه فرهنگیان تهران
</div>

</div>

</body>

</html>
"""


# =========================================================
# بررسی ورود
# =========================================================

def login_required():

    if "user_id" not in session:
        return False

    return True


# =========================================================
# داشبورد
# =========================================================

@app.route("/dashboard")
def dashboard():

    if not login_required():
        return redirect(url_for("login"))

    return """

<!DOCTYPE html>

<html lang="fa" dir="rtl">

<head>

<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width, initial-scale=1.0">

<title>داشبورد سامانه</title>

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Tahoma, Arial;
    background: #f4f7fb;
}

.sidebar {
    position: fixed;
    right: 0;
    top: 0;
    bottom: 0;
    width: 260px;
    background: #0d47a1;
    color: white;
    padding: 25px 15px;
}

.logo-box {
    text-align: center;
    padding-bottom: 25px;
    border-bottom: 1px solid rgba(255,255,255,.2);
}

.logo-box h2 {
    margin: 10px 0;
}

.menu a {
    display: block;
    color: white;
    text-decoration: none;
    padding: 14px;
    margin: 6px 0;
    border-radius: 8px;
}

.menu a:hover {
    background: rgba(255,255,255,.15);
}

.main {
    margin-right: 260px;
    padding: 35px;
}

.header {
    background: white;
    padding: 25px;
    border-radius: 15px;
    margin-bottom: 25px;
}

.cards {
    display: grid;
    grid-template-columns: repeat(auto-fit,minmax(220px,1fr));
    gap: 20px;
}

.card {
    background: white;
    padding: 25px;
    border-radius: 15px;
    box-shadow: 0 3px 15px rgba(0,0,0,.06);
}

.card h3 {
    color: #0d47a1;
}

.number {
    font-size: 32px;
    font-weight: bold;
}

@media(max-width:800px) {

    .sidebar {
        position: relative;
        width: 100%;
    }

    .main {
        margin-right: 0;
    }

}

</style>

</head>

<body>

<div class="sidebar">

<div class="logo-box">

<h2>دانشگاه فرهنگیان</h2>

<p>سامانه پایش</p>

</div>

<div class="menu">

<a href="/dashboard">🏠 داشبورد اصلی</a>

<a href="/structure">🏢 ساختار سازمانی</a>

<a href="/management">👥 مدیریت و کارکنان</a>

<a href="/empty">📋 پست‌های خالی</a>

<a href="/search">🔎 جست‌وجوی هوشمند</a>

<a href="/orgchart">🌐 چارت سازمانی</a>

<a href="/export">📊 دریافت گزارش Excel</a>

<a href="/users">👤 مدیریت کاربران</a>

<a href="/logout">🚪 خروج</a>

</div>

</div>


<div class="main">

<div class="header">

<h1>داشبورد سامانه پایش</h1>

<p>
خوش آمدید
</p>

</div>


<div class="cards">

<div class="card">

<h3>ساختار سازمانی</h3>

<p>
مشاهده ساختار و واحدهای دانشگاه
</p>

<a href="/structure">
مشاهده
</a>

</div>


<div class="card">

<h3>مدیریت و کارکنان</h3>

<p>
اطلاعات کارکنان و پست‌ها
</p>

<a href="/management">
مشاهده
</a>

</div>


<div class="card">

<h3>پست‌های خالی</h3>

<p>
مشاهده پست‌های فاقد متصدی
</p>

<a href="/empty">
مشاهده
</a>

</div>


<div class="card">

<h3>جست‌وجوی هوشمند</h3>

<p>
جست‌وجو در اطلاعات ساختاری
</p>

<a href="/search">
جست‌وجو
</a>

</div>


</div>

</div>

</body>

</html>

"""


# =========================================================
# خواندن Excel
# =========================================================

def load_excel():

    if not os.path.exists(EXCEL_FILE):
        return pd.DataFrame()

    try:

        df = pd.read_excel(
            EXCEL_FILE,
            sheet_name="داده‌های ساختاری"
        )

        df = df.fillna("")

        return df

    except Exception:

        try:

            df = pd.read_excel(EXCEL_FILE)
            return df.fillna("")

        except Exception:

            return pd.DataFrame()


# =========================================================
# ساختار سازمانی
# =========================================================

@app.route("/structure")
def structure():

    if not login_required():
        return redirect(url_for("login"))

    df = load_excel()

    if df.empty:
        return page(
            "ساختار سازمانی",
            "<p>فایل structure.xlsx پیدا نشد یا اطلاعاتی در آن وجود ندارد.</p>"
        )

    rows = ""

    for _, row in df.iterrows():

        cells = ""

        for value in row.tolist():

            cells += f"<td>{value}</td>"

        rows += f"<tr>{cells}</tr>"

    headers = ""

    for col in df.columns:

        headers += f"<th>{col}</th>"

    html = f"""

<table>

<thead>

<tr>

{headers}

</tr>

</thead>

<tbody>

{rows}

</tbody>

</table>

"""

    return page("ساختار سازمانی", html)


# =========================================================
# مدیریت و کارکنان
# =========================================================

@app.route("/management")
def management():

    if not login_required():
        return redirect(url_for("login"))

    df = load_excel()

    if df.empty:
        return page(
            "مدیریت و کارکنان",
            "<p>اطلاعاتی یافت نشد.</p>"
        )

    total = len(df)

    html = f"""

<div class="cards">

<div class="stat">

<h2>{total}</h2>

<p>تعداد رکوردها</p>

</div>

</div>

"""

    return page("مدیریت و کارکنان", html)


# =========================================================
# پست‌های خالی
# =========================================================

@app.route("/empty")
def empty():

    if not login_required():
        return redirect(url_for("login"))

    df = load_excel()

    if df.empty:
        return page(
            "پست‌های خالی",
            "<p>اطلاعاتی یافت نشد.</p>"
        )

    if "وضعیت" in df.columns:

        empty_df = df[
            df["وضعیت"].astype(str).str.contains(
                "خالی|بلاتصدی|فاقد",
                case=False,
                na=False
            )
        ]

    elif "نام فرد" in df.columns:

        empty_df = df[
            df["نام فرد"].astype(str).str.strip() == ""
        ]

    else:

        empty_df = pd.DataFrame()

    if empty_df.empty:

        return page(
            "پست‌های خالی",
            "<h3>پست خالی پیدا نشد.</h3>"
        )

    headers = ""

    for col in empty_df.columns:
        headers += f"<th>{col}</th>"

    rows = ""

    for _, row in empty_df.iterrows():

        cells = ""

        for value in row.tolist():
            cells += f"<td>{value}</td>"

        rows += f"<tr>{cells}</tr>"

    html = f"""

<table>

<thead>
<tr>
{headers}
</tr>
</thead>

<tbody>
{rows}
</tbody>

</table>

"""

    return page("پست‌های خالی", html)


# =========================================================
# جستجو
# =========================================================

@app.route("/search", methods=["GET", "POST"])
def search():

    if not login_required():
        return redirect(url_for("login"))

    query = request.form.get("query", "").strip()

    df = load_excel()

    result_html = ""

    if query and not df.empty:

        mask = df.astype(str).apply(
            lambda column:
            column.str.contains(
                query,
                case=False,
                na=False
            )
        ).any(axis=1)

        result = df[mask]

        if not result.empty:

            headers = ""

            for col in result.columns:
                headers += f"<th>{col}</th>"

            rows = ""

            for _, row in result.iterrows():

                cells = ""

                for value in row.tolist():
                    cells += f"<td>{value}</td>"

                rows += f"<tr>{cells}</tr>"

            result_html = f"""

<h3>نتایج جست‌وجو</h3>

<table>

<thead>
<tr>
{headers}
</tr>
</thead>

<tbody>
{rows}
</tbody>

</table>

"""

        else:

            result_html = "<p>موردی پیدا نشد.</p>"

    return page(
        "جست‌وجوی هوشمند",
        f"""

<form method="POST">

<input
    name="query"
    placeholder="نام، واحد، پست یا هر عبارت دیگر..."
    value="{query}"
    style="
        width:70%;
        padding:14px;
        border:1px solid #ddd;
        border-radius:8px;
    "
>

<button type="submit">
جست‌وجو
</button>

</form>

{result_html}

"""
    )


# =========================================================
# چارت سازمانی
# =========================================================

@app.route("/orgchart")
def orgchart():

    if not login_required():
        return redirect(url_for("login"))

    df = load_excel()

    if df.empty:
        return page(
            "چارت سازمانی",
            "<p>اطلاعات ساختاری پیدا نشد.</p>"
        )

    units = []

    if "نوع واحد" in df.columns:

        units = sorted(
            [
                str(x)
                for x in df["نوع واحد"].unique()
                if str(x).strip()
            ]
        )

    html = """

<h2>چارت سازمانی دانشگاه فرهنگیان تهران</h2>

<div class="chart">

<div class="root">
دانشگاه فرهنگیان تهران
</div>

"""

    for unit in units:

        html += f"""

<div class="unit">

{unit}

</div>

"""

    html += """

</div>

"""

    return page("چارت سازمانی", html)


# =========================================================
# خروجی Excel
# =========================================================

@app.route("/export")
def export():

    if not login_required():
        return redirect(url_for("login"))

    if not os.path.exists(EXCEL_FILE):

        return page(
            "گزارش Excel",
            "<p>فایل Excel پیدا نشد.</p>"
        )

    return send_file(
        EXCEL_FILE,
        as_attachment=True,
        download_name="گزارش_ساختار_دانشگاه.xlsx"
    )


# =========================================================
# مدیریت کاربران
# =========================================================

@app.route("/users")
def users():

    if not login_required():
        return redirect(url_for("login"))

    if session.get("role") != "admin":

        return page(
            "دسترسی غیرمجاز",
            "<h2>شما دسترسی مدیریت کاربران را ندارید.</h2>"
        )

    conn = get_db()

    users_list = conn.execute(
        "SELECT * FROM users ORDER BY id DESC"
    ).fetchall()

    conn.close()

    rows = ""

    for user in users_list:

        rows += f"""

<tr>

<td>{user["id"]}</td>

<td>{user["username"]}</td>

<td>{user["fullname"]}</td>

<td>{user["role"]}</td>

<td>

<a href="/users/delete/{user["id"]}"
   onclick="return confirm('حذف شود؟')">

حذف

</a>

</td>

</tr>

"""

    html = f"""

<h2>مدیریت کاربران</h2>

<a class="btn" href="/users/add">
➕ افزودن کاربر
</a>

<table>

<thead>

<tr>

<th>شناسه</th>
<th>نام کاربری</th>
<th>نام کامل</th>
<th>نقش</th>
<th>عملیات</th>

</tr>

</thead>

<tbody>

{rows}

</tbody>

</table>

"""

    return page("مدیریت کاربران", html)


# =========================================================
# افزودن کاربر
# =========================================================

@app.route("/users/add", methods=["GET", "POST"])
def add_user():

    if not login_required():
        return redirect(url_for("login"))

    if session.get("role") != "admin":

        return page(
            "دسترسی غیرمجاز",
            "<h2>دسترسی ندارید.</h2>"
        )

    error = ""

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        fullname = request.form.get("fullname", "").strip()
        role = request.form.get("role", "user")

        if not username or not password:

            error = "نام کاربری و رمز عبور الزامی است."

        else:

            try:

                conn = get_db()

                conn.execute(
                    """
                    INSERT INTO users
                    (username,password,fullname,role)
                    VALUES (?,?,?,?)
                    """,
                    (
                        username,
                        generate_password_hash(password),
                        fullname,
                        role
                    )
                )

                conn.commit()
                conn.close()

                return redirect(url_for("users"))

            except sqlite3.IntegrityError:

                error = "این نام کاربری قبلاً ثبت شده است."

    html = f"""

<h2>افزودن کاربر</h2>

<p style="color:red;">
{error}
</p>

<form method="POST">

<input
    name="fullname"
    placeholder="نام و نام خانوادگی"
    required
>

<input
    name="username"
    placeholder="نام کاربری"
    required
>

<input
    name="password"
    type="password"
    placeholder="رمز عبور"
    required
>

<select name="role">

<option value="user">
کاربر
</option>

<option value="admin">
مدیر
</option>

</select>

<button type="submit">
ذخیره کاربر
</button>

</form>

"""

    return page("افزودن کاربر", html)


# =========================================================
# حذف کاربر
# =========================================================

@app.route("/users/delete/<int:user_id>")
def delete_user(user_id):

    if not login_required():
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    if user_id == session.get("user_id"):

        return page(
            "خطا",
            "<h3>نمی‌توانید حساب خودتان را حذف کنید.</h3>"
        )

    conn = get_db()

    conn.execute(
        "DELETE FROM users WHERE id = ?",
        (user_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("users"))


# =========================================================
# خروج
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# =========================================================
# قالب صفحات
# =========================================================

def page(title, content):

    return f"""

<!DOCTYPE html>

<html lang="fa" dir="rtl">

<head>

<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width, initial-scale=1.0">

<title>{title}</title>

<style>

* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    font-family: Tahoma, Arial;
    background: #f4f7fb;
    color: #222;
}}

header {{
    background: #0d47a1;
    color: white;
    padding: 20px 30px;
}}

.container {{
    max-width: 1400px;
    margin: auto;
    padding: 30px;
}}

.card {{
    background: white;
    padding: 25px;
    border-radius: 15px;
    box-shadow: 0 3px 15px rgba(0,0,0,.07);
}}

table {{
    width: 100%;
    border-collapse: collapse;
    margin-top: 25px;
    background: white;
}}

th {{
    background: #0d47a1;
    color: white;
}}

th, td {{
    padding: 12px;
    border: 1px solid #ddd;
    text-align: right;
}}

tr:nth-child(even) {{
    background: #f8f9fa;
}}

input, select {{
    padding: 12px;
    margin: 6px;
    border: 1px solid #ddd;
    border-radius: 8px;
}}

button, .btn {{
    display: inline-block;
    background: #0d47a1;
    color: white;
    border: none;
    padding: 12px 20px;
    border-radius: 8px;
    text-decoration: none;
    cursor: pointer;
}}

.stat {{
    background: white;
    padding: 25px;
    margin-bottom: 20px;
    border-radius: 15px;
}}

.chart {{
    text-align: center;
    padding: 30px;
}}

.root {{
    background: #0d47a1;
    color: white;
    padding: 25px;
    border-radius: 15px;
    margin-bottom: 30px;
    font-size: 22px;
}}

.unit {{
    display: inline-block;
    background: white;
    border: 2px solid #1976d2;
    padding: 20px;
    margin: 10px;
    border-radius: 12px;
}}

a {{
    color: #0d47a1;
}}

</style>

</head>

<body>

<header>

<h2>
{title}
</h2>

</header>

<div class="container">

<div class="card">

{content}

<br><br>

<a href="/dashboard">
⬅ بازگشت به داشبورد
</a>

</div>

</div>

</body>

</html>

"""


# =========================================================
# اجرای برنامه
# =========================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
