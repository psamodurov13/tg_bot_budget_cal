import pickle
from forex_python.converter import CurrencyRates
import requests
import db

expense_book_file = 'info.data'

# Функция вывода всех операций определенной группы
def show_group(chat_id, search_group):
    result_show_group = f'Все расходы по статье - {search_group} \n'
    group_operations_db = db.fetchall(chat_id, f'WHERE operation_group = "{search_group}"')
    print(group_operations_db)
    for i in group_operations_db:
        if i[3] == search_group:
            result_show_group += f"{i[0]} {i[1]} - {i[2]} ({i[4]})\n"
    return result_show_group

# Функция вывода всех групп
def show_all_groups(chat_id):
    result_show_all_groups = 'Статьи расходов: \n'
    groups_db = db.fetch_unique_param(chat_id, 'operation_group')
    for i in groups_db:
        result_show_all_groups += str(*i) + '\n'
    return result_show_all_groups

# Функция вывода всех операций
def show_operations(chat_id, count_offset=0):
    result_show_operations = 'Все операции: \n'
    operations_db = db.fetchall(chat_id, offset=count_offset)
    for i in operations_db:
        result_show_operations += f"{i[0]} {i[1]} - {i[2]} / {i[3]} ({i[4]})\n"
    return result_show_operations

# Функция вывода суммы всех операций
def show_all_price(chat_id):
    result_show_all_price = 'Всего потрачено: \n'
    currency_db = [str(*i) for i in db.fetch_unique_param(chat_id, 'operation_currency')]
    print(currency_db)
    for currency in currency_db:
        sum_cur = str(*db.sum_price(chat_id, currency))
        result_show_all_price += f"{sum_cur} {currency} \n"
    print(result_show_all_price)
    return result_show_all_price

# Функция конвертации во все валюты
def convert_to_one(chat_id, choice_currency):
    currency_db = [str(*i) for i in db.fetch_unique_param(chat_id, 'operation_currency')]
    print('currencies ', currency_db)
    result = 0
    convert = CurrencyRates()
    data = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()
    for index in range(len(currency_db)):
        sum_cur = str(*db.sum_price(chat_id, currency_db[index]))
        print(sum_cur)
        if currency_db[index] == choice_currency:
            result += int(sum_cur)
        else:
            if choice_currency == 'RUB':
                result += int(sum_cur) * data['Valute'][currency_db[index]]['Value'] / \
                          data['Valute'][currency_db[index]]['Nominal']
            else:
                if currency_db[index] == 'RUB':
                    result += int(sum_cur) / data['Valute'][choice_currency]['Value'] * \
                              data['Valute'][choice_currency]['Nominal']
                else:
                    result += convert.convert(currency_db[index], choice_currency, int(sum_cur))
    print(result, ' ', choice_currency)
    return result