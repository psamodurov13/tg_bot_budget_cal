import telebot
import pickle
import finance
from finance import Finance
from telebot import types
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from datetime import date, timedelta

bot = telebot.TeleBot('5502805436:AAF83iukDBx0h4XXaeVLesFduwsxOFbETNw')
# Импортируем типы из модуля, чтобы создавать кнопки


unknown = []
operation_date = ''
new_exe = []
Finance.start()

# Общая кнопка возврата в главное меню
keyboard_to_main = types.InlineKeyboardMarkup()
key_to_main = types.InlineKeyboardButton(text='В главное меню', callback_data='to_main')
keyboard_to_main.add(key_to_main)

# Готовим кнопки главного меню
keyboard_main = types.InlineKeyboardMarkup()
key_budget = types.InlineKeyboardButton(text='Бюджет', callback_data='budget')
keyboard_main.add(key_budget)
key_calendar = types.InlineKeyboardButton(text='Календарь', callback_data='calendar')
keyboard_main.add(key_calendar)

# Готовим кнопки бюджета
keyboard = types.InlineKeyboardMarkup()
key_add_operation = types.InlineKeyboardButton(text='Добавить запись', callback_data='add_operation')
keyboard.add(key_add_operation)
key_show_operations = types.InlineKeyboardButton(text='Посмотреть операции', callback_data='show_operations')
keyboard.add(key_show_operations)
key_show_all_groups = types.InlineKeyboardButton(text='Посмотреть статьи расходов', callback_data='show_all_groups')
keyboard.add(key_show_all_groups)
key_show_group = types.InlineKeyboardButton(text='Посмотреть статью расходов', callback_data='show_group')
keyboard.add(key_show_group)
key_show_all_price = types.InlineKeyboardButton(text='Всего потрачено', callback_data='show_all_price')
keyboard.add(key_show_all_price)

keyboard.add(key_to_main)

# Готовим кнопки перевода расходов в одну валюту
keyboard_convert = types.InlineKeyboardMarkup()
key_convert_to_one = types.InlineKeyboardButton(text='Посчитать в одной валюте', callback_data='convert_to_one')
keyboard_convert.add(key_convert_to_one)
keyboard_convert.add(key_to_main)

# Готовим кнопки выбора даты
keyboard_operation_date = types.InlineKeyboardMarkup()
key_today = types.InlineKeyboardButton(text='Сегодня', callback_data='today')
keyboard_operation_date.add(key_today)
key_yesterday = types.InlineKeyboardButton(text='Вчера', callback_data='yesterday')
keyboard_operation_date.add(key_yesterday)
key_other_date = types.InlineKeyboardButton(text='Другая дата', callback_data='other_date')
keyboard_operation_date.add(key_other_date)

# Готовим кнопки календаря
keyboard_calendar = types.InlineKeyboardMarkup()
keyboard_calendar.add(key_to_main)


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Привет. Я помогу вести книгу учета расходов и заполнять календарь",
                   reply_markup=keyboard_main)



@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    mt = message.text.lower()
    if mt == 'привет':
        bot.send_message(message.from_user.id, 'Привет. Я помогу вести книгу учета расходов и заполнять календарь',
                         reply_markup=keyboard_main)
    elif mt == '/help':
        bot.send_message(message.from_user.id, 'Напиши привет')
    elif mt == 'add_operation':
        bot.send_message(message.from_user.id, 'Введите сумму.')
        bot.register_next_step_handler(message, add_operation_currency)
    else:
        bot.send_message(message.from_user.id, 'Я тебя не  понимаю, напиши /help ')
        unknown.append(message.text)


def add_operation(chat_id):
    message = bot.send_message(chat_id, 'Введите сумму.')
    bot.register_next_step_handler(message, add_operation_currency)


def add_operation_currency(message):
    global new_exe
    new_exe = []
    new_exe.append(int(message.text))
    bot.send_message(message.from_user.id, 'Введите валюту.')
    bot.register_next_step_handler(message, add_operation_name)


def add_operation_name(message):
    new_exe.append(message.text)
    bot.send_message(message.from_user.id, 'Введите товар.')
    bot.register_next_step_handler(message, add_operation_group)


def add_operation_group(message):
    new_exe.append(message.text)
    bot.send_message(message.from_user.id, 'Введите статью расходов.')
    bot.register_next_step_handler(message, add_operation_date)


def add_operation_date(message):
    new_exe.append(message.text)
    bot.send_message(message.from_user.id, 'Когда была совершена операция:', reply_markup=keyboard_operation_date)



def start(chat_id):
    calendar, step = DetailedTelegramCalendar().build()
    bot.send_message(chat_id,
                     f"Выберите {LSTEP[step]}",
                     reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def cal(c):
    result, key, step = DetailedTelegramCalendar().process(c.data)
    if not result and key:
        bot.edit_message_text(f"Выберите {LSTEP[step]}",
                              c.message.chat.id,
                              c.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"Выбрана дата {result}",
                              c.message.chat.id,
                              c.message.message_id)
        global operation_date
        operation_date = result
        new_exe.append(operation_date)
        create_finance(c.message)

def create_finance(message):
    print(new_exe)
    print(type(operation_date))
    bot.send_message(message.chat.id, f'Операция добавлена: {new_exe[0]} {new_exe[1]} - {new_exe[2]}  / '
                                           f'{new_exe[3]} / {new_exe[4]} \n')
    Finance(new_exe[2], new_exe[0], new_exe[1], new_exe[3], new_exe[4])
    with open(finance.expense_book_file, 'wb') as f:
        pickle.dump(Finance.operations, f)
        pickle.dump(Finance.currencies, f)
        pickle.dump(Finance.groups, f)
    # Отправляем текст в Телеграм
    msg = 'Данные сохранены.'
    bot.send_message(message.chat.id, msg)
    budget_menu(message.chat.id)


def budget_menu(chat_id):
    bot.send_message(chat_id, 'Что вы хотите сделать?', reply_markup=keyboard)


# Обработчик нажатий на кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == 'budget':
        budget_menu(call.message.chat.id)

    if call.data == 'calendar':
        bot.send_message(call.message.chat.id, 'Данная функция в разработке', reply_markup=keyboard_to_main)

    if call.data == 'add_operation':
        add_operation(call.message.chat.id)

    # Если нажали на кнопку показать операции
    if call.data == 'show_operations':
        msg = Finance.show_operations()
        # Отправляем текст в Телеграм
        bot.send_message(call.message.chat.id, msg)
        budget_menu(call.message.chat.id)

    if call.data == 'show_all_groups':
        msg = Finance.show_all_groups()
        # Отправляем текст в Телеграм
        bot.send_message(call.message.chat.id, msg)
        budget_menu(call.message.chat.id)

    if call.data == 'show_group':
        # Создаем клавиатуру для вывода групп
        keyboard_show_group = types.InlineKeyboardMarkup()
        for i in range(len(Finance.groups)):
            keyboard_show_group.add(types.InlineKeyboardButton(text=str(Finance.groups[i]),
                                                               callback_data=str('show_group_' + str(i))))
        # Отправляем текст и кнопки групп в Телеграм
        bot.send_message(call.message.chat.id, 'Расходы какой группы хотите посмотреть?',
                         reply_markup=keyboard_show_group)

    if 'show_group_' in call.data:
        index = int(call.data[11:])
        msg = Finance.show_group(Finance.groups[index])
        # Отправляем текст в Телеграм
        bot.send_message(call.message.chat.id, msg)
        budget_menu(call.message.chat.id)

    if call.data == 'show_all_price':
        msg = Finance.show_all_price()
        # Отправляем текст в Телеграм
        bot.send_message(call.message.chat.id, msg)
        bot.send_message(call.message.chat.id, 'Хотите узнать полные расходы в одной валюте?',
                         reply_markup=keyboard_convert)

    if call.data == 'convert_to_one':
        # Создаем клавиатуру для вывода валют
        keyboard_choice_currency = types.InlineKeyboardMarkup()
        for i in range(len(Finance.currencies)):
            keyboard_choice_currency.add(types.InlineKeyboardButton(text=str(Finance.currencies[i]),
                                                               callback_data=str('choice_curr_' + str(i))))
        # Отправляем текст и кнопки групп в Телеграм
        bot.send_message(call.message.chat.id, 'В какой валюте показать общий расход?',
                         reply_markup=keyboard_choice_currency)

    if 'choice_curr_' in call.data:
        index = int(call.data[12:])
        msg = str(round(Finance.convert_to_one()[index], 2)) + ' ' + Finance.currencies[index]
        # Отправляем текст в Телеграм
        bot.send_message(call.message.chat.id, msg)
        budget_menu(call.message.chat.id)

    if call.data == 'to_main':
        bot.send_message(call.message.chat.id, 'Выбери нужный раздел',
                         reply_markup=keyboard_main)

    if call.data == 'today':
        operation_date = date.today()
        print(operation_date)
        new_exe.append(operation_date)
        create_finance(call.message)

    if call.data == 'yesterday':
        operation_date = date.today() - timedelta(days=1)
        print(operation_date)
        new_exe.append(operation_date)
        create_finance(call.message)

    if call.data == 'other_date':
        start(call.message.chat.id)




bot.polling(none_stop=True, interval=0)