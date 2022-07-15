from forex_python.converter import CurrencyRates
import requests
import db
import json
import xlsxwriter

del_operations = []


# Функция вывода всех операций определенной группы
def show_group(chat_id, search_group):
    result_show_group = f'Все расходы по статье - {search_group} \n'
    group_operations_db = db.fetchall(chat_id, f'WHERE operation_group = "{search_group}"')
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
    if count_offset == 0:
        result_show_operations = 'Последние 5 операций: \n'
    else:
        result_show_operations = ''
    return result_show_operations + find_operations(chat_id, count_offset)[1]


def find_operations(chat_id, count_offset):
    operations_db = db.fetchall(chat_id, offset=f'OFFSET {count_offset}')
    finded_operations = ''
    for i in operations_db:
        finded_operations += f"{i[0]} {i[1]} - {i[2]} / {i[3]} ({i[4]}) /del{operations_db.index(i)} \n"
    print(operations_db)
    db.update_param(chat_id, 'del_operations', operations_db)
    return [operations_db, finded_operations]

# Функция вывода суммы всех операций
def show_all_price(chat_id):
    result_show_all_price = 'Всего потрачено: \n'
    currency_db = [str(*i) for i in db.fetch_unique_param(chat_id, 'operation_currency')]
    for currency in currency_db:
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
    data = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()
    for index in range(len(currency_db)):
        sum_cur = str(*db.sum_price(chat_id, currency_db[index]))
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
    return result


def send_excel(chat_id, groups_list='', limit=5):
    if groups_list:
        ...
    else:
        all_op = [('цена', 'валюта', 'назначение', 'статья', 'дата', 'id')] + db.fetchall(chat_id, offset='', limit='')
        print(all_op)

        # Create a workbook and add a worksheet.
        file_name = f'budget-{chat_id}.xlsx'
        workbook = xlsxwriter.Workbook(file_name)
        worksheet = workbook.add_worksheet() # Some data we want to write to the worksheet.

        # data = [(123, 'enalapril'), (456, 'atenolol'), (789, 'lovastatin')] # Iterate over the data and write it out row by row.
        for row, line in enumerate(all_op):
            for col, cell in enumerate(line):
                worksheet.write(row, col, cell)
        workbook.close()
    return file_name

