# services/auth_service.py

import sqlite3
import random
import smtplib
from email.message import EmailMessage
import bcrypt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

# --- Email Constants ---
SENDER_EMAIL = "roshanpour.reza@gmail.com"
SENDER_APP_PASSWORD = "hfoq rfhb sioy lpzt" # هشدار: این روش برای محصول نهایی امن نیست

# --- Database Constants ---
DB_FILE = "taram_wallet.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, encrypted_mnemonic TEXT NOT NULL)')
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS tracked_wallets (id INTEGER PRIMARY KEY, user_id INTEGER, blockchain TEXT NOT NULL, address TEXT NOT NULL, FOREIGN KEY (user_id) REFERENCES users (id))')
    conn.commit()
    conn.close()

# --- Email Functions ---
def send_verification_code(recipient_email):
    code = str(random.randint(100000, 999999))
    msg = EmailMessage()
    msg.set_content(f"سلام،\n\nکد تایید شما برای ورود به کیف پول Taram:\n\n{code}")
    msg['Subject'] = 'کد تایید ورود - Taram Wallet'
    msg['From'] = SENDER_EMAIL
    msg['To'] = recipient_email
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"کد تایید با موفقیت به {recipient_email} ارسال شد.")
        return code
    except Exception as e:
        print(f"خطا در ارسال ایمیل: {e}")
        print(f"کد (برای تست): {code}") # بازگرداندن کد در صورت خطا برای تست
        return code

# --- Crypto Functions ---
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

def _derive_key(password, salt):
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=480000)
    return base64.urlsafe_b64encode(kdf.derive(password.encode('utf-8')))

def encrypt_mnemonic(mnemonic, password):
    salt = os.urandom(16)
    key = _derive_key(password, salt)
    f = Fernet(key)
    return salt + f.encrypt(mnemonic.encode('utf-8'))

def decrypt_mnemonic(encrypted_data_with_salt, password):
    try:
        salt = encrypted_data_with_salt[:16]
        encrypted_data = encrypted_data_with_salt[16:]
        key = _derive_key(password, salt)
        f = Fernet(key)
        return f.decrypt(encrypted_data).decode('utf-8')
    except Exception:
        return None

# --- User Database Functions ---
def get_user_by_email(email):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email=?", (email,))
    user_data = cursor.fetchone()
    conn.close()
    if user_data:
        return {'id': user_data[0], 'email': user_data[1], 'password_hash': user_data[2], 'encrypted_mnemonic': user_data[3]}
    return None

def add_new_user(email, password_hash, encrypted_mnemonic):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (email, password_hash, encrypted_mnemonic) VALUES (?, ?, ?)",
                   (email, password_hash, encrypted_mnemonic))
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id

# --- Tracked Wallet Database Functions ---
def add_tracked_wallet(user_id, blockchain, address):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tracked_wallets (user_id, blockchain, address) VALUES (?, ?, ?)",
                   (user_id, blockchain, address))
    conn.commit()
    conn.close()

def get_tracked_wallets(user_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT blockchain, address FROM tracked_wallets WHERE user_id=?", (user_id,))
    wallets = cursor.fetchall()
    conn.close()
    return wallets