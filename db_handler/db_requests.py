"""Модуль работы с БД fiber_db"""

from decimal import Decimal

import psycopg
from asyncpg_lite import DatabaseManager
from decouple import config
from psycopg.abc import Params, Query

PG_LINK = config("PG_LINK")
pg_manager = DatabaseManager(deletion_password=False, db_url=PG_LINK)
psycopg_manager = psycopg.connect(PG_LINK)


async def get_tg_id(tg_id: str, table_name="fiber_user"):
    """Получает tg_id из таблицы fiber_user"""
    async with pg_manager:
        user_tg_id = await pg_manager.select_data(
            table_name=table_name, where_dict={"tg_id": tg_id}, one_dict=True
        )
        if user_tg_id:
            return user_tg_id
        else:
            return None


async def insert_user(user_data: dict, table_name="fiber_user"):
    """Функция добавления пользователя"""
    async with pg_manager:
        await pg_manager.insert_data_with_update(
            table_name=table_name,
            records_data=user_data,
            conflict_column="tg_id",
            update_on_conflict=True,
        )


async def insert_calc_fiber(product_dict: dict, table_name="product_acceptance"):
    """Добавление значения клетчатки по продуку"""
    async with pg_manager:
        await pg_manager.insert_data_with_update(
            table_name=table_name,
            records_data=product_dict,
            conflict_column="product_acceptance_id",
            update_on_conflict=True,
        )


async def get_fiber_product(product: dict, table_name="product"):
    """Получение количества клетчатки на 100 г конекретного продукта"""
    async with pg_manager:
        await pg_manager.select_data(
            table_name,
            where_dict=product,
            columns=["amount_fiber_per_100"],
            one_dict=True,
        )


def execute_query(query: Query, params: Params | None, insert=False) -> list | None:
    """Подключение к БД и выполнение запроса"""
    with psycopg_manager.connect(PG_LINK) as manager:
        data = manager.execute(query, params)
        if insert:
            manager.commit()
        else:
            data = data.fetchall()
            return data


def get_daily_amount_fiber(tg_id: str) -> Decimal:
    """Получение количества клетчатки за текущие сутки"""
    query = """select calc_amount_fiber from product_acceptance pa
            where user_id = (select user_id from fiber_user where tg_id = %s)
            and date_trunc('day', pa.consumption_at) = date_trunc('day', now());
            """
    params = (tg_id,)
    data = execute_query(query, params)
    amount = Decimal("0")
    for el in data:
        amount += el[0]
    return amount


# TODO: Переименовать функцию
# TODO: Добавить проверку на наличие продукта в
def get_product_id_fiber(product_name: str):
    """Получение product_id и колиества клетчатки на 100 г продукта"""
    query = """select
    product_id, amount_fiber_per_100
from
    product
where
    tsv_content @@ plainto_tsquery('russian', %s);"""
    params = (product_name,)
    data = execute_query(query, params)
    return data


def insert_calc_amount_fiber(product_tuple: tuple):
    """Запрос на добавление записи о продукте"""
    query = """insert
    into product_acceptance(product_id, user_id, amount_product, calc_amount_fiber)
    values(
    %s,
    (select user_id from fiber_user where tg_id = %s),
    %s,
    %s);"""
    params = product_tuple
    execute_query(query, params, insert=True)
