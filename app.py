from flask import Flask, request, abort, send_file
from telebot import TeleBot, types
from telebot.types import WebAppInfo, MenuButtonWebApp, LabeledPrice, ShippingOption
import config
from utils import parse_init_data

bot = TeleBot(config.BOT_TOKEN, parse_mode="HTML")
app = Flask(__name__, static_url_path='/static')


@app.post(config.WEBHOOK_PATH)
def process_webhook_post():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        abort(403)


@app.get('/')
def index():
    return send_file('static/index.html')


@app.post('/submitOrder')
def submit_order():
    prices = []
    data = request.json
    init_data = parse_init_data(token=config.BOT_TOKEN, raw_init_data=data['initData'])
    if init_data is False:
        return False

    query_id = init_data['query_id']

    result_text = "<b>Order summary:</b>\n\n"
    for item in data['items']:
        name, price, amount = item.values()
        prices.append(LabeledPrice(label=f'{name}', amount=price))
        result_text += f"{name} x{amount} — <b>{price}</b>\n"
    result_text += '\n' + data["totalPrice"]

    result = types.InlineQueryResultArticle(
        id=query_id,
        title='Order',
        input_message_content=types.InputTextMessageContent(message_text=result_text, parse_mode='HTML'))
    bot.answer_web_app_query(query_id, result)
    global chat_id

    bot.send_invoice(
        chat_id,  # chat_id
        'GS Order Food',  # title
        ' Want to visit your great-great-great-grandparents? Make a fortune at the races? Shake hands with Hammurabi and take a stroll in the Hanging Gardens? Order our Working Time Machine today!',
        # description
        'HAPPY FRIDAYS COUPON',  # invoice_payload
        config.provider_token,  # provider_token
        'uzs',  # currency
        prices,  # prices
        photo_url='http://erkelzaar.tsudao.com/models/perrotta/TIME_MACHINE.jpg',
        photo_height=512,  # !=0/None or picture won't be shown
        photo_width=512,
        photo_size=512,
        is_flexible=False,  # True If you need to set up Shipping Fee
        start_parameter='time-machine-example')
    return ''


@bot.message_handler(commands=['start'])
def cmd_start(message: types.Message):
    bot.set_chat_menu_button(chat_id=message.chat.id, menu_button=MenuButtonWebApp(type='web_app', text='Open Menu',
                                                                                   web_app=WebAppInfo(
                                                                                      url=f'{config.WEBAPP_HOST}')))
    global chat_id
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup(
        keyboard=[
            [
                types.InlineKeyboardButton(
                    text="Order Food",
                    web_app=types.WebAppInfo(url=f'{config.WEBAPP_HOST}'),
                )
            ]
        ]
    )
    bot.send_message(message.from_user.id, f"<b>Hey {chat_id}!</b>\nYou can order food here!", reply_markup=markup)


@bot.message_handler(func=lambda message: message.via_bot)
def ordered(message: types.Message):
    bot.reply_to(message, '<b>Thank you for your order!</b>\n(It will not be delivered)')


def main():
    bot.delete_webhook()
    bot.set_webhook(config.WEBHOOK_URL)
    app.run(host=config.WEBAPP_HOST, port=config.WEBAPP_PORT)


if __name__ == "__main__":
    # app.run(host=config.WEBAPP_HOST, port=config.WEBAPP_PORT)
    main()

chat_id = None
