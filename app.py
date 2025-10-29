from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3, qrcode, os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'ticktify_secret'
DB = 'database.db'

# ---------- DATABASE SETUP ----------
def init_db():
    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        email TEXT UNIQUE,
                        password TEXT)''')

        cur.execute('''CREATE TABLE IF NOT EXISTS tickets (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_email TEXT,
                        event_name TEXT,
                        num_tickets INTEGER,
                        booking_date TEXT,
                        qr_path TEXT)''')
    con.close()

init_db()

# ---------- HOME ----------
@app.route('/')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('home.html', user=session['user'])

# ---------- SIGNUP ----------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        with sqlite3.connect(DB) as con:
            cur = con.cursor()
            try:
                cur.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", 
                            (name, email, password))
                con.commit()
                flash("Signup successful! Please login.")
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                flash("Email already exists. Please login.")
    return render_template('signup.html')

# ---------- LOGIN ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        with sqlite3.connect(DB) as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
            user = cur.fetchone()
            if user:
                session['user'] = email
                return redirect(url_for('home'))
            else:
                flash("Invalid credentials. Try again.")
    return render_template('login.html')

# ---------- LOGOUT ----------
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("You have logged out successfully.")
    return redirect(url_for('login'))

# ---------- BOOK TICKET ----------
@app.route('/book', methods=['GET', 'POST'])
def book_ticket():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        event_name = request.form['event_name']
        num_tickets = request.form['num_tickets']
        email = session['user']
        booking_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Generate QR Code
        qr_data = f"User: {email}\nEvent: {event_name}\nTickets: {num_tickets}\nDate: {booking_date}"
        qr_img = qrcode.make(qr_data)

        qr_folder = 'static/qr_codes'
        if not os.path.exists(qr_folder):
            os.makedirs(qr_folder)

        qr_filename = f"{secure_filename(email)}_{datetime.now().timestamp()}.png"
        qr_full_path = os.path.join(qr_folder, qr_filename)
        qr_img.save(qr_full_path)

        # Store relative path for Flask to serve
        relative_qr_path = f"qr_codes/{qr_filename}"

        with sqlite3.connect(DB) as con:
            cur = con.cursor()
            cur.execute("""INSERT INTO tickets 
                           (user_email, event_name, num_tickets, booking_date, qr_path) 
                           VALUES (?, ?, ?, ?, ?)""",
                        (email, event_name, num_tickets, booking_date, relative_qr_path))
            con.commit()

        flash("Ticket booked successfully!")
        return render_template('qr_page.html', qr_path=relative_qr_path, event=event_name, tickets=num_tickets)
    return render_template('book_ticket.html')

# ---------- HISTORY ----------
@app.route('/history')
def history():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    email = session['user']
    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM tickets WHERE user_email=?", (email,))
        bookings = cur.fetchall()

    return render_template('history.html', bookings=bookings)

# ---------- RUN ----------
if __name__ == '__main__':
    app.run(debug=True)
