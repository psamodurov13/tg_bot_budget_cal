import pickle
from forex_python.converter import CurrencyRates
import requests

expense_book_file = 'info.data'


class Finance:
    # Создаем список со всеми операциями
    operations = []
    groups = []
    currencies = []

    def __init__(self, name, price, currency, group, date):
        self.name = name
        self.price = price
        self.currency = currency
        self.group = group
        self.date = date

        # Добавляем новую группу
        if self.group not in Finance.groups:
            Finance.groups.append(group)
            print(f'Создана новая группа расходов - {self.group}')

        # Добавляем новую валюту
        if self.currency not in Finance.currencies:
            Finance.currencies.append(currency)
            print(f'Добавлена новая валюта -  {self.currency}')

        # Добавляем новую операцию (словарь) в список операций
        Finance.operations.append({
            'Сумма': self.price,
            'Валюта': self.currency,
            'Товар': self.name,
            'Группа': self.group,
            'Дата': self.date
        })

        print(f'Расход: {self.price} {self.currency} - {self.name} / {self.group} / {self.date} \n')

    @staticmethod
    def start():
        try:
            with open(expense_book_file, 'rb') as f:
                try:
                    Finance.operations = pickle.load(f)
                    Finance.currencies = pickle.load(f)
                    Finance.groups = pickle.load(f)
                except EOFError:
                    print('Записей еще нет')
        except FileNotFoundError:
            print('Создаем книгу расходов')
            new_data = open(expense_book_file, 'wb')
            new_data.close()

    # Функция вывода всех операций определенной группы
    @staticmethod
    def show_group(search_group):
        result_show_group = f'Все расходы по статье - {search_group} \n'
        for i in range(len(Finance.operations)):
            if Finance.operations[i]['Группа'] == search_group:
                result_show_group += f"{Finance.operations[i]['Сумма']} {Finance.operations[i]['Валюта']} - " \
                                     f"{Finance.operations[i]['Товар']} / {Finance.operations[i]['Дата']} \n"
        return result_show_group

    # Функция вывода всех групп
    @staticmethod
    def show_all_groups():
        result_show_all_groups = 'Статьи расходов: \n'
        for i in Finance.groups:
            result_show_all_groups += f"{i} \n"
        return result_show_all_groups

    # Функция вывода всех операций
    @staticmethod
    def show_operations():
        result_show_operations = 'Все операции: \n'
        for i in Finance.operations:
            result_show_operations += f"{i['Сумма']} {i['Валюта']} - {i['Товар']} / {i['Группа']} / {i['Дата']}\n"
        return result_show_operations

    # Функция вывода суммы всех операций
    @staticmethod
    def show_all_price():
        result_show_all_price = 'Всего потрачено: \n'
        all_price = [0] * len(Finance.currencies)
        for operation in Finance.operations:
            index_operation = Finance.currencies.index(operation['Валюта'])
            all_price[index_operation] += operation['Сумма']
        for index in range(len(all_price)):
            result_show_all_price += f"{all_price[index]} {Finance.currencies[index]} \n"
        print(result_show_all_price)
        return result_show_all_price

    # Функция конвертации во все валюты
    @staticmethod
    def convert_to_one():
        print('currencies ', Finance.currencies)
        all_price = [0] * len(Finance.currencies)
        result_convert = [0] * len(Finance.currencies)
        convert = CurrencyRates()
        data = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()
        for operation in Finance.operations:
            index_operation = Finance.currencies.index(operation['Валюта'])
            all_price[index_operation] += operation['Сумма']
        for index_price in range(len(all_price)):
            for result_index in range(len(result_convert)):
                if index_price == result_index:
                    result_convert[index_price] += all_price[index_price]
                else:
                    if Finance.currencies[index_price] == 'RUB':
                        result_convert[index_price] += all_price[result_index] * \
                                               data['Valute'][Finance.currencies[result_index]]['Value'] / \
                                               data['Valute'][Finance.currencies[result_index]]['Nominal']
                    else:
                        if Finance.currencies[result_index] == 'RUB':
                            result_convert[index_price] += all_price[result_index] / \
                                                   data['Valute'][Finance.currencies[index_price]]['Value'] * \
                                                   data['Valute'][Finance.currencies[index_price]]['Nominal']
                        else:
                            result_convert[index_price] += convert.convert(Finance.currencies[result_index],
                                                                   Finance.currencies[index_price],
                                                                   all_price[result_index])

        return result_convert


Finance.start()
# running = True
#
# while running:
#     choise = int(input('''
#         1 - Добавить запись
#         2 - Посмотреть все записи
#         3 - Посмотреть все группы
#         4 - Посмотреть записи группы
#         5 - Сколько всего потрачено
#         6 - Закрыть программу
#     '''))
#
#     if choise == 1:
#         new_price = int(input('Введите сумму: '))
#         new_currency = str(input('Введите валюту: '))
#         new_product = str(input('Введите товар: '))
#         new_group = str(input('Введите статью расходов: '))
#         Finance(new_product, new_price, new_currency, new_group)
#         continue
#
#     if choise == 2:
#         Finance.show_operations()
#         continue
#
#     if choise == 3:
#         Finance.show_all_groups()
#         continue
#
#     if choise == 4:
#         Finance.show_all_groups()
#         find_group = str(input('Введите статью расходов: '))
#         Finance.show_group(find_group)
#         continue
#
#     if choise == 5:
#         Finance.show_all_price()
#         continue
#
#     if choise == 6:
#         # Сохраняем операции, группы и валюты в файл
#         with open(expense_book_file, 'wb') as f:
#             pickle.dump(Finance.operations, f)
#             pickle.dump(Finance.currencies, f)
#             pickle.dump(Finance.groups, f)
#         running = False
#
# print('Программа завершена')
# input('Нажмите Enter для выхода')
# quit()