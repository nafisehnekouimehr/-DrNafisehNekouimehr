from flask import Flask, render_template_string
import sqlite3
from datetime import date

app = Flask(__name__)

# --- بخش دیتابیس ---
def init_db():
    """ایجاد دیتابیس و جدول اگر وجود نداشته باشند"""
    conn = sqlite3.connect('stats.db')
    c = conn.cursor()
    # ایجاد جدولی که تاریخ و تعداد بازدید را نگه می‌دارد
    c.execute('''CREATE TABLE IF NOT EXISTS daily_visits 
                 (visit_date TEXT PRIMARY KEY, count INTEGER)''')
    conn.commit()
    conn.close()

def increment_visitor():
    """افزودن یک بازدید به تاریخ امروز"""
    today = str(date.today())
    conn = sqlite3.connect('stats.db')
    c = conn.cursor()
    
    # چک کردن اینکه آیا امروز قبلاً در دیتابیس ثبت شده یا خیر
    c.execute("SELECT count FROM daily_visits WHERE visit_date = ?", (today,))
    result = c.fetchone()
    
    if result:
        # اگر امروز ثبت شده بود، یکی به تعداد اضافه کن
        new_count = result[0] + 1
        c.execute("UPDATE daily_visits SET count = ? WHERE visit_date = ?", (new_count, today))
    else:
        # اگر امروز اولین بازدید است، ردیف جدید بساز
        c.execute("INSERT INTO daily_visits (visit_date, count) VALUES (?, ?)", (today, 1))
    
    conn.commit()
    conn.close()

def get_today_visits():
    """دریافت تعداد بازدیدهای امروز برای نمایش"""
    today = str(date.today())
    conn = sqlite3.connect('stats.db')
    c = conn.cursor()
    c.execute("SELECT count FROM daily_visits WHERE visit_date = ?", (today,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else 0

# --- مسیرهای سایت ---

@app.route('/')
def index():
    # هر بار که صفحه باز می‌شود، یک بازدید ثبت کن
    increment_visitor()
    
    # دریافت تعداد بازدید امروز برای نمایش
    visits = get_today_visits()
    
    # یک قالب HTML ساده برای نمایش
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>سایت من</title>
        <style>
            body { font-family: Tahoma; text-align: center; margin-top: 50px; }
            .counter { font-size: 2em; color: #2c3e50; border: 2px solid #3498db; display: inline-block; padding: 20px; border-radius: 10px; }
        </style>
    </head>
    <body>
        <h1>به سایت من خوش آمدید!</h1>
        <div class="counter">
            تعداد بازدیدهای امروز: {{ visits }}
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template, visits=visits)

if __name__ == '__main__':
    init_db()  # هنگام اجرا دیتابیس را آماده کن
    app.run(debug=True)
