import json
import logging

import requests
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.message import ContentType

import config

# log
logging.basicConfig(level=logging.INFO)

# init
bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)

# prices
PRICE = types.LabeledPrice(label="2 виртуальных монет", amount=100 * 100)  # в копейках (руб)
PRICE_1 = types.LabeledPrice(label="4 виртуальных монет", amount=200 * 100)  # в копейках (руб)
PRICE_2 = types.LabeledPrice(label="10 виртуальных монет", amount=500 * 100)  # в копейках (руб)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    s = 'Привет, это бот оплаты виртуальных монет. После оплаты вы получите код который вам вышлет бот, который ' \
            'надо будет ввести на сайте, чтобы получить виртуальные монеты. Выберите команды в меню'
    await bot.send_message(message.chat.id, s)

# buy
@dp.message_handler(commands=['buy2'])
async def buy_one(message: types.Message):
    await bot.send_invoice(message.chat.id,
                           title="Две виртуальные монеты - 100 рублей",
                           description='Виртуальная монета для нашего сервиса',
                           provider_token=config.PAYMENTS_TOKEN,
                           currency="rub",
                           is_flexible=False,
                           prices=[PRICE],
                           start_parameter="one_coin",
                           payload="test-invoice-payload")

@dp.message_handler(commands=['buy10'])
async def buy_ten(message: types.Message):
    await bot.send_invoice(message.chat.id,
                           title="Десять виртуальных монет - 500 рублей",
                           description='Виртуальная монета для нашего сервиса',
                           provider_token=config.PAYMENTS_TOKEN,
                           currency="rub",
                           is_flexible=False,
                           prices=[PRICE_2],
                           start_parameter="ten_coin",
                           payload="test-invoice-payload")

@dp.message_handler(commands=['buy4'])
async def buy_four(message: types.Message):
    await bot.send_invoice(message.chat.id,
                           title="Четыре виртуальных монет - 200 рублей",
                           description='Виртуальная монета для нашего сервиса',
                           provider_token=config.PAYMENTS_TOKEN,
                           currency="rub",
                           is_flexible=False,
                           prices=[PRICE_1],
                           start_parameter="four_coin",
                           payload="test-invoice-payload")


# pre checkout  (must be answered in 10 seconds)
@dp.pre_checkout_query_handler(lambda query: True)
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


# successful payment
@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message):
    payment_info = message.successful_payment.to_python()
    d = list(payment_info.items())
    money = (int(d[1][1]) / 100) / 50
    check = d[-1][1]
    response = requests.post(f'http://127.0.0.1:8000/checks_path/', data={'money': money, 'check': check})  # !!!Смените потом на свой адрес сайта
    await bot.send_message(message.chat.id,
                           f"Платеж прошел, введи код на сайте для получения средств! Код: {check}")


# run long-polling
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=False)