import telebot
import finance
from telebot import types
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from datetime import date, timedelta
import db

bot = telebot.TeleBot('5502805436:AAF83iukDBx0h4XXaeVLesFduwsxOFbETNw')

unknown = []
operation_date = ''
new_exe = {}
count_offset = 0

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

# Готовим кнопки интервала времени операций
keyboard_operations_interval = types.InlineKeyboardMarkup()
key_next_operations = types.InlineKeyboardButton(text='Посмотреть следующие операции', callback_data='next')
keyboard_operations_interval.add(key_next_operations)
key_interval_operations = types.InlineKeyboardButton(text='Выбрать интервал', callback_data='interval')
keyboard_operations_interval.add(key_interval_operations)
keyboard_operations_interval.add(key_to_main)

# Готовим кнопки интервала времени операций без next
keyboard_operations_interval_wo_next = types.InlineKeyboardMarkup()
keyboard_operations_interval_wo_next.add(key_interval_operations)
keyboard_operations_interval_wo_next.add(key_to_main)

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
    else:
        bot.send_message(message.from_user.id, 'Я тебя не  понимаю, напиши /help ')
        unknown.append(message.text)


# Функции сбора информации для добавления новой операции
def add_operation(chat_id):
    '''Ввод суммы новой операции'''
    message = bot.send_message(chat_id, 'Введите сумму.')
    bot.register_next_step_handler(message, add_operation_currency)
    print(message)


def add_operation_currency(message):
    '''Ввод валюты новой операции'''
    global new_exe
    new_exe = {}
    new_exe['operation_price'] = int(message.text)
    bot.send_message(message.from_user.id, 'Введите валюту.')
    bot.register_next_step_handler(message, add_operation_name)
    print(message)


def add_operation_name(message):
    '''Ввод названия операции'''
    new_exe['operation_currency'] = message.text
    bot.send_message(message.from_user.id, 'Введите товар.')
    bot.register_next_step_handler(message, add_operation_group)


def add_operation_group(message):
    '''Ввод статьи расходов'''
    new_exe['operation_name'] = message.text
    bot.send_message(message.from_user.id, 'Введите статью расходов.')
    bot.register_next_step_handler(message, add_operation_date)


def add_operation_date(message):
    '''Ввод даты операции'''
    new_exe['operation_group'] = message.text
    bot.send_message(message.from_user.id, 'Когда была совершена операция:', reply_markup=keyboard_operation_date)


def start_callendar(chat_id):
    '''Построение календаря'''
    calendar, step = DetailedTelegramCalendar().build()
    bot.send_message(chat_id,
                     f"Выберите {LSTEP[step]}",
                     reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def cal(c):
    '''Ввод даты полностью'''
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
        create_finance(c.message)


def create_finance(message):
    '''Создание операции'''
    new_exe['operation_date'] = operation_date
    bot.send_message(message.chat.id, f'Операция добавлена: '
                                      f'{new_exe["operation_price"]} '
                                      f'{new_exe["operation_currency"]} - '
                                      f'{new_exe["operation_name"]} / '
                                      f'{new_exe["operation_group"]} '
                                      f'{new_exe["operation_date"]} \n')
    db.insert(message.chat.id, new_exe)
    # Finance(new_exe[2], new_exe[0], new_exe[1], new_exe[3], new_exe[4])
    # with open(finance.expense_book_file, 'wb') as f:
    #     pickle.dump(Finance.operations, f)
    #     pickle.dump(Finance.currencies, f)
    #     pickle.dump(Finance.groups, f)
    # Отправляем текст в Телеграм
    msg = 'Данные сохранены.'
    bot.send_message(message.chat.id, msg)
    budget_menu(message.chat.id)


def budget_menu(chat_id):
    '''Меню пункта "бюджет"'''
    bot.send_message(chat_id, 'Что вы хотите сделать?', reply_markup=keyboard)

def show_operations_menu(chat_id):
    '''Меню пункта "просмотр операций"'''
    bot.send_message(chat_id, 'Что дальше?', reply_markup=keyboard_operations_interval)

def show_operations_menu_without_next(chat_id):
    '''Меню пункта "просмотр операций"'''
    bot.send_message(chat_id, 'Что дальше?', reply_markup=keyboard_operations_interval_wo_next)

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
        global count_offset
        msg = finance.show_operations(call.message.chat.id)
        # Отправляем текст в Телеграм
        bot.send_message(call.message.chat.id, msg)
        show_operations_menu(call.message.chat.id)
        count_offset = 5


    if call.data == 'next':
        msg = finance.show_operations(call.message.chat.id, count_offset)
        bot.send_message(call.message.chat.id, msg)
        count_offset += 5
        if count_offset <= int(*db.count(call.message.chat.id)):
            show_operations_menu(call.message.chat.id)
        else:
            show_operations_menu_without_next(call.message.chat.id)
            count_offset = 0


    if call.data == 'show_all_groups':
        msg = finance.show_all_groups(call.message.chat.id)
        # Отправляем текст в Телеграм
        bot.send_message(call.message.chat.id, msg)
        budget_menu(call.message.chat.id)

    if call.data == 'show_group':
        # Создаем клавиатуру для вывода групп
        keyboard_show_group = types.InlineKeyboardMarkup()
        groups_db = [str(*i) for i in db.fetch_unique_param(call.message.chat.id, 'operation_group')]
        for i in groups_db:
            keyboard_show_group.add(types.InlineKeyboardButton(text=str(i),
                                                               callback_data=str('show_group_' + str(i))))
        # Отправляем текст и кнопки групп в Телеграм
        bot.send_message(call.message.chat.id, 'Расходы какой группы хотите посмотреть?',
                         reply_markup=keyboard_show_group)

    if 'show_group_' in call.data:
        msg = finance.show_group(call.message.chat.id, call.data[11:])
        # Отправляем текст в Телеграм
        bot.send_message(call.message.chat.id, msg)
        budget_menu(call.message.chat.id)

    if call.data == 'show_all_price':
        msg = finance.show_all_price(call.message.chat.id)
        # Отправляем текст в Телеграм
        bot.send_message(call.message.chat.id, msg)
        bot.send_message(call.message.chat.id, 'Хотите узнать полные расходы в одной валюте?',
                         reply_markup=keyboard_convert)

    if call.data == 'convert_to_one':
        # Создаем клавиатуру для вывода валют
        keyboard_choice_currency = types.InlineKeyboardMarkup()
        currency_db = [str(*i) for i in db.fetch_unique_param(call.message.chat.id, 'operation_currency')]
        for i in currency_db:
            keyboard_choice_currency.add(types.InlineKeyboardButton(text=str(i),
                                                               callback_data=str('choice_curr_' + str(i))))
        # Отправляем текст и кнопки групп в Телеграм
        bot.send_message(call.message.chat.id, 'В какой валюте показать общий расход?',
                         reply_markup=keyboard_choice_currency)

    if 'choice_curr_' in call.data:
        choice_currency = call.data[12:]
        msg = str(round(finance.convert_to_one(call.message.chat.id, choice_currency))) + ' ' + choice_currency
        # Отправляем текст в Телеграм
        bot.send_message(call.message.chat.id, msg)
        budget_menu(call.message.chat.id)

    if call.data == 'to_main':
        bot.send_message(call.message.chat.id, 'Выбери нужный раздел',
                         reply_markup=keyboard_main)
        count_offset = 0

    if call.data == 'today':
        operation_date = date.today()
        print(operation_date)
        new_exe['operation_date'] = operation_date
        create_finance(call.message)

    if call.data == 'yesterday':
        operation_date = date.today() - timedelta(days=1)
        print(operation_date)
        new_exe['operation_date'] = operation_date
        create_finance(call.message)

    if call.data == 'other_date':
        start_callendar(call.message.chat.id)




bot.polling(none_stop=True, interval=0)