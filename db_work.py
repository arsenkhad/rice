from typing import Tuple, List
from db_context_manager import DBContextManager


def select(db_config: dict, sql: str) -> Tuple[Tuple, List[str]]:
    """
    Выполняет запрос (SELECT) к БД с указанным конфигом и запросом.
    Args:
        db_config: dict - Конфиг для подключения к БД.
        sql: str - SQL-запрос.
    Return:
        Кортеж с результатом запроса и описанеим колонок запроса.
    """
    result = tuple()
    schema = []
    with DBContextManager(db_config) as cursor:
        if cursor is None:
            raise ValueError('Cursor not found')
        cursor.execute(sql)
        schema = [column[0] for column in cursor.description]
        result = cursor.fetchall()
    return result, schema


def select_dict(db_config: dict, _sql: str):
    """
       Выполняет запрос (SELECT) к БД с указанным конфигом и запросом.
       Args:
           db_config: dict - Конфиг для подключения к БД.
           _sql: str - SQL-запрос.
       Return:
           Список словарей, где ключ - имя колонки, значение - результат запроса в текущей строке
       """
    with DBContextManager(db_config) as cursor:
        if cursor is None:
            raise ValueError('Cursor not found')
        cursor.execute(_sql)
        result = []
        schema = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            result.append(dict(zip(schema, row)))

        print('result dict:', '', ' '.join([f'{j:12}' for j in result[0]]),
              *[' '.join([f'{str(i[j]):12}' for j in i]) for i in result], sep='\n')
    return result


def insert(db_config: dict, _sql: str):
    """
       Выполняет SQL-код с БД с указанным конфигом.
       Args:
           db_config: dict - Конфиг для подключения к БД.
           _sql: str - SQL-код.
       Return:
           Результат выполнения SQL-кода
       """
    with DBContextManager(db_config) as cursor:
        if cursor is None:
            raise ValueError('Курсор не создан')
        result = cursor.execute(_sql)
    return result


def call_proc(db_config: dict, proc_name: str, *args):
    """
       Выполняет вызов процедуры в БД с указанным конфигом и аргументами.
       Args:
           db_config: dict - Конфиг для подключения к БД.
           proc_name: str - Название процедуры.
           *args: any - Аргументы вызова процедуры
       Return:
           Результат выполнения процедуры.
       """
    with DBContextManager(db_config) as cursor:
        if cursor is None:
            raise ValueError('Курсор не создан')
        param_list = []
        for arg in args:
            param_list.append(arg)

        res = cursor.callproc(proc_name, param_list)

        return res
