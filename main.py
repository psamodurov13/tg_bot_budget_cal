import telebot
import finance
from telebot import types
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from datetime import date, timedelta
import db
from loguru import logger
import json
import ast

logger.add('debug.log', format='{time} {level} {message}', level='DEBUG', rotation='10 KB', compression='zip')

bot = telebot.TeleBot('5502805436:AAF83iukDBx0h4XXaeVLesFduwsxOFbETNw')

unknown = []

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
key_download_excel = types.InlineKeyboardButton(text='Скачать отчет', callback_data='download')
keyboard.add(key_download_excel)
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

# Готовим кнопки скачивания
keyboard_download_excel = types.InlineKeyboardMarkup()
key_download_all = types.InlineKeyboardButton(text='Выгрузить все операции', callback_data='download_all')
keyboard_download_excel.add(key_download_all)
key_download_category = types.InlineKeyboardButton(text='Выбрать статью расходов', callback_data='download_category')
keyboard_download_excel.add(key_download_category)
keyboard_download_excel.add(key_to_main)

# Готовим кнопки интервала времени операций без next
keyboard_operations_interval_wo_next = types.InlineKeyboardMarkup()
keyboard_operations_interval_wo_next.add(key_interval_operations)
keyboard_operations_interval_wo_next.add(key_to_main)

# Готовим кнопки календаря
keyboard_calendar = types.InlineKeyboardMarkup()
keyboard_calendar.add(key_to_main)


@bot.message_handler(commands=['start'])
def start_message(message):
    db.create_db(message.chat.id)
    bot.send_message(message.chat.id,
                     "Привет. Я помогу вести книгу учета расходов и заполнять календарь", reply_markup=keyboard_main)


@bot.message_handler(content_types=['text'])
@logger.catch
def get_text_messages(message):
    mt = message.text.lower()
    if mt == 'привет':
        bot.send_message(message.from_user.id, 'Привет. Я помогу вести книгу учета расходов и заполнять календарь',
                         reply_markup=keyboard_main)
    elif mt == '/help':
        bot.send_message(message.from_user.id, 'Для начала напиши "привет" или выбери один из пунктов меню. Я могу'
                                               'добавлять расходы и удалять добавленные записи, показывать статьи '
                                               'расходов, показывать операции по каждой статье расходов, считать '
                                               'количество потраченных денег в разной валюте. Для быстрого добавления '
                                               'новой операции напишите мне сообщение "100, rub, товар, статья '
                                               'расходов"')
    elif mt == 'скачать':
        file_name = finance.send_excel(message.from_user.id)
        bot.send_document(message.from_user.id, document=open(file_name, 'rb'))
    elif mt[:4] == '/del':
        del_operations = ast.literal_eval(db.fetch_param(message.chat.id, 'del_operations'))
        print(del_operations)
        print(type(del_operations))
        bot.send_message(message.from_user.id, db.delete(message.chat.id,
                                                         del_operations[int(message.text[4:])]),
                         reply_markup=keyboard)
    elif mt[0].isdigit():
        parse = mt.split(', ')
        parse[0] = int(parse[0])
        parse[1] = parse[1].upper()
        db.update_param(message.from_user.id, 'operation_date', date.today())
        new_exe = dict(zip(['operation_price', 'operation_currency',
                            'operation_name', 'operation_group'], parse))
        db.update_param(message.from_user.id, 'new_exe', new_exe)
        if len(new_exe) == 4:
            create_finance(message.from_user.id)
        else:
            bot.send_message(message.from_user.id, 'Возникла ошибка', reply_markup=keyboard_main)
    else:
        bot.send_message(message.from_user.id, 'Я тебя не  понимаю, напиши /help ')
        unknown.append(message.text)


# Функции сбора информации для добавления новой операции
@logger.catch
def add_operation(chat_id):
    # Ввод суммы новой операции
    message = bot.send_message(chat_id, 'Введите сумму.', reply_markup=keyboard_to_main)

    bot.register_next_step_handler(message, add_operation_currency)



@logger.catch
def add_operation_currency(message):
    if message.text.isdigit():
        # Ввод валюты новой операции
        new_exe = {'operation_price': float(message.text)}
        bot.send_message(message.from_user.id, 'Введите валюту.')
        bot.register_next_step_handler(message, add_operation_name, new_exe)
    else:
        bot.send_message(message.from_user.id, 'Возникла ошибка')
        to_main(message.from_user.id)


@logger.catch
def add_operation_name(message, new_exe):
    # Ввод названия операции
    new_exe['operation_currency'] = message.text
    bot.send_message(message.from_user.id, 'Введите товар.')
    bot.register_next_step_handler(message, add_operation_group, new_exe)


@logger.catch
def add_operation_group(message, new_exe):
    # Ввод статьи расходов
    new_exe['operation_name'] = message.text
    bot.send_message(message.from_user.id, 'Введите статью расходов.')
    bot.register_next_step_handler(message, add_operation_date, new_exe)


@logger.catch
def add_operation_date(message, new_exe):
    # Ввод даты операции
    new_exe['operation_group'] = message.text
    db.update_param(message.from_user.id, 'new_exe', new_exe)
    bot.send_message(message.from_user.id, 'Когда была совершена операция:', reply_markup=keyboard_operation_date)


@logger.catch
def start_callendar(chat_id):
    # Построение календаря
    calendar, step = DetailedTelegramCalendar().build()
    bot.send_message(chat_id,
                     f"Выберите {LSTEP[step]}",
                     reply_markup=calendar)


@logger.catch
@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def cal(c):
    # Ввод даты полностью
    result, key, step = DetailedTelegramCalendar().process(c.data)
    callendar_param = db.fetch_param(c.message.chat.id, 'callendar_param')
    if not result and key:
        bot.edit_message_text(f"Выберите {LSTEP[step]}",
                              c.message.chat.id,
                              c.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"Выбрана дата {result}",
                              c.message.chat.id,
                              c.message.message_id)
        if callendar_param == 'new_op':
            op_date = result
            db.update_param(c.message.chat.id, 'operation_date', op_date)
            create_finance(c.message.chat.id)
            db.update_param(c.message.chat.id, 'callendar_param', '')
        if callendar_param == 'interv':
            interval = json.loads(db.fetch_param(c.message.chat.id, 'interval').replace('\'', '"'))
            print(interval)
            print(type(interval))
            if len(interval) == 0:
                interval['start'] = str(result)
                db.update_param(c.message.chat.id, 'interval', interval)
                start_callendar(c.message.chat.id)
            elif len(interval) == 1:
                interval['end'] = str(result)
                bot.send_message(c.message.chat.id, finance.show_operations_interval(c.message.chat.id, interval))
                show_operations_menu_without_next(c.message.chat.id)
                interval = {}
                db.update_param(c.message.chat.id, 'interval', interval)
                db.update_param(c.message.chat.id, 'callendar_param', '')


@logger.catch
def create_finance(chat_id):
    # Создание операции
    new_exe = json.loads(db.fetch_param(chat_id, 'new_exe').replace('\'', '"'))
    new_exe['operation_date'] = db.fetch_param(chat_id, 'operation_date')
    bot.send_message(chat_id, f'Операция добавлена: '
                              f'{new_exe["operation_price"]} '
                              f'{new_exe["operation_currency"]} - '
                              f'{new_exe["operation_name"]} / '
                              f'{new_exe["operation_group"]} '
                              f'{new_exe["operation_date"]} \n')
    db.insert(chat_id, new_exe)
    msg = 'Данные сохранены.'
    bot.send_message(chat_id, msg)
    budget_menu(chat_id)
    db.update_param(chat_id, 'operation_date', '')
    db.update_param(chat_id, 'callendar_param', '')


@logger.catch
def budget_menu(chat_id):
    # Меню пункта "бюджет"
    bot.send_message(chat_id, 'Что вы хотите сделать?', reply_markup=keyboard)


@logger.catch
def show_operations_menu(chat_id):
    # Меню пункта "просмотр операций"
    bot.send_message(chat_id, 'Что дальше?', reply_markup=keyboard_operations_interval)


@logger.catch
def show_operations_menu_without_next(chat_id):
    # Меню пункта "просмотр операций"
    bot.send_message(chat_id, 'Что дальше?', reply_markup=keyboard_operations_interval_wo_next)

@logger.catch
def to_main(chat_id):
    bot.send_message(chat_id, 'Выбери нужный раздел',
                     reply_markup=keyboard_main)
    db.update_param(chat_id, 'count_offset', 0)


# Обработчик нажатий на кнопки
@logger.catch
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
        msg = finance.show_operations(call.message.chat.id)
        # Отправляем текст в Телеграм
        bot.send_message(call.message.chat.id, msg)
        print(db.count(call.message.chat.id)[0])
        print('len', db.count(call.message.chat.id)[0])
        if db.count(call.message.chat.id)[0] == 0:
            budget_menu(call.message.chat.id)
        elif db.fetch_param(call.message.chat.id, 'count_offset') + 5 >= int(*db.count(call.message.chat.id)):
            show_operations_menu_without_next(call.message.chat.id)
        else:
            show_operations_menu(call.message.chat.id)


    if call.data == 'next':
        db.update_param(call.message.chat.id, 'count_offset', db.fetch_param(call.message.chat.id, 'count_offset') + 5)
        msg = finance.show_operations(call.message.chat.id, db.fetch_param(call.message.chat.id, 'count_offset'))
        bot.send_message(call.message.chat.id, msg)
        if db.fetch_param(call.message.chat.id, 'count_offset')+5 < int(*db.count(call.message.chat.id)):
            show_operations_menu(call.message.chat.id)
        else:
            bot.send_message(call.message.chat.id, 'Больше записей нет')
            show_operations_menu_without_next(call.message.chat.id)
            db.update_param(call.message.chat.id, 'count_offset', 0)

    if call.data == 'interval':
        db.update_param(call.message.chat.id, 'callendar_param', 'interv')
        interval = {}
        db.update_param(call.message.chat.id, 'interval', interval)
        start_callendar(call.message.chat.id)

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
        to_main(call.message.chat.id)

    if call.data == 'today':
        db.update_param(call.message.chat.id, 'operation_date', date.today())
        create_finance(call.message.chat.id)

    if call.data == 'yesterday':
        db.update_param(call.message.chat.id, 'operation_date', date.today() - timedelta(days=1))
        create_finance(call.message.chat.id)

    if call.data == 'other_date':
        db.update_param(call.message.chat.id, 'callendar_param', 'new_op')
        start_callendar(call.message.chat.id)

    if call.data == 'download':
        bot.send_message(call.message.chat.id, 'Выберите тип отчета',
                         reply_markup=keyboard_download_excel)

    if call.data == 'download_all':
        file_name = finance.send_excel(call.message.chat.id)
        bot.send_document(call.message.chat.id, document=open(file_name, 'rb'))

    if call.data == 'download_category':
        bot.send_message(call.message.chat.id, 'В разработке',
                         reply_markup=keyboard_to_main)

bot.polling(none_stop=True, interval=0)
