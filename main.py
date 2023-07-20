from aiogram import Bot, Dispatcher, executor, types
import asyncio
import datetime
import calendar
import keyboards as kb
import database as db


bot = Bot('BOT_TOKEN')
dp = Dispatcher(bot)


async def on_startup(_):
    await db.delete_tables()
    await db.create_tables()


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer(f'Привет, {message.chat.first_name}, это бот-напоминалка, выбери действие, чтобы продолжить',
                         reply_markup=kb.main_menu)


async def set_reminder(message, reminder_id):
    reminder = await db.get_reminder_by_id(reminder_id)
    while True:
        await asyncio.sleep(reminder['sleep_time'])
        reminder = await db.get_reminder_by_id(reminder_id)
        if reminder['is_deleted'] == 1:
            await db.delete_reminder(reminder_id)
            return
        await message.answer(f'Напоминалка!\n{reminder["text"]}')
        if reminder['once'] == 1:
            return


@dp.message_handler()
async def cmd_text(message: types.Message):
    user = await db.get_user_by_id(message.chat.id)
    reminder = None

    if user is not None:
        reminder = await db.get_reminder_by_id(user['reminder_id'])

    if message.text == 'Главное меню':
        await message.answer('Выбери действие, чтобы продолжить', reply_markup=kb.main_menu)

    elif message.text == 'Создать напоминалку':
        user = await db.get_user_by_id(message.chat.id)
        if user is None:
            await db.add_new_user(message.chat.id, 'add_new_user')
            await message.answer('Для корректной работы бота, напиши время в своем часовом поясе в формате ЧЧ:ММ',
                                 reply_markup=kb.menu)
        else:
            await db.update_user_step(message.chat.id, 'set_reminder_text')
            await message.answer('Напиши напоминалку длиной до 100 символов', reply_markup=kb.menu)

    elif user is not None and user['step'] == 'add_new_user':
        if len(message.text) == 5 and message.text[:2].isdigit() and message.text[2] == ':' and  \
                message.text[3:].isdigit() and 24 > int(message.text[:2]) >= 0 and 60 > int(message.text[3:]) >= 0:
            time_now = int(datetime.datetime.now(datetime.timezone.utc).hour)
            await db.update_user_timezone(message.chat.id, int(message.text[:2]) - time_now, True)
            await db.update_user_step(message.chat.id, 'set_reminder_text')
            await message.answer('Напиши напоминалку длиной до 100 символов', reply_markup=kb.menu)
        else:
            await message.answer('Некорректное время, попробуй снова', reply_markup=kb.menu)

    elif user is not None and user['step'] == 'set_reminder_text':
        if len(message.text) > 100:
            await message.answer(f'Напоминалка слишком длинная: {len(message.text)}/100, попробуй еще раз',
                                 reply_markup=kb.menu)
        else:
            await db.update_user_step(message.chat.id, 'set_reminder_date')
            await db.add_new_reminder(message.chat.id, message.text)
            await message.answer('Выбери формат даты напоминалки', reply_markup=kb.date)

    elif user is not None and user['step'] == 'set_reminder_date' and message.text == 'Определенная дата и время':
        await db.update_user_step(message.chat.id, 'set_reminder_date_select_year')
        await message.answer('Напиши год напоминалки', reply_markup=kb.select_year)

    elif user is not None and user['step'] == 'set_reminder_date_select_year':
        if message.text == 'Этот год':
            date = str(datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=user['timezone']))).year) + '-'
            await db.update_reminder_date(user['reminder_id'], date)
            await db.update_user_step(message.chat.id, 'set_reminder_date_select_month')
            await message.answer('Напиши номер месяца напоминалки', reply_markup=kb.select_month)
        elif message.text == 'Следующий год':
            date = int(datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=user['timezone']))).year)
            await db.update_reminder_date(user['reminder_id'], str(date + 1) + '-')
            await db.update_user_step(message.chat.id, 'set_reminder_date_select_month')
            await message.answer('Напиши номер месяца напоминалки', reply_markup=kb.select_month)
        elif not message.text.isdigit():
            await message.answer('Введи год цифрами или выбери один из предложенных ниже', reply_markup=kb.select_year)
        elif int(message.text) < int(datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=user['timezone']))).year):
            await message.answer('Некорректный год, попробуй снова', reply_markup=kb.select_year)
        else:
            await db.update_reminder_date(user['reminder_id'], message.text + '-')
            await db.update_user_step(message.chat.id, 'set_reminder_date_select_month')
            await message.answer('Напиши номер месяца напоминалки', reply_markup=kb.select_month)

    elif user is not None and user['step'] == 'set_reminder_date_select_month':
        if not message.text.isdigit():
            await message.answer('Введи месяц цифрами', reply_markup=kb.select_month)
        elif int(message.text) > 12 or int(message.text) < 1 or (reminder['date'] == str(datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=user['timezone']))).year) + ' ' and
                int(message.text) < int(datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=user['timezone']))).month)):
            await message.answer('Некорректный номер месяца, попробуй снова', reply_markup=kb.select_month)
        else:
            await db.update_user_step(message.chat.id, 'set_reminder_date_select_day')
            reminder_date = ''
            if len(message.text) == 1:
                reminder_date += '0'
            reminder_date += message.text + '-'
            await db.update_reminder_date(user['reminder_id'], reminder['date'] + reminder_date)
            await message.answer('Напиши день месяца напоминалки', reply_markup=kb.select_day(int(reminder['date'][:4]),
                                                                                              int(reminder_date[:2])))

    elif user is not None and user['step'] == 'set_reminder_date_select_day':
        if not message.text.isdigit():
            await message.answer('Введи день месяца цифрами', reply_markup=kb.select_day(int(reminder['date'][:4]),
                                                                                         int(reminder['date'][5:7])))
        elif int(message.text) > calendar.monthrange(int(reminder['date'][:4]), int(reminder['date'][5:7]))[1] or \
                int(message.text) < 1 or (int(reminder['date'][:4]) == int(datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=user['timezone']))).year) and
                int(reminder['date'][5:7]) == int(datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=user['timezone']))).month) and
                int(message.text) < int(datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=user['timezone']))).day)):
            await message.answer('Некорректный день месяца, попробуй снова', reply_markup=kb.select_day(int(reminder['date'][:4]), int(reminder['date'][5:7])))
        else:
            await db.update_user_step(message.chat.id, 'set_reminder_date_select_time')
            reminder_date = ''
            if len(message.text) == 1:
                reminder_date += '0'
            reminder_date += message.text + ' '
            await db.update_reminder_date(user['reminder_id'], reminder['date'] + reminder_date)
            await message.answer('Напиши время в формате чч:мм', reply_markup=kb.menu)

    elif user is not None and user['step'] == 'set_reminder_date_select_time':
        if len(message.text) != 5 or not message.text[:2].isdigit() or not message.text[3:5].isdigit() or \
            int(message.text[:2]) > 23 or int(message.text[:2]) < 0 or int(message.text[3:5]) > 59 or \
                int(message.text[3:5]) < 0:
            await message.answer('Некорректное время, попробуй снова', reply_markup=kb.menu)
        else:
            reminder_date = reminder['date'] + message.text
            reminder_time = (datetime.datetime.strptime(reminder_date, '%Y-%m-%d %H:%M').replace(
                tzinfo=datetime.timezone(datetime.timedelta(hours=user['timezone']))))
            time_now = datetime.datetime.now(datetime.timezone.utc).replace(
                tzinfo=datetime.timezone(datetime.timedelta(hours=user['timezone'], seconds=0)))
            sleep_time = round((reminder_time - time_now).total_seconds())
            if sleep_time < 0:
                await message.answer('Некорректное время, попробуй снова', reply_markup=kb.menu)
            else:
                await db.update_reminder_date(user['reminder_id'], reminder_date)
                await db.update_reminder_sleep_time(user['reminder_id'], sleep_time)
                await db.update_reminder_once(user['reminder_id'], 1)
                await db.update_user_step(message.chat.id, 'None')
                await db.update_user_reminder_id(message.chat.id, -1)
                await message.answer('Напоминалка успешно добавлена', reply_markup=kb.main_menu)
                await set_reminder(message, user['reminder_id'])

    elif user is not None and user['step'] == 'set_reminder_date' and message.text == 'Каждые n дней':
        await db.update_user_step(message.chat.id, 'set_reminder_date_every_n_days')
        await message.answer('Напиши количество дней, через которые нужно напоминать', reply_markup=kb.menu)

    elif user is not None and user['step'] == 'set_reminder_date_every_n_days':
        if not message.text.isdigit():
            await message.answer('Напиши количество цифрами', reply_markup=kb.menu)
        elif int(message.text.isdigit()) <= 0:
            await message.answer('Некорректное количество дней, попробуй снова', reply_markup=kb.menu)
        else:
            if int(message.text) % 10 == 1 and int(message.text) % 100 != 11:
                reminder_date = 'Каждый '
            else:
                reminder_date = 'Каждые '
            reminder_date += message.text
            if int(message.text) % 10 == 1 and int(message.text) % 100 != 11:
                reminder_date +=' день'
            elif int(message.text) % 10 in [2, 3, 4] and int(message.text) % 100 not in [12, 13, 14]:
                reminder_date += ' дня'
            else:
                reminder_date += ' дней'
            if len(reminder_date) > 20:
                await db.update_user_step(message.chat.id, 'set_reminder_date')
                await message.answer('Ждать придется слишком долго, попробуй снова',
                                     reply_markup=kb.date)
            sleep_time = int(message.text) * 24 * 60 * 60
            await db.update_reminder_date(user['reminder_id'], reminder_date)
            await db.update_reminder_sleep_time(user['reminder_id'], sleep_time)
            await db.update_reminder_once(user['reminder_id'], 0)
            await db.update_user_step(message.chat.id, 'None')
            await db.update_user_reminder_id(message.chat.id, -1)
            await message.answer('Напоминалка успешно добавлена', reply_markup=kb.main_menu)
            await set_reminder(message, user['reminder_id'])

    elif user is not None and user['step'] == 'set_reminder_date' and message.text == 'Каждые n часов':
        await db.update_user_step(message.chat.id, 'set_reminder_date_every_n_hours')
        await message.answer('Напиши количество часов, через которые нужно напоминать', reply_markup=kb.menu)

    elif user is not None and user['step'] == 'set_reminder_date_every_n_hours':
        if not message.text.isdigit():
            await message.answer('Напиши количество цифрами', reply_markup=kb.menu)
        elif int(message.text.isdigit()) <= 0:
            await message.answer(
                'Некорректное количество часов, попробуй снова', reply_markup=kb.menu)
        else:
            if int(message.text) % 10 == 1 and int(message.text) % 100 != 11:
                reminder_date = 'Каждый '
            else:
                reminder_date = 'Каждые '
            reminder_date += message.text
            if int(message.text) % 10 == 1 and int(message.text) % 100 != 11:
                reminder_date +=' час'
            elif int(message.text) % 10 in [2, 3, 4] and int(message.text) % 100 not in [12, 13, 14]:
                reminder_date +=' часа'
            else:
                reminder_date += ' часов'
            if len(reminder_date) > 20:
                await db.update_user_step(message.chat.id, 'set_reminder_date')
                await message.answer('Ждать придется слишком долго, попробуй снова',
                                     reply_markup=kb.date)
            sleep_time = int(message.text) * 60 * 60
            await db.update_reminder_date(user['reminder_id'], reminder_date)
            await db.update_reminder_sleep_time(user['reminder_id'], sleep_time)
            await db.update_reminder_once(user['reminder_id'], 0)
            await db.update_user_step(message.chat.id, 'None')
            await db.update_user_reminder_id(message.chat.id, -1)
            await message.answer('Напоминалка успешно добавлена', reply_markup=kb.main_menu)
            await set_reminder(message, user['reminder_id'])

    elif user is not None and user['step'] == 'set_reminder_date' and message.text == 'Каждые n минут':
        await db.update_user_step(message.chat.id, 'set_reminder_date_every_n_minutes')
        await message.answer('Напиши количество минут, через которые нужно напоминать', reply_markup=kb.menu)

    elif user is not None and user['step'] == 'set_reminder_date_every_n_minutes':
        if not message.text.isdigit():
            await message.answer('Напиши количество цифрами', reply_markup=kb.menu)
        elif int(message.text.isdigit()) <= 0:
            await message.answer(
                'Некорректное количество минут, попробуй снова', reply_markup=kb.menu)
        else:
            if int(message.text) % 10 == 1 and int(message.text) % 100 != 11:
                reminder_date = 'Каждую '
            else:
                reminder_date = 'Каждые '
            reminder_date += message.text
            if int(message.text) % 10 == 1 and int(message.text) % 100 != 11:
                reminder_date += ' минуту'
            elif int(message.text) % 10 in [2, 3, 4] and int(message.text) % 100 not in [12, 13, 14]:
                reminder_date += ' минуты'
            else:
                reminder_date += ' минут'
            if len(reminder_date) > 20:
                await db.update_user_step(message.chat.id, 'set_reminder_date')
                await message.answer('Ждать придется слишком долго, попробуй снова',
                                     reply_markup=kb.date)
            else:
                sleep_time = int(message.text) * 60
                await db.update_reminder_date(user['reminder_id'], reminder_date)
                await db.update_reminder_sleep_time(user['reminder_id'], sleep_time)
                await db.update_reminder_once(user['reminder_id'], 0)
                await db.update_user_step(message.chat.id, 'None')
                await db.update_user_reminder_id(message.chat.id, -1)
                await message.answer('Напоминалка успешно добавлена', reply_markup=kb.main_menu)
                await set_reminder(message, user['reminder_id'])

    elif message.text == 'Мои напоминалки':
        reminders = await db.get_all_users_reminders(message.chat.id)
        if len(reminders) != 0:
            text = 'Твои напоминалки:\n\n'
            for i in range(len(reminders)):
                text += f'{i + 1}. {reminders[i]["text"]}\n{reminders[i]["date"]}\n\n'
            text += 'Выбери действие, чтобы продолжить'
            await db.update_user_step(message.chat.id, 'my_reminders')
            await message.answer(text, reply_markup=kb.my_reminders)
        else:
            await message.answer('У тебе еще нет напоминалок, ты можешь добавить их в меню', reply_markup=kb.menu)

    elif user is not None and user['step'] == 'my_reminders' and message.text == 'Удалить напоминалку':
        await db.update_user_step(message.chat.id, 'delete_reminder')
        reminders = await db.get_all_users_reminders(message.chat.id)
        await message.answer('Введи номер напоминалки, которую ты хочешь удалить', reply_markup=kb.reminders(len(reminders)))

    elif user is not None and user['step'] == 'delete_reminder':
        reminders = await db.get_all_users_reminders(message.chat.id)
        if message.text.isdigit() and 1 <= int(message.text) <= len(reminders):
            await db.update_user_step(message.chat.id, 'sure_to_delete_reminder')
            await db.update_user_reminder_id(message.chat.id, int(message.text))
            await message.answer(f'Вы уверены, что хотите удалить напоминалку\n\n{reminders[int(message.text) - 1]["text"]}\n{reminders[int(message.text) - 1]["date"]}',
                                 reply_markup=kb.delete_reminder)
        elif message.text == 'Удалить все напоминалки':
            await db.update_user_step(message.chat.id, 'sure_to_delete_all_reminders')
            await message.answer('Вы уверены, что хотите удалить все напоминалки', reply_markup=kb.delete_reminder)
        else:
            await message.answer('Некорректный номер, попробуйте снова')

    elif user is not None and user['step'] == 'sure_to_delete_reminder':
        if message.text == 'Да':
            await db.update_reminder_is_deleted(user['reminder_id'])
            await db.update_user_step(message.chat.id, 'None')
            await db.update_user_reminder_id(message.chat.id, -1)
            await message.answer('Напоминалка успешно удалена', reply_markup=kb.my_reminders)
        elif message.text == 'Нет':
            await db.update_user_step(message.chat.id, 'None')
            await db.update_user_reminder_id(message.chat.id, -1)
            await message.answer('Выбери действие, чтобы продолжить', reply_markup=kb.menu)

    elif user is not None and user['step'] == 'sure_to_delete_all_reminders':
        if message.text == 'Да':
            await db.update_all_reminders_is_deleted(message.chat.id)
            await db.update_user_step(message.chat.id, 'None')
            await db.update_user_reminder_id(message.chat.id, -1)
            await message.answer('Напоминалки успешно удалены', reply_markup=kb.my_reminders)
        elif message.text == 'Нет':
            await db.update_user_step(message.chat.id, 'None')
            await db.update_user_reminder_id(message.chat.id, -1)
            await message.answer('Выбери действие, чтобы продолжить', reply_markup=kb.menu)

    elif message.text == 'Сменить часовой пояс':
        if user is None:
            await message.answer('У тебе еще нет установленного часового пояса, ты можешь сделать это, добавив свою первую напоминалку',
                                 reply_markup=kb.menu)
        else:
            await db.update_user_step(message.chat.id, 'update_user_timezone')
            await message.answer('Напиши время в своем часовом поясе в формате ЧЧ:ММ')

    elif user is not None and user['step'] == 'update_user_timezone':
        if len(message.text) == 5 and message.text[:2].isdigit() and message.text[2] == ':' and \
                message.text[3:].isdigit() and 24 > int(message.text[:2]) >= 0 and 60 > int(message.text[3:]) >= 0:
            timezone = int(message.text[:2]) - int(datetime.datetime.now(datetime.timezone.utc).hour)
            await db.update_user_timezone(message.chat.id, timezone, 0)
            await db.update_user_step(message.chat.id, 'None')
            await db.update_user_reminder_id(message.chat.id, -1)
            await message.answer('Часовой пояс успешно сменен', reply_markup=kb.main_menu)
        else:
            await message.answer('Некорректное время, попробуй снова', reply_markup=kb.menu)

    else:
        await message.answer('Неизвестная команда, попробуй снова', reply_markup=kb.main_menu)


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
