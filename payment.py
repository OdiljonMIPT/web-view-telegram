import telebot
from telebot.types import LabeledPrice, ShippingOption

# token = '5523238384:AAGh-rRIu0XmSSGdraemn6Xr1XHV5ovqixI'
import config

token = config.BOT_TOKEN_TEST
provider_token = '1650291590:TEST:1657792520511_YXJh8j57qk9uun6z'
bot = telebot.TeleBot(token)
bot.delete_webhook()

prices = [LabeledPrice(label='Working Time Machine', amount=100000), LabeledPrice('Gift wrapping', 50000)]

shipping_options = [
    ShippingOption(id='instant', title='WorldWide Teleporter').add_price(LabeledPrice('Teleporter', 100000)),
    ShippingOption(id='pickup', title='Local pickup').add_price(LabeledPrice('Pickup', 30000))]


@bot.message_handler(commands=['buy'])
def command_pay(message):
    bot.send_message(message.chat.id,
                     "Real cards won't work with me, no money will be debited from your account."
                     " Use this test card number to pay for your Time Machine: `4242 4242 4242 4242`"
                     "\n\nThis is your demo invoice:", parse_mode='Markdown')
    bot.send_invoice(
        message.chat.id,  # chat_id
        'Working Time Machine',  # title
        ' Want to visit your great-great-great-grandparents? Make a fortune at the races? Shake hands with Hammurabi and take a stroll in the Hanging Gardens? Order our Working Time Machine today!',
        # description
        'HAPPY FRIDAYS COUPON',  # invoice_payload
        provider_token,  # provider_token
        'uzs',  # currency
        prices,  # prices
        photo_url='http://erkelzaar.tsudao.com/models/perrotta/TIME_MACHINE.jpg',
        photo_height=512,  # !=0/None or picture won't be shown
        photo_width=512,
        photo_size=512,
        is_flexible=False,  # True If you need to set up Shipping Fee
        start_parameter='time-machine-example')


@bot.shipping_query_handler(func=lambda query: True)
def shipping(shipping_query):
    print(shipping_query)
    bot.answer_shipping_query(shipping_query.id, ok=True, shipping_options=shipping_options,
                              error_message='Oh, seems like our Dog couriers are having a lunch right now. Try again later!')


@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                  error_message="Aliens tried to steal your card's CVV, but we successfully protected your credentials,"
                                                " try to pay again in a few minutes, we need a small rest.")


@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    bot.send_message(message.chat.id,
                     'Hoooooray! Thanks for payment! We will proceed your order for `{} {}` as fast as possible! '
                     'Stay in touch.\n\nUse /buy again to get a Time Machine for your friend!'.format(
                         message.successful_payment.total_amount / 100, message.successful_payment.currency),
                     parse_mode='Markdown')


bot.infinity_polling(skip_pending=True)
