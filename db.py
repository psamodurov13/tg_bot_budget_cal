import sqlite3 as sq
import os


def insert(table_id, dict):
    cn = sq.connect(os.path.join('budget.db'))
    cr = cn.cursor()
    cr.execute(f'''CREATE TABLE IF NOT EXISTS "{table_id}"
                (operation_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                operation_price INTEGER, 
                operation_currency VARCHAR(3), 
                operation_name VARCHAR(255), 
                operation_group VARCHAR(255),
                operation_date DATE) ''')
    columns = ', '.join([i for i in dict.keys()])
    values = [i for i in dict.values()]
    placeholders = ', '.join('?' * len(dict.keys()))
    cr.execute(f'''INSERT INTO "{table_id}" 
                ({columns}) 
                VALUES ({placeholders})''',
                values)
    cn.commit()
    print('Succesfull')
    fetchall(table_id)
    cn.close()

def fetchall(table_id, param='', offset=0):
    cn = sq.connect(os.path.join('budget.db'))
    cr = cn.cursor()
    cr.execute(f'''SELECT 
                operation_price, 
                operation_currency, 
                operation_name, 
                operation_group, 
                operation_date 
                FROM "{table_id}"
                {param}
                ORDER BY operation_date DESC
                LIMIT 5
                OFFSET {offset}''')
    result = cr.fetchall()
    print(f'{result}')
    cn.close()
    return result

def fetch_unique_param(table_id, param):
    cn = sq.connect(os.path.join('budget.db'))
    cr = cn.cursor()
    cr.execute(f'''SELECT DISTINCT {param}
                   FROM "{table_id}"''')
    result = cr.fetchall()
    print(result)
    cn.close()
    return result

def sum_price(table_id, currency):
    cn = sq.connect(os.path.join('budget.db'))
    cr = cn.cursor()
    cr.execute(f'''SELECT SUM("operation_price")
                   FROM "{table_id}"
                   WHERE operation_currency = "{currency}"''')
    result = cr.fetchall()[0]
    print(result)
    cn.close()
    return result

def operations_interval(table_id, interval):
    cn = sq.connect(os.path.join('budget.db'))
    cr = cn.cursor()
    cr.execute(f'''SELECT 
                operation_price, 
                operation_currency, 
                operation_name, 
                operation_group, 
                operation_date 
                FROM "{table_id}"
                WHERE operation_date BETWEEN "{interval[0]}" and "{interval[1]}"''')
    result = cr.fetchall()
    print(f'{result}')
    cn.close()
    return result

def count(table_id):
    cn = sq.connect(os.path.join('budget.db'))
    cr = cn.cursor()
    cr.execute(f'''SELECT COUNT("operation_price")
                   FROM "{table_id}"''')
    result = cr.fetchall()[0]
    print(result)
    cn.close()
    return result

def delete(table_id, operation):
    cn = sq.connect(os.path.join('budget.db'))
    cr = cn.cursor()
    cr.execute(f'''DELETE FROM "{table_id}"
                   WHERE operation_price = "{operation[0]}" AND 
                   operation_currency = "{operation[1]}" AND 
                   operation_name = "{operation[2]}" AND
                   operation_group = "{operation[3]}" AND
                   operation_date = "{operation[4]}"''')
    result = cr.fetchall()
    print(result)
    cn.commit()
    cn.close()
    return f'Запись {operation} удалена'