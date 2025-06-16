import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

# Connecting to database
HOST = os.getenv('HOST')
DBNAME = os.getenv('DBNAME')
USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')
PORT = os.getenv('PORT')
connection = psycopg2.connect(host=HOST, dbname=DBNAME, user=USER, password=PASSWORD, port=PORT)


# Deleting all the tables
async def delete_tables():
    with connection.cursor() as cursor:
        print('DATABASE: ARE YOU SURE YOU WANT TO DELETE TABLES users, reminders')
        if input('WRITE Y/N: ') == 'Y':
            cursor.execute("DROP TABLE IF EXISTS users")
            cursor.execute("DROP TABLE IF EXISTS reminders")
            connection.commit()


# Creating tables in tha database
async def create_tables():
    with connection.cursor() as cursor:
        cursor.execute("CREATE TABLE IF NOT EXISTS users("
                        "user_id INTEGER PRIMARY KEY, "
                        "step VARCHAR(35), "
                        "timezone INTEGER, "
                        "reminder_id INTEGER);")
        cursor.execute("CREATE TABLE IF NOT EXISTS reminders("
                        "reminder_id SERIAL PRIMARY KEY, "
                        "user_id INTEGER, "
                        "text VARCHAR(100), "
                        "date VARCHAR(20), "
                        "sleep_time INTEGER, "
                        "once INTEGER, "
                        "is_deleted INTEGER);")
        connection.commit()


# Adding new user to the database
async def add_new_user(user_id):
    with connection.cursor() as cursor:
        cursor.execute(f"INSERT INTO users (user_id, step, timezone, reminder_id) VALUES ({user_id}, '', -1000, -1);")
        connection.commit()


# Updating user's step
async def update_user_step(user_id, step):
    with connection.cursor() as cursor:
        cursor.execute(f"UPDATE users SET step = '{step}' WHERE user_id = {user_id};")
        connection.commit()


# Updating user's timezone
async def update_user_timezone(user_id, timezone, is_new):
    with (connection.cursor() as cursor):
        if is_new:
            cursor.execute(f"UPDATE users SET timezone = {timezone} WHERE user_id = {user_id};")
        else:
            cursor.execute(f"SELECT timezone FROM users WHERE user_id = {user_id};")
            prev_timezone = cursor.fetchone()[0]
            cursor.execute(f"UPDATE users SET timezone = {timezone} WHERE user_id = {user_id};")
            cursor.execute(f"SELECT reminder_id FROM reminders WHERE once = 1;")
            reminders_id = cursor.fetchall()
            for reminder_id in reminders_id:
                cursor.execute(f"SELECT date FROM reminders WHERE reminder_id = {reminder_id[0]};")
                reminder = cursor.fetchone()[0]
                date = reminder[:11] + str(int(reminder[11:13]) - (prev_timezone - timezone)) + reminder[13:]
                cursor.execute(f"UPDATE reminders SET date = '{date}' WHERE reminder_id = {reminder_id[0]};")
        connection.commit()


# Updating user's reminder id
async def update_user_reminder_id(user_id, reminder_id):
    with connection.cursor() as cursor:
        cursor.execute(f"UPDATE users SET reminder_id = {reminder_id} WHERE user_id = {user_id};")
        connection.commit()


# Adding new reminder's to tha database
async def add_new_reminder(user_id, text):
    with connection.cursor() as cursor:
        cursor.execute(f"INSERT INTO reminders (user_id, text, date, sleep_time, once, is_deleted) VALUES ({user_id}, '{text}', 'None', 0, 0, 0);")
        cursor.execute(f"SELECT MAX(reminder_id) FROM reminders WHERE user_id = {user_id};")
        reminder_id = cursor.fetchone()[0]
        cursor.execute(f"UPDATE users SET reminder_id = {reminder_id} WHERE user_id = {user_id};")
        connection.commit()


# Updating reminder's date
async def update_reminder_date(reminder_id, date):
    with connection.cursor() as cursor:
        cursor.execute(f"UPDATE reminders SET date = '{date}' WHERE reminder_id = {reminder_id};")
        connection.commit()


# Updating reminder's sleep time
async def update_reminder_sleep_time(reminder_id, sleep_time):
    with connection.cursor() as cursor:
        cursor.execute(f"UPDATE reminders SET sleep_time = {sleep_time} WHERE reminder_id = {reminder_id};")
        connection.commit()


# Updating reminder's once condition
async def update_reminder_once(reminder_id, once):
    with connection.cursor() as cursor:
        cursor.execute(f"UPDATE reminders SET once = {once} WHERE reminder_id = {reminder_id};")
        connection.commit()


# Updating reminder's is deleted state
async def update_reminder_is_deleted(reminder_id):
    with connection.cursor() as cursor:
        cursor.execute(f"UPDATE reminders SET is_deleted = 1 WHERE reminder_id = {reminder_id};")
        connection.commit()


# Updating all user's reminder's is deleted state
async def update_all_reminders_is_deleted(user_id):
    with connection.cursor() as cursor:
        cursor.execute(f"UPDATE reminders SET is_deleted = 1 WHERE user_id = {user_id};")
        connection.commit()


# Deleting the reminder
async def delete_reminder(reminder_id):
    with connection.cursor() as cursor:
        cursor.execute(f"DELETE FROM reminders WHERE reminder_id = {reminder_id};")
        connection.commit()


# Getting user's info
async def get_user_by_id(user_id):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM users WHERE user_id = {user_id};")
        user = cursor.fetchone()
        if user is None:
            return None
        res = {}
        res_keys = ['user_id', 'step', 'timezone', 'reminder_id']
        for i in range(len(user)):
            res[res_keys[i]] = user[i]
        return res


# Getting reminder's info
async def get_reminder_by_id(reminder_id):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM reminders WHERE reminder_id = {reminder_id};")
        reminder = cursor.fetchone()
        if reminder is None:
            return None
        res = {}
        res_keys = ['reminder_id', 'user_id', 'text', 'date', 'sleep_time', 'once', 'is_deleted']
        for i in range(len(reminder)):
            res[res_keys[i]] = reminder[i]
        return res


# Getting all user's reminders
async def get_all_users_reminders(user_id):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT reminder_id, text, date, sleep_time, once FROM reminders WHERE user_id = {user_id} AND is_deleted = 0;")
        reminders = cursor.fetchall()
        res = []
        for reminder in reminders:
            res.append({"reminder_id": reminder[0], "text": reminder[1], "date": reminder[2], "sleep_time": reminder[3], "once": reminder[4]})
        return res
