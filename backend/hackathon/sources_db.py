import psycopg2
from psycopg2.extras import DictCursor
from django.conf import settings

def runQuery(query, db_name='default'):
    rows = []
    pg_connection = psycopg2.connect(
        dbname=settings.DATABASES[db_name]['NAME'],
        user=settings.DATABASES[db_name]['USER'],
        password=settings.DATABASES[db_name]['PASSWORD'],
        host=settings.DATABASES[db_name]['HOST'],
        port=settings.DATABASES[db_name]['PORT'],
    )
    with pg_connection.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
    cols = list(map(lambda x: x[0], cursor.description))
    cursor.close()
    pg_connection.close()
    data = []
    for row in rows:
        item = {}
        for index, col in enumerate(cols):
            item[col] = row[index]
        data.append(item)
    return data

def execQuery(query, db_name='default'):
    pg_connection = psycopg2.connect(
        dbname=settings.DATABASES[db_name]['NAME'],
        user=settings.DATABASES[db_name]['USER'],
        password=settings.DATABASES[db_name]['PASSWORD'],
        host=settings.DATABASES[db_name]['HOST'],
        port=settings.DATABASES[db_name]['PORT'],
    )
    with pg_connection.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute(query)
        add_data = pg_connection.commit()
    cursor.close()
    pg_connection.close()
    return add_data

def generateUpdateQuery(row, columns):
    q = []
    for column in columns:
        s = column + '='
        value = row[column]
        if type(value) == str:
            s += f"'{value}'"
        elif type(value) == bool:
            s += str(value)
        elif value is None:
            s += 'null'
        else: s += str(value)
        q.append(s)
    return ', '.join(q)

def getFirst(query, db_name='default'):
    items = runQuery(query, db_name)
    return items[0] if items else None