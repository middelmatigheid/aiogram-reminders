from aiogram.types import ReplyKeyboardMarkup
import calendar


main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add('Создать напоминалку').add('Мои напоминалки').add('Сменить часовой пояс')


menu = ReplyKeyboardMarkup(resize_keyboard=True)
menu.add('Главное меню')


date = ReplyKeyboardMarkup(resize_keyboard=True)
date.add('Определенная дата и время').add('Каждые n дней').add('Каждые n часов').add('Каждые n минут').add('Главное меню')


select_year = ReplyKeyboardMarkup(resize_keyboard=True)
select_year.add('Этот год').add('Следующий год').add('Главное меню')


select_month = ReplyKeyboardMarkup(resize_keyboard=True)
select_month.row('1', '2', '3', '4')
select_month.row('5', '6', '7', '8')
select_month.row('9', '10', '11', '12')
select_month.add('Главное меню')


def select_day(year, month):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    if calendar.monthrange(year, month)[1] == 28:
        markup.row('1', '2', '3', '4', '5', '6', '7')
        markup.row('8', '9', '10', '11', '12', '13', '14')
        markup.row('15', '16', '17', '18', '19', '20', '21')
        markup.row('22', '23', '24', '25', '26', '27', '28')
    elif calendar.monthrange(year, month)[1] == 29:
        markup.row('1', '2', '3', '4', '5', '6')
        markup.row('7', '8', '9', '10', '11', '12')
        markup.row('13', '14', '15', '16', '17', '18')
        markup.row('19', '20', '21', '22', '23', '24')
        markup.row('25', '26', '27', '28', '29')
    elif calendar.monthrange(year, month)[1] == 30:
        markup.row('1', '2', '3', '4', '5', '6')
        markup.row('7', '8', '9', '10', '11', '12')
        markup.row('13', '14', '15', '16', '17', '18')
        markup.row('19', '20', '21', '22', '23', '24')
        markup.row('25', '26', '27', '28', '29', '30')
    else:
        markup.row('1', '2', '3', '4', '5', '6')
        markup.row('7', '8', '9', '10', '11', '12')
        markup.row('13', '14', '15', '16', '17', '18')
        markup.row('19', '20', '21', '22', '23', '24')
        markup.row('25', '26', '27', '28', '29', '30', '31')
    markup.add('Главное меню')
    return markup


my_reminders = ReplyKeyboardMarkup(resize_keyboard=True)
my_reminders.add('Удалить напоминалку').add('Главное меню')


delete_reminder = ReplyKeyboardMarkup(resize_keyboard=True)
delete_reminder.add('Да').add('Нет')


def reminders(reminders_num):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(0, reminders_num - 2, 3):
        markup.row(str(i + 1), str(i + 2), str(i + 3))
    if reminders_num % 3 == 1:
        num = reminders_num // 3 * 3
        markup.row(str(num + 1))
    elif reminders_num % 3 == 2:
        num = reminders_num // 3 * 3
        markup.row(str(num + 1), str(num + 2))
    markup.add('Удалить все напоминалки')
    markup.add('Главное меню')
    return markup
