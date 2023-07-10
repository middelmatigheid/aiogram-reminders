import sqlite3 as sq


db = sq.connect('reminders.db')
cursor = db.cursor()


async def delete_tables():
    print('DATABASE: ARE YOU SURE YOU WANT TO DELETE TABLES users, reminders')
    if input('WRITE Y/N: ') == 'Y':
        cursor.execute("DROP TABLE IF EXISTS users")
        cursor.execute("DROP TABLE IF EXISTS reminders")
        db.commit()


async def create_tables():
    cursor.execute("CREATE TABLE IF NOT EXISTS users("
                    "user_id INTEGER PRIMARY KEY, "
                    "step VARCHAR(35), "
                    "timezone INTEGER, "
                    "reminder_id INTEGER, "
                    "is_on INTEGER)")
    cursor.execute("CREATE TABLE IF NOT EXISTS reminders("
                    "reminder_id INTEGER PRIMARY KEY AUTOINCREMENT, "
                    "user_id INTEGER, "
                    "text VARCHAR(100), "
                    "date VARCHAR(20), "
                    "sleep_time INTEGER, "
                    "once INTEGER)")
    db.commit()


async def add_new_user(user_id, step):
    cursor.execute(f"INSERT INTO users (user_id, step, timezone, reminder_id, is_on) VALUES ({user_id}, '{step}', 0, -1, 1)")
    db.commit()


async def update_user_step(user_id, step):
    cursor.execute(f"UPDATE users SET step = '{step}' WHERE user_id == {user_id}")
    db.commit()


async def update_user_timezone(user_id, timezone, is_new):
    if is_new:
        cursor.execute(f"UPDATE users SET timezone = {timezone} WHERE user_id == {user_id}")
    else:
        prev_timezone = cursor.execute(f"SELECT timezone FROM users WHERE user_id == {user_id}").fetchone()[0]
        cursor.execute(f"UPDATE users SET timezone = {timezone} WHERE user_id == {user_id}")
        reminders_id = cursor.execute(f"SELECT reminder_id FROM reminders WHERE once == 1").fetchall()
        for reminder_id in reminders_id:
            reminder = cursor.execute(f"SELECT date FROM reminders WHERE reminder_id == {reminder_id[0]}").fetchone()[0]
            date = reminder[:11] + str(int(reminder[11:13]) - (prev_timezone - timezone)) + reminder[13:]
            cursor.execute(f"UPDATE reminders SET date = '{date}' WHERE reminder_id == {reminder_id[0]}")
    db.commit()


async def update_user_reminder_id(user_id, reminder_id):
    cursor.execute(f"UPDATE users SET reminder_id = {reminder_id} WHERE user_id == {user_id}")
    db.commit()


async def add_new_reminder(user_id, text):
    cursor.execute(f"INSERT INTO reminders (user_id, text, date, sleep_time, once) VALUES ({user_id}, '{text}', 'None', 0, 0)")
    reminder_id = cursor.execute(f"SELECT MAX(reminder_id) FROM reminders WHERE user_id == {user_id}").fetchone()[0]
    cursor.execute(f"UPDATE users SET reminder_id == {reminder_id} WHERE user_id == {user_id}")
    db.commit()


async def update_reminder_date(reminder_id, date):
    cursor.execute(f"UPDATE reminders SET date = '{date}' WHERE reminder_id == {reminder_id}")
    db.commit()


async def update_reminder_sleep_time(reminder_id, sleep_time):
    cursor.execute(f"UPDATE reminders SET sleep_time = {sleep_time} WHERE reminder_id == {reminder_id}")
    db.commit()


async def update_reminder_once(reminder_id, once):
    cursor.execute(f"UPDATE reminders SET once = {once} WHERE reminder_id == {reminder_id}")
    db.commit()


async def update_user_is_on(user_id, is_on):
    cursor.execute(f"UPDATE users SET is_on == {is_on} WHERE user_id == {user_id}")
    db.commit()


async def get_user_by_id(user_id):
    user = cursor.execute(f"SELECT * FROM users WHERE user_id == {user_id}").fetchone()
    if user is None:
        return None
    res = {'user_id': None, 'step': None, 'timezone': None, 'reminder_id': None, 'is_on': None}
    res_keys = ['user_id', 'step', 'timezone', 'reminder_id', 'is_on']
    for i in range(len(user)):
        res[res_keys[i]] = user[i]
    return res


async def get_reminder_by_id(reminder_id):
    reminder = cursor.execute(f"SELECT * FROM reminders WHERE reminder_id == {reminder_id}").fetchone()
    if reminder is None:
        return None
    res = {'reminder_id': None, 'user_id': None, 'text': None, 'date': None, 'sleep_time': None, 'once': None}
    res_keys = ['reminder_id', 'user_id', 'text', 'date', 'sleep_time', 'once']
    for i in range(len(reminder)):
        res[res_keys[i]] = reminder[i]
    return res


async def get_all_users_reminders(user_id):
    reminders = cursor.execute(f"SELECT reminder_id, text, date, sleep_time, once FROM reminders WHERE user_id == {user_id}").fetchall()
    res = []
    for reminder in reminders:
        res.append({"reminder_id": reminder[0], "text": reminder[1], "date": reminder[2], "sleep_time": reminder[3], "once": reminder[4]})
    return res


async def delete_reminder(reminder_id):
    cursor.execute(f"DELETE FROM reminders WHERE reminder_id == {reminder_id}")
    db.commit()


async def delete_all_reminders(user_id):
    cursor.execute(f"DELETE FROM reminders WHERE user_id == {user_id}")
    db.commit()
