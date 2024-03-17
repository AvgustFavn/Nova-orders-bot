import asyncio
import logging
import sys

from aiogram import *
from aiogram.filters import Command
from aiogram.types import WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

from back import is_in_sys, extract_first_number, is_orders_client, is_exec_n_upper, is_admin, is_work_had
from db import User, Orders, Dialogs
from db import session as sess

API_TOKEN = '7077677944:AAGF3Ybl9sAK37Kk27sttVlhfwo5X1pxyyw'
logging.basicConfig(level=logging.INFO)
router = Router()
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
dp.include_router(router)
logging.basicConfig(level=logging.INFO, stream=sys.stdout)


@router.message(Command(commands=["start"]))
async def cmd_start(message: types.Message):
    if await is_in_sys(message.from_user.id):
        builder = InlineKeyboardBuilder()
        builder.button(text=f'Каталог услуг 🛒', callback_data=f'catalog')
        builder.button(text=f'Наши работы 💼', url='https://t.me/cnproject/2')
        builder.button(text=f'Инфо ℹ️', url='https://t.me/cnproject/9')
        builder.button(text=f'Поддержка 24/7 👤', callback_data=f'help')
        if await is_orders_client(message.from_user.id):
            builder.button(text=f'Мои проекты ⚡️', callback_data=f'my_orders')
        if await is_exec_n_upper(message.from_user.id):
            builder.button(text=f'Лист свободных работ 📄', callback_data=f'orders')
        if await is_admin(message.from_user.id):
            builder.button(text=f'Админ панель', callback_data=f'admin')
        if await is_work_had(message.from_user.id):
            builder.button(text=f'Моя работа', callback_data=f'work')

        builder.adjust(1)

        # Отправляем сообщение с клавиатурой
        await message.answer(f"Привет, {message.from_user.username}, выберите из меню:", reply_markup=builder.as_markup())

    else:
        builder = InlineKeyboardBuilder()
        time_zones = [
            "UTC-12:00", "UTC-11:00", "UTC-10:00", "UTC-09:00", "UTC-08:00",
            "UTC-07:00", "UTC-06:00", "UTC-05:00", "UTC-04:00", "UTC-03:00",
            "UTC-02:00", "UTC-01:00", "UTC+00:00", "UTC+01:00", "UTC+02:00",
            "UTC+03:00", "UTC+04:00", "UTC+05:00", "UTC+06:00", "UTC+07:00",
            "UTC+08:00", "UTC+09:00", "UTC+10:00", "UTC+11:00", "UTC+12:00"
        ]

        buttons = [
            [builder.button(text=f'{tz}', callback_data=f'{tz}')]
            for i, tz in enumerate(time_zones, start=1)
        ]
        print(buttons)
        text = '🕓 Добро пожаловать! Выберите свой часовой пояс: 🕓'
        builder.adjust(2)
        await bot.send_message(text=text, chat_id=message.from_user.id, reply_markup=builder.as_markup())


@dp.callback_query(lambda c: c.data.startswith("UTC"))
async def callback_utc(c: types.CallbackQuery):
    num = await extract_first_number(c.data)
    print(num, c.data)
    if '-' in c.data:
        num = int(num) * -1

    print(num)

    try:
        user = User(tg_id=int(c.from_user.id), status=0, username=c.from_user.username, time_zone=num)
        sess.add(user)
        sess.commit()
    except:
        pass
    await bot.send_message(text='Теперь нам будет удобнее с вами контактировать :) Перезапустите бота: /start',
                           chat_id=c.from_user.id)

@dp.callback_query(lambda c: c.data == 'catalog')
async def callback_catalog(c: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text=f'Программирование 💻', callback_data=f'code')
    builder.button(text=f'Дизайн 🖼', callback_data=f'paint')
    builder.button(text=f'Bitcoin 🪙', callback_data=f'bitcoin')
    builder.adjust(1)
    await bot.send_message(text='Наши услуги:',
                           chat_id=c.from_user.id, reply_markup=builder.as_markup())


@dp.callback_query(lambda c: c.data == 'code')
async def callback_prog(c: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text=f'Бот любой сложности', callback_data=f'bots')
    builder.button(text=f'Сайт любой сложности', callback_data=f'sites')
    builder.button(text=f'Иное', callback_data=f'another_prog')
    builder.adjust(1)
    await bot.send_message(text='🖥 Наши услуги в сфере программирования 🖥 :',
                           chat_id=c.from_user.id, reply_markup=builder.as_markup())

@dp.callback_query(lambda c: c.data == 'bots')
async def callback_bots(c: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text=f'Напишите ТЗ:', web_app=WebAppInfo(url=f'https://nova-api.online/{c.from_user.id}/prog/bots'))
    await bot.send_message(text='Напишите ТЗ(техническое задание, описание вашей идеи):',
                           chat_id=c.from_user.id, reply_markup=builder.as_markup())

@dp.callback_query(lambda c: c.data == 'sites')
async def callback_sites(c: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text=f'Напишите ТЗ:', web_app=WebAppInfo(url=f'https://nova-api.online/{c.from_user.id}/prog/sites'))
    await bot.send_message(text='Напишите ТЗ(техническое задание, описание вашей идеи):',
                           chat_id=c.from_user.id, reply_markup=builder.as_markup())

@dp.callback_query(lambda c: c.data == 'another_prog')
async def callback_another_prog(c: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text=f'Напишите ТЗ:', web_app=WebAppInfo(url=f'https://nova-api.online/{c.from_user.id}/prog/another'))
    await bot.send_message(text='Напишите ТЗ(техническое задание, описание вашей идеи):',
                           chat_id=c.from_user.id, reply_markup=builder.as_markup())

@dp.callback_query(lambda c: c.data == 'orders_admin')
async def callback_orders_admin(c: types.CallbackQuery):
    if await is_admin(c.from_user.id):
        orders = sess.query(Orders).all()
        if orders:
            for o in orders:
                builder = InlineKeyboardBuilder()
                text = f'⭐️⭐️⭐️ Заказ: {o.name} ⭐️⭐️⭐️\n' \
                       f'Цена проекта: {o.price}USDT\n' \
                       f'Категория заказа: {o.cat}\n' \
                       f'➖➖➖➖➖➖➖➖➖➖\n' \
                       f'ТЗ заказа: {o.descr}\n' \
                       f'➖➖➖➖➖➖➖➖➖➖\n'

                if o.tg_id_executor:
                    text += f'Исполнитель: @{o.username_executor}\n'
                else:
                    text += f'Исполнитель: не назначен ❌\n'

                text += f'Клиент: @{o.username_client}\n'
                builder.button(text=f'Посмотреть диалог',
                               web_app=WebAppInfo(url=f'https://nova-api.online/{o.id}/{o.tg_id_client}/{c.from_user.id}/messages'))
                builder.button(text=f'Удалить заказ', callback_data=f'del_ord_{o.id}')
                builder.adjust(1)
                await bot.send_message(text=text, chat_id=c.from_user.id,
                                       reply_markup=builder.as_markup())
            await bot.send_message(text='Все доступные заказы были выведены, если нет - заказов доступных нету',
                                   chat_id=c.from_user.id)
        else:
            await bot.send_message(text='Видимо, у вас нету заказов', chat_id=c.from_user.id)


@dp.callback_query(lambda c: c.data == 'paint')
async def callback_paint(c: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text=f'Напишите ТЗ:', web_app=WebAppInfo(url=f'https://nova-api.online/{c.from_user.id}/paints'))
    await bot.send_message(text='Напишите ТЗ(техническое задание, описание вашей идеи):',
                           chat_id=c.from_user.id, reply_markup=builder.as_markup())

@dp.callback_query(lambda c: c.data == 'bitcoin')
async def callback_bitcoin(c: types.CallbackQuery):
    await bot.send_message(text='Здравствуйте, на данный момент покупка Bitcoin производится в ручном режиме. '
                                'Рассмотрим любую услугу по Bitcoin, пожалуйста напишите конкретную и ожидайте ответ '
                                'оператора @novac0d',
                           chat_id=c.from_user.id)

@dp.callback_query(lambda c: c.data == 'help')
async def callback_help(c: types.CallbackQuery):
    await bot.send_message(text='👤Поддержка 24/7👤\nЕсли у вас возникли вопросы, можете связаться с нашей поддержкой\nНапишите и оператор ответит вам в ближайшее время: @novac0d',
                           chat_id=c.from_user.id)

@dp.callback_query(lambda c: c.data == 'my_orders')
async def callback_my_orders(c: types.CallbackQuery):
    orders = sess.query(Orders).filter(Orders.tg_id_client == c.from_user.id).all()
    for o in orders:
        text = f'⭐️⭐️⭐️ Заказ: {o.name} ⭐️⭐️⭐️\n' \
               f'Цена проекта: {o.price}USDT\n' \
               f'Категория заказа: {o.cat}\n'
        if o.tg_id_executor:
            text += f'Исполнитель: назначен ✅\n'
        else:
            text += f'Исполнитель: не назначен ❌\n'

        if await is_admin(c.from_user.id):
            text += f'Клиент: @{o.username_client}\n'
            text += f'Исполнитель: @{o.username_executor}\n'

        builder = InlineKeyboardBuilder()
        builder.button(text=f'💌 Сообщения по заказу 💌', web_app=WebAppInfo(url=f'https://nova-api.online/{o.id}/{o.tg_id_client}/{c.from_user.id}/messages'))
        builder.adjust(1)
        await bot.send_message(text=text, chat_id=c.from_user.id, reply_markup=builder.as_markup())


@dp.callback_query(lambda c: c.data == 'orders')
async def callback_orders(c: types.CallbackQuery):
    if await is_exec_n_upper(c.from_user.id):
        builder = InlineKeyboardBuilder()
        builder.button(text=f'Программирование', callback_data='prog_orders')
        builder.button(text=f'Дизайн', callback_data='prog_dis')
        builder.adjust(1)
        await bot.send_message(text='Выберите категорию доступных заказов:', chat_id=c.from_user.id, reply_markup=builder.as_markup())

@dp.callback_query(lambda c: c.data == 'prog_orders')
async def callback_prog_orders(c: types.CallbackQuery):
    if await is_exec_n_upper(c.from_user.id):
        orders = sess.query(Orders).filter(Orders.tg_id_executor == None, Orders.cat.in_(['Сайты', 'Боты', 'Программирование, другое'])).all()
        for o in orders:
            desc = sess.query(Dialogs).filter(Dialogs.id_order == o.id).order_by(Dialogs.id.asc()).first()
            text = f'⭐️⭐️⭐️ Заказ: {o.name} ⭐️⭐️⭐️\n' \
                   f'Цена проекта: {o.price}USDT\n' \
                   f'Категория заказа: {o.cat}\n' \
                   f'➖➖➖➖➖➖➖➖➖➖➖➖\n' \
                   f'ТЗ заказа: {desc.message}\n' \
                   f'➖➖➖➖➖➖➖➖➖➖➖➖\n'

            text += f'Исполнитель: не назначен ❌\n'

            if await is_admin(c.from_user.id):
                text += f'Клиент: @{o.username_client}\n'

            builder = InlineKeyboardBuilder()
            builder.button(text=f'Взять заказ', web_app=WebAppInfo(url=f'https://nova-api.online/{o.id}/{o.tg_id_client}/{c.from_user.id}/take_it'))
            builder.adjust(1)
            await bot.send_message(text=text, chat_id=c.from_user.id, reply_markup=builder.as_markup())
        await bot.send_message(text='Все доступные заказы были выведены, если нет - заказов доступных нету', chat_id=c.from_user.id)

@dp.callback_query(lambda c: c.data == 'prog_dis')
async def callback_prog_dis(c: types.CallbackQuery):
    if await is_exec_n_upper(c.from_user.id):
        orders = sess.query(Orders).filter(Orders.tg_id_executor == None, Orders.cat == 'Дизайн').all()
        for o in orders:
            desc = sess.query(Dialogs).filter(Dialogs.id_order == o.id).order_by(Dialogs.id.asc()).first()
            text = f'⭐️⭐️⭐️ Заказ: {o.name} ⭐️⭐️⭐️\n' \
                   f'Цена проекта: {o.price}USDT\n' \
                   f'Категория заказа: {o.cat}\n' \
                   f'➖➖➖➖➖➖➖➖➖➖➖➖\n' \
                   f'ТЗ заказа: {desc.message}\n' \
                   f'➖➖➖➖➖➖➖➖➖➖➖➖\n'

            text += f'Исполнитель: не назначен ❌\n'

            if await is_admin(c.from_user.id):
                text += f'Клиент: @{o.username_client}\n'

            builder = InlineKeyboardBuilder()
            builder.button(text=f'Взять заказ', web_app=WebAppInfo(url=f'https://nova-api.online/{o.id}/{o.tg_id_client}/{c.from_user.id}/take_it'))
            builder.adjust(1)
            await bot.send_message(text=text, chat_id=c.from_user.id, reply_markup=builder.as_markup())
        await bot.send_message(text='Все доступные заказы были выведены, если нет - заказов доступных нету',
                               chat_id=c.from_user.id)

@dp.callback_query(lambda c: c.data == 'work')
async def callback_work(c: types.CallbackQuery):
    if await is_exec_n_upper(c.from_user.id):
        orders = sess.query(Orders).filter(Orders.tg_id_executor == c.from_user.id).all()
        if orders:
            builder = InlineKeyboardBuilder()
            builder.adjust(1)
            for o in orders:
                builder.button(text=f'Заказ: {o.name}',
                               web_app=WebAppInfo(url=f'https://nova-api.online/{o.id}/{o.tg_id_client}/{c.from_user.id}/messages'))
            await bot.send_message(text='Все ваши заказы: ', chat_id=c.from_user.id, reply_markup=builder.as_markup())
        else:
            await bot.send_message(text='Видимо, у вас нету заказов', chat_id=c.from_user.id)

@dp.callback_query(lambda c: c.data.startswith("cancel_exec_"))
async def callback_cancel_exec_(c: types.CallbackQuery):
    if await is_exec_n_upper(c.from_user.id):
        id_order = c.data.replace('cancel_exec_', '')
        print(id_order)
        id_order = int(id_order)
        order = sess.query(Orders).filter(Orders.id == id_order).first()
        order.tg_id_executor = None
        order.username_executor = None
        sess.add(order)
        sess.commit()
        await bot.send_message(text=f'Вы отказались от заказа', chat_id=c.from_user.id)
        await bot.send_message(text=f'Исполнитель отказался от вашего заказа. Теперь его могут выбрать другие фрилансеры.',
                               chat_id=order.tg_id_client)

@dp.callback_query(lambda c: c.data == 'admin')
async def callback_admin(c: types.CallbackQuery):
    if await is_admin(c.from_user.id):
        builder = InlineKeyboardBuilder()
        builder.adjust(1)
        builder.button(text=f'Все заказы', callback_data='orders_admin')
        builder.button(text=f'Найти заказ', web_app=WebAppInfo(url=f'https://nova-api.online/search/{c.from_user.id}'))
        builder.button(text=f'Назначить пользователя исполнителем', web_app=WebAppInfo(url=f'https://nova-api.online/do_exec/{c.from_user.id}'))
        builder.button(text=f'Назначить пользователя админом', web_app=WebAppInfo(url=f'https://nova-api.online/do_admin/{c.from_user.id}'))
        builder.button(text=f'Понижение полномочий пользователя',
                       web_app=WebAppInfo(url=f'https://nova-api.online/do_usual/{c.from_user.id}'))
        builder.adjust(1)
        await bot.send_message(text='Выберите действие:', chat_id=c.from_user.id, reply_markup=builder.as_markup())

@dp.callback_query(lambda c: c.data.startswith("del_ord_"))
async def callback_del_ord_(c: types.CallbackQuery):
    if await is_admin(c.from_user.id):
        id_order = int(c.data.replace('del_ord_', ''))
        order = sess.query(Orders).filter(Orders.id == id_order).first()
        messages = sess.query(Dialogs).filter(Dialogs.id_order == order.id)
        sess.delete(order)
        for m in messages:
             sess.delete(m)
        sess.commit()
        await bot.send_message(text=f'Вы удалили заказ', chat_id=c.from_user.id)

async def main() -> None:
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
