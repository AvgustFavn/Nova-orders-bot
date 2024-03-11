import re

from db import *


async def is_in_sys(id_tg):
    user = session.query(User).filter(User.tg_id == int(id_tg)).first()
    if user:
        return True
    else:
        return False

async def extract_first_number(text):
    match = re.search(r'\d+', text)
    if match:
        return int(match.group())
    else:
        raise ValueError('No number found in the text')


async def is_orders_client(id_tg):
    orders = session.query(Orders).filter(Orders.tg_id_client == int(id_tg)).first()
    if orders:
        return True
    else:
        return False

async def is_exec_n_upper(id_tg):
    user = session.query(User).filter(User.tg_id == int(id_tg)).first()
    if user.status > 0:
        return True
    else:
        return False

async def is_admin(id_tg):
    user = session.query(User).filter(User.tg_id == int(id_tg)).first()
    if user.status == 1:
        return True
    else:
        return False

async def is_work_had(id_tg):
    orders = session.query(Orders).filter(Orders.tg_id_executor == int(id_tg)).first()
    if orders:
        return True
    else:
        return False