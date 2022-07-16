import sqlite3 as sq
import os


def create_db(table_id):
    cn = sq.connect(os.path.join('budget.db'))
    cr = cn.cursor()
    cr.execute(f'''CREATE TABLE IF NOT EXISTS "{table_id}"
                (operation_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                operation_price INTEGER, 
                operation_currency VARCHAR(3), 
                operation_name VARCHAR(255), 
                operation_group VARCHAR(255),
                operation_date DATE) ''')
    cr.execute(f'''CREATE TABLE IF NOT EXISTS "users"
                   (user INTEGER,
                   operation_date DATE,
                   new_exe VARCHAR,
                   count_offset INTEGER,
                   callendar_param VARCHAR,
                   interval VARCHAR,
                   del_operations VARCHAR)''')
    cr.execute(f'''INSERT OR IGNORE INTO users  
                   (user, operation_date, new_exe, count_offset, callendar_param, interval, del_operations) 
                   VALUES ({table_id}, "", "", 0, "", "", "") ''')
    cn.commit()
    cn.close()


def insert(table_id, dict_new):
    cn = sq.connect(os.path.join('budget.db'))
    cr = cn.cursor()
    columns = ', '.join([i for i in dict_new.keys()])
    values = [i for i in dict_new.values()]
    placeholders = ', '.join('?' * len(dict_new.keys()))
    cr.execute(f'''INSERT INTO "{table_id}" 
                ({columns}) 
                VALUES ({placeholders})''', values)
    cn.commit()
    fetchall(table_id)
    cn.close()


def fetchall(table_id, param='', offset='OFFSET 0', limit='LIMIT 5'):
    cn = sq.connect(os.path.join('budget.db'))
    cr = cn.cursor()
    cr.execute(f'''SELECT 
                operation_price, 
                operation_currency, 
                operation_name, 
                operation_group, 
                operation_date, 
                operation_id 
                FROM "{table_id}"
                {param}
                ORDER BY operation_date DESC
                {limit} 
                {offset}''')
    result = cr.fetchall()
    cn.close()
    return result


def fetch_unique_param(table_id, param):
    cn = sq.connect(os.path.join('budget.db'))
    cr = cn.cursor()
    cr.execute(f'''SELECT DISTINCT {param}
                   FROM "{table_id}"''')
    result = cr.fetchall()
    cn.close()
    return result


def sum_price(table_id, currency):
    cn = sq.connect(os.path.join('budget.db'))
    cr = cn.cursor()
    cr.execute(f'''SELECT SUM("operation_price")
                   FROM "{table_id}"
                   WHERE operation_currency = "{currency}"''')
    result = cr.fetchall()[0]
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
                operation_date,
                operation_id 
                FROM "{table_id}"
                WHERE operation_date BETWEEN "{interval['start']}" and "{interval['end']}"''')
    result = cr.fetchall()
    cn.close()
    return result


def count(table_id):
    cn = sq.connect(os.path.join('budget.db'))
    cr = cn.cursor()
    cr.execute(f'''SELECT COUNT("operation_price")
                   FROM "{table_id}"''')
    result = cr.fetchall()[0]
    cn.close()
    return result


def delete(table_id, operation):
    cn = sq.connect(os.path.join('budget.db'))
    cr = cn.cursor()
    print(operation[5])
    cr.execute(f'''DELETE FROM "{table_id}"
                   WHERE operation_id = "{operation[5]}"''')
    cn.commit()
    cn.close()
    return f'Запись {operation} удалена'


def update_param(user_id, param, value):
    cn = sq.connect(os.path.join('budget.db'))
    cr = cn.cursor()
    cr.execute(f'''UPDATE users 
                   SET {param} = "{value}"
                   WHERE user = "{user_id}"''')
    cn.commit()
    cn.close()
    return f'{param} обновлен в БД'


def fetch_param(user_id, param):
    cn = sq.connect(os.path.join('budget.db'))
    cr = cn.cursor()
    cr.execute(f'''SELECT {param} FROM users 
                   WHERE user = "{user_id}"''')
    result = cr.fetchone()[0]
    print(result)
    cn.close()
    return result
