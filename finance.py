from forex_python.converter import CurrencyRates
import requests
import db
import json
import xlsxwriter
from datetime import date

data = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()
data2 = requests.get('https://theforexapi.com/api/latest').json()
all_currency = data['Valute'].keys() & data2['rates'].keys()


# Функция вывода всех операций определенной группы
def show_group(chat_id, search_group):
    result_show_group = f'Все расходы по статье - {search_group} \n'
    group_operations_db = db.fetchall(chat_id, f'WHERE operation_group = "{search_group}"')
    for i in group_operations_db:
        if i[3] == search_group:
            result_show_group += f"{i[0]} {i[1]} - {i[2]} ({i[4]})\n"
    return result_show_group


# Функция вывода всех операций
def show_operations(chat_id, count_offset=0):
    operations = find_operations(chat_id, count_offset)
    if count_offset == 0 and len(operations[0]) != 0:
        result_show_operations = 'Последние 5 операций: \n'
    else:
        result_show_operations = ''
    return result_show_operations + operations[1]


def find_operations(chat_id, count_offset):
    operations_db = db.fetchall(chat_id, offset=f'OFFSET {count_offset}')
    if len(operations_db) == 0:
        finded_operations = 'Операций нет'
    else:
        finded_operations = ''
    for i in operations_db:
        finded_operations += f"{i[0]} {i[1]} - {i[2]} / {i[3]} ({i[4]}) /del{operations_db.index(i)} \n"
    print(operations_db)
    db.update_param(chat_id, 'del_operations', operations_db)
    return [operations_db, finded_operations]


# Функция вывода суммы всех операций
def show_all_price(chat_id, type_operation=''):
    result_show_all_price = 'Всего потрачено: \n'
    currency_db = [str(*i) for i in db.fetch_unique_param(chat_id, 'operation_currency')]
    for currency in currency_db:
        if type_operation:
            try:
                sum_cur = str(abs(*db.sum_price(chat_id, currency, type_operation)))
            except TypeError:
                sum_cur = '0'
        else:
            sum_cur = str(*db.sum_price(chat_id, currency))
        result_show_all_price += f"{sum_cur} {currency} \n"
    return result_show_all_price


# Функция вывода операций определенного интервала
def show_operations_interval(chat_id, interval):
    result = f'Операции с {interval["start"]} по {interval["end"]}: \n'
    operations_interval_list = db.operations_interval(chat_id, interval)
    if len(operations_interval_list) == 0:
        result = 'В этом периоде операций не было'
    else:
        for i in operations_interval_list:
            result += f"{i[0]} {i[1]} - {i[2]} / {i[3]} ({i[4]}) /del{operations_interval_list.index(i)} \n"
    db.update_param(chat_id, 'del_operations', operations_interval_list)
    return result


# Функция конвертации во все валюты
def convert_to_one(chat_id, choice_currency):
    currency_db = [str(*i) for i in db.fetch_unique_param(chat_id, 'operation_currency')]
    result = 0
    convert = CurrencyRates()
    type_operation = db.fetch_param(chat_id, 'type_operation')
    for index in range(len(currency_db)):
        try:
            sum_cur = str(abs(*db.sum_price(chat_id, currency_db[index], type_operation)))
        except TypeError:
            sum_cur = '0'
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
    db.update_param(chat_id, 'type_operation', '')
    return result


def send_excel(chat_id, groups_list='', limit=5):
    if groups_list:
        all_op = ([('цена', 'валюта', 'назначение', 'статья', 'дата', 'id')]
                  + db.fetchall(chat_id, f'WHERE operation_group = "{groups_list}"', offset='', limit=''))
        print(all_op)
        file_name = f'budget-{chat_id}-{groups_list}.xlsx'
    else:
        all_op = [('цена', 'валюта', 'назначение', 'статья', 'дата', 'id')] + db.fetchall(chat_id, offset='', limit='')
        print(all_op)
        file_name = f'budget-{chat_id}.xlsx'

    workbook = xlsxwriter.Workbook(file_name)
    worksheet = workbook.add_worksheet()
    for row, line in enumerate(all_op):
        for col, cell in enumerate(line):
            worksheet.write(row, col, cell)
    workbook.close()
    return file_name


def fast_add(chat_id, parse):
    parse[0] = int(parse[0])
    parse[1] = parse[1].upper()
    db.update_param(chat_id, 'operation_date', date.today())
    new_exe = dict(zip(['operation_price', 'operation_currency',
                        'operation_name', 'operation_group'], parse))
    db.update_param(chat_id, 'new_exe', new_exe)
