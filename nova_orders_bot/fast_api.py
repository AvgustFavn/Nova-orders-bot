from aiogram.types import WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from fastapi import FastAPI
from fastapi.params import Form
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy import func
from back import is_admin
from db import *
from filters import *
from main import bot

env = Environment(
    loader=FileSystemLoader('templates'),
    autoescape=select_autoescape(['html', 'xml'])
)
env.filters['time_delta'] = time_delta
env.filters['format_datetime'] = format_datetime

# Создание экземпляра FastAPI и Jinja2Templates с зарегистрированными фильтрами
app = FastAPI()
templates = Jinja2Templates(directory="templates")
templates.env = env



@app.get("/{id}/prog/sites")
async def prog_sites(request: Request, id: int):
    return templates.TemplateResponse(request, "form_order.html", context={'tg_id_client': id, "cat": 'Сайты'})

@app.post("/{id}/form/{cat}")
async def prog_another(request: Request, id: int, cat: str, name: str = Form(default=None), description: str = Form(default=None),
                     price: str = Form(default=None)):
    user = session.query(User).filter(User.tg_id == int(id)).first()
    order = Orders(tg_id_client=int(id), username_client=user.username, cat=cat, price=int(price), name=name, descr=description)
    session.add(order)
    session.commit()
    mess = Dialogs(id_order=int(order.id), tg_id_client=id, message=description)
    session.add(mess)
    session.commit()
    await bot.send_message(text='Мы получили ваш заказ! Как только его возьмут в работу, вы получите здесь уведомление. '
                                'Если вам будут писать сообщение от менеджера '
                                'или исполнителя заказа, вы так же получите уведомление. ', chat_id=user.tg_id)
    executors = session.query(User).filter(User.status == 2).all()
    builder = InlineKeyboardBuilder()
    builder.button(text=f'Взять заказ', callback_data=f'takeorder_{order.id}')
    builder.adjust(1)
    for e in executors:
        text = '✅ Новый заказ ✅\n' \
               f'Категория: {order.cat}' \
               f'Название: {name}' \
               f'➖➖➖➖➖➖➖➖➖' \
               f'ТЗ: {description}\n' \
               f'➖➖➖➖➖➖➖➖➖' \
               f'💲💲💲 Желаемая цена проекта: {price}USDT (При взятии заказа, можно обсудить цену и установить свою)'

        await bot.send_message(text=text, chat_id=e.tg_id, reply_markup=builder.as_markup())
    return RedirectResponse(f'/{order.id}/{user.tg_id}/{id}/messages', status_code=302)


@app.get("/{id}/prog/bots")
async def prog_bots(request: Request, id: int):
    return templates.TemplateResponse(request, "form_order.html", context={'tg_id_client': id, "cat": 'Боты'})

@app.get("/{id}/prog/another")
async def prog_another(request: Request, id: int):
    return templates.TemplateResponse(request, "form_order.html", context={'tg_id_client': id, "cat": 'Программирование, другое'})

@app.get("/{id}/paints")
async def prog_paints(request: Request, id: int):
    return templates.TemplateResponse(request, "form_order.html", context={'tg_id_client': id, "cat": 'Дизайн'})

@app.get("/{order_id}/{tg_id_client}/{here_id}/messages")
async def dialog(request: Request, order_id: int, tg_id_client: int, here_id: int):
    messages = session.query(Dialogs).filter(Dialogs.id_order == order_id).order_by(Dialogs.data_time.desc()).all()
    order = session.query(Orders).filter(Orders.id == order_id).first()
    client = session.query(User).filter(User.tg_id == int(tg_id_client)).first()
    print(tg_id_client, client)
    executor = session.query(User).filter(User.tg_id == order.tg_id_executor).first()
    if executor:
        return templates.TemplateResponse(request, "dialog.html", context={"messages": messages, "order": order,
                                                                  "time_cl": int(client.time_zone), "time_ex": int(executor.time_zone), "here": here_id})
    else:
        return templates.TemplateResponse(request, "dialog.html", context={"messages": messages, "order": order,
                                                                               "time_cl": int(client.time_zone),
                                                                               "here": here_id, "time_ex": 0})

@app.post("/{order_id}/{tg_id_client}/{here_id}/messages")
async def dialog(request: Request, order_id: int, tg_id_client: int, here_id: int, message: str = Form(default=None)):
    if tg_id_client == here_id:
        mess = Dialogs(id_order=int(order_id), tg_id_client=int(tg_id_client), message=message, data_time=datetime.datetime.utcnow())
        session.add(mess)
        session.commit()
        order = session.query(Orders).filter(Orders.id == order_id).first()
        builder = InlineKeyboardBuilder()
        builder.button(text=f'Зайти в диалог ➡️', web_app=WebAppInfo(url=f'https://nova-api.online/{order_id}/{tg_id_client}/{order.tg_id_executor}/messages'))
        builder.adjust(1)
        try:
            await bot.send_message(text='📩📬 Вам прислали сообщение 📩📬', chat_id=order.tg_id_executor, reply_markup=builder.as_markup())
        except:
            pass
        return RedirectResponse(f'/{order_id}/{tg_id_client}/{here_id}/messages', status_code=302)
    else:
        mess = Dialogs(id_order=int(order_id), tg_id_executor=int(here_id), message=message, data_time=datetime.datetime.utcnow())
        session.add(mess)
        session.commit()
        builder = InlineKeyboardBuilder()
        builder.button(text=f'Зайти в диалог ➡️', web_app=WebAppInfo(url=f'https://nova-api.online/{order_id}/{tg_id_client}/{tg_id_client}/messages'))
        builder.adjust(1)
        try:
            await bot.send_message(text='📩📬 Вам прислали сообщение 📩📬', chat_id=tg_id_client,
                               reply_markup=builder.as_markup())
        except:
            pass
        return RedirectResponse(f'/{order_id}/{tg_id_client}/{here_id}/messages', status_code=302)

@app.get("/{order_id}/{tg_id_client}/{exec_id}/take_it")
async def take(request: Request, order_id: int, tg_id_client: int, exec_id: int):
    order = session.query(Orders).filter(Orders.id == order_id).first()
    exec_u = session.query(User).filter(User.tg_id == int(exec_id)).first()
    if order.tg_id_executor == None:
        order.tg_id_executor = int(exec_id)
        order.username_executor = exec_u.username
        session.add(order)
        session.commit()
        builder = InlineKeyboardBuilder()
        builder.button(text=f'Сообщения заказа', web_app=WebAppInfo(url=f'https://nova-api.online/{order_id}/{tg_id_client}/{exec_id}/messages'))
        await bot.send_message(text='✅ Вы взяли заказ! ✅', chat_id=exec_id, reply_markup=builder.as_markup())
        await bot.send_message(text='✅ Ваш заказ взят! ✅', chat_id=tg_id_client, reply_markup=builder.as_markup())
        return RedirectResponse(f'/{order_id}/{tg_id_client}/{exec_id}/messages', status_code=302)
    else:
        pass

@app.get("/{order_id}/{tg_id}/price")
async def change_price(request: Request, tg_id: int, order_id: int):
    order = session.query(Orders).filter(Orders.id == order_id).first()
    return templates.TemplateResponse(request, "new_price.html", context={"order": order, "tg_id": tg_id})

@app.post("/{order_id}/{tg_id}/price")
async def change_price(request: Request, order_id: int, tg_id: int, digits: str = Form(default=None)):
    order = session.query(Orders).filter(Orders.id == order_id).first()
    order.price = int(digits)
    session.add(order)
    session.commit()
    builder = InlineKeyboardBuilder()
    builder.button(text=f'Зайти в диалог ➡️',  web_app=WebAppInfo(url=f'https://nova-api.online/{order_id}/{order.tg_id_client}/{tg_id}/messages'))
    try:
        await bot.send_message(text=f'💸 Цена заказа была изменена: {digits} usdt 💸', chat_id=order.tg_id_executor, reply_markup=builder.as_markup())
    except:
        pass
    await bot.send_message(text=f'💸 Цена заказа была изменена: {digits} usdt 💸', chat_id=order.tg_id_client, reply_markup=builder.as_markup())
    return RedirectResponse(f'/{order_id}/{order.tg_id_client}/{tg_id}/messages', status_code=302)

@app.get("/{order_id}/{tg_id}/cancel_exec")
async def cancel_exec(request: Request, order_id: int, tg_id: int, digits: str = Form(default=None)):
    order = session.query(Orders).filter(Orders.id == order_id).first()
    builder = InlineKeyboardBuilder()
    builder.button(text=f'Отказаться 👺🫡', callback_data=f'cancel_exec_{order_id}')
    await bot.send_message(text=f'Вы отказываетесь от заказа? Если не нажмете на подверждение, то заказ все еще будет у вас.', chat_id=tg_id, reply_markup=builder.as_markup())
    return RedirectResponse(f'/rightback', status_code=302)


@app.get("/rightback")
async def change_price(request: Request):
    return templates.TemplateResponse(request, "rightback.html")

@app.get("/search/{id_tg}")
async def change_price(request: Request, id_tg: int):
    return templates.TemplateResponse(request, "search.html")

@app.post("/search/{id_tg}")
async def change_price(request: Request, id_tg: int, keys: str = Form(default=None)):
    res = []
    keys = keys.split(' ')
    for k in keys:
        k = k.lower()
        ord_n = session.query(Orders).filter(func.lower(Orders.name).ilike(f'%{k}%')).all()
        try:
            ord_p = session.query(Orders).filter(Orders.name == int(k)).all()
        except:
            ord_p = []

        ord_m = session.query(Orders).filter(func.lower(Orders.descr).ilike(f'%{k}%')).all()
        if ord_m:
            res.extend(ord_m)
        if ord_p:
            res.extend(ord_p)
        if ord_n:
            res.extend(ord_n)

    if res:
        for o in res:
            text = f'⭐⭐⭐ Заказ: {o.name} ⭐⭐⭐\n' \
                   f'Цена проекта: {o.price}USDT\n' \
                   f'Категория заказа: {o.cat}\n' \
                   f'➖➖➖➖➖➖➖➖➖➖➖➖\n' \
                   f'ТЗ заказа: {o.descr}\n' \
                   f'➖➖➖➖➖➖➖➖➖➖➖➖'

            text += f'Клиент: @{o.username_client}\n'
            if o.tg_id_executor:
                text += f'Исполнитель: @{o.username_executor}\n'

            builder = InlineKeyboardBuilder()
            if o.tg_id_executor:
                builder.button(text=f'Посмотреть сообщения',
                               web_app=WebAppInfo(url=f'https://nova-api.online/{o.id}/{o.tg_id_client}/{o.tg_id_executor}/messages'))
            else:
                builder.button(text=f'Посмотреть сообщения',
                               web_app=WebAppInfo(
                                   url=f'https://nova-api.online/{o.id}/{o.tg_id_client}/{o.tg_id_client}/messages'))
            builder.button(text=f'Удалить заказ', callback_data=f'del_ord_{o.id}')
            builder.adjust(1)
            await bot.send_message(text=text, chat_id=id_tg, reply_markup=builder.as_markup())
        return RedirectResponse(f'/rightback', status_code=302)

    else:
        await bot.send_message(text='Кажется, заказ не нашелся', chat_id=id_tg)
        return RedirectResponse(f'/rightback', status_code=302)


@app.get("/do_exec/{id_tg}")
async def do_exec(request: Request, id_tg: int, username: str = Form(default=None)):
    return templates.TemplateResponse(request, "do_exec.html")

@app.post("/do_exec/{id_tg}")
async def do_exec(request: Request, id_tg: int, username: str = Form(default=None)):
    user = session.query(User).filter(User.username == username).first()
    if user:
        user.status = 2
        session.add(user)
        session.commit()
        bot.send_message(text=f'Пользователь @{username} теперь исполнитель', chat_id=id_tg)
        return RedirectResponse(f'/rightback', status_code=302)
    else:
        await bot.send_message(text='Пользователь с таким юзернеймом отсутствует в боте', chat_id=id_tg)
    return RedirectResponse(f'/rightback', status_code=302)

@app.get("/do_admin/{id_tg}")
async def do_admin(request: Request, id_tg: int, username: str = Form(default=None)):
    return templates.TemplateResponse(request, "do_exec.html")

@app.post("/do_admin/{id_tg}")
async def do_admin(request: Request, id_tg: int, username: str = Form(default=None)):
    user = session.query(User).filter(User.username == username).first()
    if user:
        user.status = 1
        session.add(user)
        session.commit()
        bot.send_message(text=f'Пользователь @{username} теперь администратор', chat_id=id_tg)
        return RedirectResponse(f'/rightback', status_code=302)
    else:
        await bot.send_message(text='Пользователь с таким юзернеймом отсутствует в боте', chat_id=id_tg)
    return RedirectResponse(f'/rightback', status_code=302)
