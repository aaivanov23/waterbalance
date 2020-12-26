#! /usr/bin/env python3

import sqlite3
import sys
import datetime
import prettytable

# write data to db
if len(sys.argv) < 2:
    print('''Incorrect use of the program.
    Please use that program with next input params: 
    1) ./water_balance.py x, when x is a amount of water you drink (type float or int)
    2) ./water_balance total [all | x], when
        without second param - amount of water for today,
        all - amount of water for all days,
        x - amount of water for last x days 
    ''')
    sys.exit()

conn = sqlite3.connect('water_balance.sqlite')
cur = conn.cursor()


def record_data(count):
    cur.execute('''
    create table if not exists water_balance
    (id integer not null Primary key autoincrement unique,
    datetime text,
    count_of_water double)''')

    cur.execute('''
    insert into water_balance (datetime, count_of_water)
    values (?, ?)''', (datetime.datetime.now().strftime('%d.%m.%Y'), count))

    conn.commit()


def show_count():
    cur.execute('''
    select datetime, SUM(count_of_water) as count
    from water_balance
    where datetime = ?''', (datetime.datetime.now().strftime('%d.%m.%Y'),))
    print(prettytable.from_db_cursor(cur))


if len(sys.argv) == 2:
    if sys.argv[1] == 'total':
        # do something
        show_count()
        conn.close()
    else:
        count_of_water = sys.argv[1]
        record_data(count_of_water)
        conn.close()
elif len(sys.argv) == 3:
    if sys.argv[2] == 'all':
        cur.execute('''
        select datetime, SUM(count_of_water) as count_of_water
        from water_balance 
        group by datetime''')
        print(prettytable.from_db_cursor(cur))
        conn.close()
    else:
        day_delta = int(sys.argv[2])
        table = prettytable.PrettyTable()
        table.field_names = ['datetime', 'count_of_water']
        dt = datetime.datetime.now()
        for i in range(day_delta-1, -1, -1):
            delta = datetime.timedelta(days=i)
            cur.execute('''
            select datetime, SUM(count_of_water)
            from water_balance
            where datetime=?''', ((dt - delta).strftime('%d.%m.%Y'),))
            data = cur.fetchone()
            if data[0] is not None:
                table.add_row([data[0], data[1]])
        print(table)
        conn.close()


