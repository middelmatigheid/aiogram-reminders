# aiogram-randombot

<div style="display: flex; gap: 25px; justify-content: center;">
    <img src="screenshots/screenshot_1.jpg" style="width: 250px;" alt="bot screenshot">
    <img src="screenshots/screenshot_2.jpg" style="width: 250px;" alt="bot screenshot">
    <img src="screenshots/screenshot_3.jpg" style="width: 250px;" alt="bot screenshot">
</div>

# About the project

Telegram bot that can remind you anytime about anything, just as simply as it is

# Main functions

- Creating and deleting reminders
- Reminding you

# Used in project

- Python 3.8+
- Aiogram - for operating the telegram bot
- Psycopg2 (PostgreSQL) - for operating the database

# Downloading and running the bot

### 1. Download [Python](https://www.python.org/) and IDE

You can use any IDE you want, for example: PyCharm, VSCode, Python IDLE, etc.

### 2. Download ZIP or use git clone

```bash
git clone https://github.com/middelmatigheid/aiogram-reminders.git
cd aiogram-reminders
```

### 3. Create virtual environment

If you are using Linux/MacOS

```bash
python -m venv venv
source venv/bin/activate
```

If you are using Windows

```bash
python -m venv venv
venv\Scripts\activate 
```

### 4. Install requirements

```bash
pip install -r requirements.txt
```

### 5. Set up the database

- Download [PostgreSQL](https://www.postgresql.org/)
- Configure the database in pgAdmin4

### 6. Create a telegram bot

Create a telegram bot using [@BotFather](https://telegram.me/BotFather)

### 7. Create .env file

Create .env file in the main directory and set up the values

```bash
BOT_TOKEN='YOUR BOT TOKEN'
HOST='YOUR HOST'
DBNAME='YOUR DBNAME'
USER='YOUR USERNAME'
PASSWORD='YOUR PASSWORD'
PORT=YOUR PORT
```

### 8. Run the bot

```bash
python main.py
```

# Project structure

```bash
aiogram-reminders/
├── main.py               # Main file to run the bot
├── app/
│   ├── handlers.py       # File for handling bot's requests
│   └── database.py       # File for operating the database
├── requirements.txt      # Python requirements
└── .env                  # Environment variables
```
