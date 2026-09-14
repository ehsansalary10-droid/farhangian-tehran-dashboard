from flask import Flask, request, redirect, url_for, session, send_from_directory
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = "farhangian-tehran-secret-key"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILE = os.path.join(BASE_DIR, "structure.xlsx")
STATIC_DIR = os.path.join(BASE_DIR, "static")


# =========================================================
# خواندن اطلاعات اکسل
# =========================================================

def load_excel():
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name="داده‌های ساختاری")

        required_columns = [
            "نوع واحد",
            "واحد",
            "بخش/معاونت",
            "عنوان پست",
            "نام فرد",
            "وضعیت"
        ]

        for col in required_columns:
            if col not in df.columns:
                df[col] = ""

        df = df[required_columns].copy()
        df = df.fillna("")

        # حفظ ساختار سلسله مراتبی اکسل
        current_type = ""
        current_unit = ""
        current_section = ""

        types = []
        units = []
        sections = []

        for _, row in df.iterrows():

            if str(row["نوع واحد"]).strip():
                current_type = str(row["نوع واحد"]).strip()

            if str(row["واحد"]).strip():
                current_unit = str(row["واحد"]).strip()

            if str(row["بخش/معاونت"]).strip():
                current_section = str(row["بخش/معاونت"]).strip()

            types.append(current_type)
            units.append(current_unit)
            sections.append(current_section)

        df["نوع واحد"] = types
        df["واحد"] = units
        df["بخش/معاونت"] = sections

        return df

    except Exception as e:
        print("خطا در خواندن اکسل:", e)
        return pd.DataFrame(columns=[
            "نوع واحد",
            "واحد",
            "بخش/معاونت",
            "عنوان پست",
            "نام فرد",
            "وضعیت"
        ])


# =========================================================
# تشخیص پست خالی
# =========================================================

def is_empty(row):

    status = str(row["وضعیت"]).strip().lower()
    name = str(row["نام فرد"]).strip().lower()

    empty_statuses = [
        "خالی",
        "بلاتصدی",
        "فاقد",
        "بدون متصدی",
        "بدون فرد",
        "فاقد متصدی",
        "خالی است"
    ]

    empty_names = [
        "",
        "nan",
        "none",
        "-",
        "*",
        "خالی",
        "فاقد فرد",
        "بدون فرد"
    ]

    if status in empty_statuses:
        return True

    if name in empty_names:
        return True

    return False


# =========================================================
# آمار
# =========================================================

def get_stats(df):

    total = len(df)

    if total == 0:
        return {
            "total": 0,
            "filled": 0,
            "empty": 0,
            "percent": 0
        }

    empty_count = sum(is_empty(row) for _, row in df.iterrows())
    filled_count = total - empty_count

    percent = round((filled_count / total) * 100)

    return {
        "total": total,
        "filled": filled_count,
        "empty": empty_count,
        "percent": percent
    }


# =========================================================
# قالب اصلی پنل
# =========================================================

def dashboard_page(content):

    return f"""
<!DOCTYPE html>
<html lang="fa" dir="rtl">

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1.0">

<title>سامانه هوشمند دانشگاه فرهنگیان تهران</title>

<style>

* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    font-family: Tahoma, Arial, sans-serif;
    background: #f4f7fb;
    color: #172033;
}}

.sidebar {{
    position: fixed;
    right: 0;
    top: 0;
    width: 260px;
    height: 100vh;
    background: linear-gradient(180deg,#063b73,#0a5ca8);
    color: white;
    padding: 25px 15px;
    overflow-y: auto;
}}

.logo-box {{
    text-align: center;
    padding-bottom: 20px;
    border-bottom: 1px solid rgba(255,255,255,.2);
}}

.logo {{
    width: 82px;
    height: 82px;
    object-fit: contain;
    background: white;
    border-radius: 50%;
    padding: 5px;
}}

.logo-title {{
    font-size: 17px;
    font-weight: bold;
    margin-top: 12px;
}}

.logo-subtitle {{
    font-size: 12px;
    opacity: .8;
    margin-top: 5px;
}}

.menu {{
    margin-top: 25px;
}}

.menu a {{
    display: block;
    color: white;
    text-decoration: none;
    padding: 13px 15px;
    margin: 7px 0;
    border-radius: 10px;
    transition: .2s;
}}

.menu a:hover {{
    background: rgba(255,255,255,.16);
    transform: translateX(-3px);
}}

.main {{
    margin-right: 260px;
    padding: 25px;
}}

.topbar {{
    background: white;
    border-radius: 15px;
    padding: 18px 22px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 4px 18px rgba(0,0,0,.06);
    margin-bottom: 20px;
}}

.top-title {{
    font-size: 20px;
    font-weight: bold;
    color: #063b73;
}}

.user {{
    color: #667085;
    font-size: 14px;
}}

.welcome {{
    background: linear-gradient(135deg,#07549b,#0d77c9);
    color: white;
    border-radius: 18px;
    padding: 25px;
    margin-bottom: 20px;
    box-shadow: 0 8px 25px rgba(0,80,160,.18);
}}

.welcome h1 {{
    margin: 0 0 8px 0;
    font-size: 24px;
}}

.welcome p {{
    margin: 0;
    opacity: .9;
}}

.cards {{
    display: grid;
    grid-template-columns: repeat(4,1fr);
    gap: 18px;
    margin-bottom: 22px;
}}

.card {{
    background: white;
    border-radius: 16px;
    padding: 22px;
    box-shadow: 0 5px 18px rgba(0,0,0,.06);
}}

.card-title {{
    color: #667085;
    font-size: 14px;
}}

.card-number {{
    font-size: 32px;
    font-weight: bold;
    color: #063b73;
    margin-top: 8px;
}}

.section {{
    background: white;
    border-radius: 16px;
    padding: 22px;
    margin-bottom: 22px;
    box-shadow: 0 5px 18px rgba(0,0,0,.05);
}}

.section-title {{
    font-size: 19px;
    font-weight: bold;
    color: #063b73;
    margin-bottom: 18px;
}}

.progress {{
    height: 12px;
    background: #edf1f5;
    border-radius: 10px;
    overflow: hidden;
}}

.progress-bar {{
    height: 100%;
    background: linear-gradient(90deg,#087fce,#14a6e8);
    border-radius: 10px;
}}

table {{
    width: 100%;
    border-collapse: collapse;
}}

th {{
    background: #063b73;
    color: white;
    padding: 13px;
    text-align: center;
}}

td {{
    padding: 12px;
    border-bottom: 1px solid #edf0f4;
    text-align: center;
}}

tr:hover {{
    background: #f7faff;
}}

.badge {{
    display: inline-block;
    padding: 5px 10px;
    border-radius: 20px;
    font-size: 12px;
}}

.badge-green {{
    background: #dcfce7;
    color: #166534;
}}

.badge-red {{
    background: #fee2e2;
    color: #991b1b;
}}

.filter-box {{
    display: grid;
    grid-template-columns: repeat(4,1fr);
    gap: 12px;
    margin-bottom: 20px;
}}

select,
input {{
    width: 100%;
    padding: 12px;
    border: 1px solid #d7dee8;
    border-radius: 9px;
    font-family: inherit;
    background: white;
}}

.btn {{
    background: #07549b;
    color: white;
    border: none;
    border-radius: 9px;
    padding: 12px 20px;
    cursor: pointer;
    font-family: inherit;
}}

.btn:hover {{
    background: #063b73;
}}

.footer {{
    text-align: center;
    color: #8892a0;
    padding: 20px;
    font-size: 12px;
}}

@media(max-width:1000px) {{

    .sidebar {{
        position: relative;
        width: 100%;
        height: auto;
    }}

    .main {{
        margin-right: 0;
    }}

    .cards {{
        grid-template-columns: repeat(2,1fr);
    }}

    .filter-box {{
        grid-template-columns: 1fr 1fr;
    }}
}}

@media(max-width:600px) {{

    .cards {{
        grid-template-columns: 1fr;
    }}

    .filter-box {{
        grid-template-columns: 1fr;
    }}

}}

</style>

</head>

<body>

<div class="sidebar">

<div class="logo-box">

<img class="logo"
     src="/logo.png"
     onerror="this.style.display='none';">

<div class="logo-title">
دانشگاه فرهنگیان تهران
</div>

<div class="logo-subtitle">
سامانه هوشمند پایش و ارزیابی
</div>

</div>

<div class="menu">

<a href="/dashboard">🏠 داشبورد اصلی</a>

<a href="/structure">🏢 ساختار سازمانی</a>

<a href="/management">👥 مدیریت و کارکنان</a>

<a href="/empty">⚠️ پست‌های خالی</a>

<a href="/search">🔎 جست‌وجوی هوشمند</a>

<a href="/orgchart">🌐 چارت سازمانی</a>

<a href="/export">📊 دریافت گزارش Excel</a>

</div>

</div>

<div class="main">

<div class="topbar">

<div class="top-title">
سامانه هوشمند پایش دانشگاه فرهنگیان تهران
</div>

<div class="user">
کاربر: مدیر سامانه
</div>

</div>

{content}

<div class="footer">
روابط عمومی دانشگاه فرهنگیان تهران
</div>

</div>

</body>
</html>
"""


# =========================================================
# ورود
# =========================================================

@app.route("/", methods=["GET", "POST"])
def login():

    error = ""

    if request.method == "POST":

        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if username == "admin" and password == "1234":

            session["logged_in"] = True

            return redirect(url_for("dashboard"))

        error = "نام کاربری یا رمز عبور صحیح نیست."

    return f"""
<!DOCTYPE html>
<html lang="fa" dir="rtl">

<head>

<meta charset="UTF-8">

<title>ورود به سامانه</title>

<style>

body {{
    margin: 0;
    background: linear-gradient(135deg,#063b73,#087dcc);
    font-family: Tahoma,Arial;
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100vh;
}}

.login {{
    width: 380px;
    background: white;
    border-radius: 20px;
    padding: 35px;
    box-shadow: 0 15px 40px rgba(0,0,0,.2);
    text-align: center;
}}

.login h1 {{
    color: #063b73;
}}

input {{
    width: 100%;
    padding: 13px;
    margin: 8px 0;
    box-sizing: border-box;
    border: 1px solid #ddd;
    border-radius: 10px;
    font-family: Tahoma;
}}

button {{
    width: 100%;
    padding: 13px;
    background: #07549b;
    color: white;
    border: none;
    border-radius: 10px;
    margin-top: 10px;
    cursor: pointer;
    font-family: Tahoma;
}}

.error {{
    color: #c62828;
    margin-top: 12px;
}}

</style>

</head>

<body>

<div class="login">

<h1>سامانه هوشمند</h1>

<p>دانشگاه فرهنگیان تهران</p>

<form method="POST">

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

<button type="submit">
ورود به سامانه
</button>

</form>

<div class="error">
{error}
</div>

</div>

</body>
</html>
"""


# =========================================================
# بررسی ورود
# =========================================================

def check_login():

    if not session.get("logged_in"):
        return False

    return True


# =========================================================
# داشبورد
# =========================================================

@app.route("/dashboard")
def dashboard():

    if not check_login():
        return redirect("/")

    df = load_excel()

    stats = get_stats(df)

    units = []

    for unit in df["واحد"].drop_duplicates():

        if not str(unit).strip():
            continue

        unit_df = df[df["واحد"] == unit]

        s = get_stats(unit_df)

        units.append({
            "name": unit,
            **s
        })

    rows = ""

    for item in units:

        rows += f"""
        <tr>

        <td>{item["name"]}</td>

        <td>{item["total"]}</td>

        <td>
            <span class="badge badge-green">
            {item["filled"]}
            </span>
        </td>

        <td>
            <span class="badge badge-red">
            {item["empty"]}
            </span>
        </td>

        <td style="min-width:180px">

            <div class="progress">

                <div class="progress-bar"
                     style="width:{item["percent"]}%">
                </div>

            </div>

            <small>
            {item["percent"]} درصد
            </small>

        </td>

        </tr>
        """

    content = f"""

<div class="welcome">

<h1>
داشبورد مدیریتی دانشگاه فرهنگیان تهران
</h1>

<p>
نمایش هوشمند وضعیت ساختار سازمانی و پست‌های دانشگاه
</p>

</div>

<div class="cards">

<div class="card">

<div class="card-title">
مجموع پست‌ها
</div>

<div class="card-number">
{stats["total"]}
</div>

</div>

<div class="card">

<div class="card-title">
پست‌های دارای متصدی
</div>

<div class="card-number">
{stats["filled"]}
</div>

</div>

<div class="card">

<div class="card-title">
پست‌های خالی
</div>

<div class="card-number">
{stats["empty"]}
</div>

</div>

<div class="card">

<div class="card-title">
درصد تکمیل ساختار
</div>

<div class="card-number">
{stats["percent"]}%
</div>

</div>

</div>

<div class="section">

<div class="section-title">
وضعیت کلی ساختار
</div>

<div class="progress">

<div class="progress-bar"
     style="width:{stats["percent"]}%">
</div>

</div>

<p>
درصد تکمیل پست‌های سازمانی:
<b>{stats["percent"]}%</b>
</p>

</div>

<div class="section">

<div class="section-title">
گزارش واحدهای دانشگاه
</div>

<table>

<thead>

<tr>

<th>واحد</th>
<th>کل پست</th>
<th>دارای متصدی</th>
<th>خالی</th>
<th>درصد تکمیل</th>

</tr>

</thead>

<tbody>

{rows}

</tbody>

</table>

</div>

"""

    return dashboard_page(content)


# =========================================================
# ساختار سازمانی + فیلتر
# =========================================================

@app.route("/structure")
def structure():

    if not check_login():
        return redirect("/")

    df = load_excel()

    selected_unit = request.args.get("unit", "")
    selected_status = request.args.get("status", "")
    search_text = request.args.get("q", "").strip()

    units = sorted([
        str(x) for x in df["واحد"].drop_duplicates()
        if str(x).strip()
    ])

    filtered = df.copy()

    if selected_unit:
        filtered = filtered[
            filtered["واحد"].astype(str) == selected_unit
        ]

    if selected_status == "empty":

        filtered = filtered[
            filtered.apply(is_empty, axis=1)
        ]

    elif selected_status == "filled":

        filtered = filtered[
            ~filtered.apply(is_empty, axis=1)
        ]

    if search_text:

        mask = filtered.astype(str).apply(
            lambda row:
            row.str.contains(
                search_text,
                case=False,
                na=False
            ).any(),
            axis=1
        )

        filtered = filtered[mask]

    unit_options = '<option value="">همه واحدها</option>'

    for unit in units:

        selected = "selected" if unit == selected_unit else ""

        unit_options += f"""
        <option value="{unit}" {selected}>
        {unit}
        </option>
        """

    table_rows = ""

    for _, row in filtered.iterrows():

        empty = is_empty(row)

        status_html = (
            '<span class="badge badge-red">خالی</span>'
            if empty
            else
            '<span class="badge badge-green">دارای متصدی</span>'
        )

        table_rows += f"""

        <tr>

        <td>{row["نوع واحد"]}</td>

        <td>{row["واحد"]}</td>

        <td>{row["بخش/معاونت"]}</td>

        <td>{row["عنوان پست"]}</td>

        <td>{row["نام فرد"]}</td>

        <td>{status_html}</td>

        </tr>

        """

    content = f"""

<div class="section">

<div class="section-title">
🔎 فیلتر هوشمند ساختار سازمانی
</div>

<form method="GET">

<div class="filter-box">

<select name="unit">

{unit_options}

</select>

<select name="status">

<option value="">
همه وضعیت‌ها
</option>

<option value="filled"
{"selected" if selected_status == "filled" else ""}>
دارای متصدی
</option>

<option value="empty"
{"selected" if selected_status == "empty" else ""}>
پست خالی
</option>

</select>

<input
name="q"
value="{search_text}"
placeholder="جستجو در ساختار..."
>

<button class="btn">
اعمال فیلتر
</button>

</div>

</form>

</div>

<div class="section">

<div class="section-title">
ساختار سازمانی
</div>

<table>

<thead>

<tr>

<th>نوع واحد</th>
<th>واحد</th>
<th>بخش/معاونت</th>
<th>عنوان پست</th>
<th>نام فرد</th>
<th>وضعیت</th>

</tr>

</thead>

<tbody>

{table_rows}

</tbody>

</table>

</div>

"""

    return dashboard_page(content)


# =========================================================
# مدیریت و کارکنان
# =========================================================

@app.route("/management")
def management():

    if not check_login():
        return redirect("/")

    df = load_excel()

    filled = df[
        ~df.apply(is_empty, axis=1)
    ]

    rows = ""

    for _, row in filled.iterrows():

        rows += f"""

        <tr>

        <td>{row["واحد"]}</td>

        <td>{row["بخش/معاونت"]}</td>

        <td>{row["عنوان پست"]}</td>

        <td>{row["نام فرد"]}</td>

        <td>
        <span class="badge badge-green">
        فعال
        </span>
        </td>

        </tr>

        """

    content = f"""

<div class="section">

<div class="section-title">
👥 کارکنان و مدیران دارای پست
</div>

<table>

<thead>

<tr>

<th>واحد</th>
<th>بخش/معاونت</th>
<th>عنوان پست</th>
<th>نام فرد</th>
<th>وضعیت</th>

</tr>

</thead>

<tbody>

{rows}

</tbody>

</table>

</div>

"""

    return dashboard_page(content)


# =========================================================
# پست‌های خالی
# =========================================================

@app.route("/empty")
def empty():

    if not check_login():
        return redirect("/")

    df = load_excel()

    empty_df = df[
        df.apply(is_empty, axis=1)
    ]

    rows = ""

    for _, row in empty_df.iterrows():

        rows += f"""

        <tr>

        <td>{row["واحد"]}</td>

        <td>{row["بخش/معاونت"]}</td>

        <td>{row["عنوان پست"]}</td>

        <td>
        <span class="badge badge-red">
        خالی
        </span>
        </td>

        </tr>

        """

    content = f"""

<div class="section">

<div class="section-title">
⚠️ پست‌های خالی دانشگاه
</div>

<table>

<thead>

<tr>

<th>واحد</th>
<th>بخش/معاونت</th>
<th>عنوان پست</th>
<th>وضعیت</th>

</tr>

</thead>

<tbody>

{rows}

</tbody>

</table>

</div>

"""

    return dashboard_page(content)


# =========================================================
# جستجوی هوشمند
# =========================================================

@app.route("/search")
def search():

    if not check_login():
        return redirect("/")

    q = request.args.get("q", "").strip()

    df = load_excel()

    results = df.iloc[0:0].copy()

    if q:

        mask = df.astype(str).apply(
            lambda row:
            row.str.contains(
                q,
                case=False,
                na=False
            ).any(),
            axis=1
        )

        results = df[mask]

    rows = ""

    for _, row in results.iterrows():

        rows += f"""

        <tr>

        <td>{row["واحد"]}</td>

        <td>{row["بخش/معاونت"]}</td>

        <td>{row["عنوان پست"]}</td>

        <td>{row["نام فرد"]}</td>

        <td>{row["وضعیت"]}</td>

        </tr>

        """

    content = f"""

<div class="section">

<div class="section-title">
🔎 جستجوی هوشمند
</div>

<form method="GET">

<div style="display:flex;gap:10px">

<input
name="q"
value="{q}"
placeholder="نام فرد، واحد، عنوان پست یا معاونت را وارد کنید..."
>

<button class="btn">
جستجو
</button>

</div>

</form>

</div>

<div class="section">

<table>

<thead>

<tr>

<th>واحد</th>
<th>بخش/معاونت</th>
<th>عنوان پست</th>
<th>نام فرد</th>
<th>وضعیت</th>

</tr>

</thead>

<tbody>

{rows}

</tbody>

</table>

</div>

"""

    return dashboard_page(content)


# =========================================================
# چارت سازمانی
# =========================================================

@app.route("/orgchart")
def orgchart():

    if not check_login():
        return redirect("/")

    df = load_excel()

    cards = ""

    for unit in df["واحد"].drop_duplicates():

        unit = str(unit).strip()

        if not unit:
            continue

        unit_df = df[df["واحد"] == unit]

        stats = get_stats(unit_df)

        cards += f"""

        <div class="card">

        <div class="card-title">
        واحد
        </div>

        <div style="font-size:19px;font-weight:bold;color:#063b73">
        {unit}
        </div>

        <hr>

        <p>
        کل پست‌ها:
        <b>{stats["total"]}</b>
        </p>

        <p>
        دارای متصدی:
        <b>{stats["filled"]}</b>
        </p>

        <p>
        پست خالی:
        <b>{stats["empty"]}</b>
        </p>

        <div class="progress">

        <div class="progress-bar"
             style="width:{stats["percent"]}%">
        </div>

        </div>

        <p>
        تکمیل ساختار: {stats["percent"]}%
        </p>

        </div>

        """

    content = f"""

<div class="section">

<div class="section-title">
🌐 نمای کلی چارت سازمانی
</div>

<div class="cards">

{cards}

</div>

</div>

"""

    return dashboard_page(content)


# =========================================================
# خروجی Excel
# =========================================================

@app.route("/export")
def export():

    if not check_login():
        return redirect("/")

    df = load_excel()

    output_file = os.path.join(
        BASE_DIR,
        "گزارش_ساختار_دانشگاه.xlsx"
    )

    df.to_excel(
        output_file,
        index=False
    )

    return send_from_directory(
        BASE_DIR,
        "گزارش_ساختار_دانشگاه.xlsx",
        as_attachment=True
    )


# =========================================================
# لوگو
# =========================================================

@app.route("/logo.png")
def logo():

    return send_from_directory(
        STATIC_DIR,
        "logo.png"
    )


# =========================================================
# اجرای سامانه
# =========================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )