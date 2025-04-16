import asyncio
import logging
import os
import ssl
import sys
import warnings


from os import getenv

from aiohttp import web

from aiogram import Bot, Dispatcher, Router, F
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from dotenv import load_dotenv
from handlers.starthandler import router
from database.models import async_main
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from utils.commands import set_commands
from admin.handlerauthadmin import authorization_start
from admin.handleradddatagaid import adddescriptiongaid, addpole, addnamefail, addfail, addpricecardgaid, addpricestargaid
from admin.handleradddatakurs import addpoleurl, addnameurl, addurl, addpricecardkurs, addpricestarkurs, adddescriptionkurs
from admin.handlerdelitdatagaid import deletegaid, gaiddelit
from admin.handlerdelitdatakurs import deletekurs, kursdelit
from handlers.outputhandlergaid import gaid_start, gaidselect,buygaid, successful_paymentgaid, pre_checkout_querygaid, payphotocheckget, Trueanswer, Falseanswer, Confirmanswer, UnConfirmanswer, UnConfirmanswerno, ConfirmanswerYes, successfulphoto
from handlers.outputhandlerkurs import kurs_start, kursselect, buykurs, successful_paymentkurs, pre_checkout_querykurs, payphotocheckgetkurs, successfulphotokurs, Trueanswerkurs, Falseanswerkurs, Confirmanswerkurs, UnConfirmanswerkurs, ConfirmanswerYeskurs, UnConfirmanswernokurs
from admin.sendall import rassilka, kurs, kurssendall, gaids, gaidsendall
from admin.statistic import statistica

from aiogram.filters import Command
from admin.handleradddatagaid import AddGaid
from admin.handleradddatakurs import AddKurs
from handlers.outputhandlergaid import Card_Pay_gaid
from handlers.outputhandlerkurs import Card_Pay_kurs

load_dotenv()

SELF_SSL = False

# Path to webhook route, on which Telegram will send requests
WEBHOOK_PATH = "/" + getenv("PROJECT_NAME")

DOMAIN = getenv("DOMAIN_IP") if SELF_SSL else getenv("DOMAIN_NAME")
EXTERNAL_PORT = 8443

# Base URL for webhook will be used to generate webhook URL for Telegram,
# in this example it is used public DNS with HTTPS support
# BASE_WEBHOOK_URL = "https://aiogram.dev/"
BASE_WEBHOOK_URL = "https://" + DOMAIN + ":" + str(EXTERNAL_PORT)

if SELF_SSL:
    WEB_SERVER_HOST = DOMAIN
    WEB_SERVER_PORT = EXTERNAL_PORT
else:
    # Webserver settings
    # bind localhost only to prevent any external access
    WEB_SERVER_HOST = "127.0.0.1"
    # Port for incoming request from reverse proxy. Should be any available port
    WEB_SERVER_PORT = 8080

# Secret key to validate requests from Telegram (optional)
WEBHOOK_SECRET = "my-secret"

# ========= For self-signed certificate =======
# Path to SSL certificate and private key for self-signed certificate.
# WEBHOOK_SSL_CERT = "/path/to/cert.pem"
# WEBHOOK_SSL_PRIV = "/path/to/private.key"
if SELF_SSL:
    WEBHOOK_SSL_CERT = "../SSL/" + DOMAIN + ".self.crt"
    WEBHOOK_SSL_PRIV = "../SSL/" + DOMAIN + ".self.key"

async def on_startup(bot: Bot) -> None:
    if SELF_SSL:
        await bot.set_webhook(
            f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}",
            certificate=FSInputFile(WEBHOOK_SSL_CERT),
            secret_token=WEBHOOK_SECRET,
        )
    else:
        await bot.set_webhook(f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}", secret_token=WEBHOOK_SECRET)


# === (Added) Register shutdown hook to initialize webhook ===
async def on_shutdown(bot: Bot) -> None:

    await bot.delete_webhook()


token = os.getenv('TOKEN')
bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher()


async def mainasync() -> None:   
    await async_main()
    dp.include_router(router)
    await set_commands(bot)


def main() -> None:
    app = web.Application()


    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET,
    )
    # Register webhook handler on application
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)

    # Mount dispatcher startup and shutdown hooks to aiohttp application
    setup_application(app, dp, bot=bot)

    if SELF_SSL:  # ==== For self-signed certificate ====
        # Generate SSL context
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.load_cert_chain(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV)

        # And finally start webserver
        web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT, ssl_context=context)
    else:
        # And finally start webserver
        web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)

dp.startup.register(on_startup)
dp.shutdown.register(on_shutdown)


dp.message.register(authorization_start, Command(commands='adminsettings'))
# dp.message.register(authorization_start2, Auth.login)
# dp.message.register(authorization_start3, Auth.password)

dp.callback_query.register(addpole, F.data.startswith('keyboardaddgaid'))
dp.message.register(addnamefail, AddGaid.namefail)
dp.message.register(addfail, AddGaid.fail)
dp.message.register(adddescriptiongaid, AddGaid.descriptiongaid)
dp.message.register(addpricecardgaid, AddGaid.pricecardgaid)
dp.message.register(addpricestargaid, AddGaid.pricestargaid)

dp.message.register(gaid_start, Command(commands='gaid'))
dp.callback_query.register(gaidselect, F.data.startswith('selectgaid_'))
dp.callback_query.register(buygaid, F.data.startswith('stars_gaid'))
dp.pre_checkout_query.register(pre_checkout_querygaid)
dp.message.register(successful_paymentgaid, F.successful_payment.invoice_payload == 'gaids')

dp.callback_query.register(deletegaid, F.data.startswith('keyboarddeletegaid'))
dp.callback_query.register(gaiddelit, F.data.startswith('delitgaid_'))


dp.callback_query.register(addpoleurl, F.data.startswith('keyboardaddkurs'))
dp.message.register(addnameurl, AddKurs.nameurl)
dp.message.register(addurl, AddKurs.url)
dp.message.register(adddescriptionkurs, AddKurs.descriptionkurs)
dp.message.register(addpricecardkurs, AddKurs.pricecardkurs)
dp.message.register(addpricestarkurs, AddKurs.pricestarkurs)


dp.message.register(kurs_start, Command(commands='kurs'))
dp.callback_query.register(kursselect, F.data.startswith('selectkurs_'))
dp.callback_query.register(buykurs, F.data.startswith('stars_kurs'))
dp.pre_checkout_query.register(pre_checkout_querykurs)
dp.message.register(successful_paymentkurs, F.successful_payment.invoice_payload == 'kurs')

dp.callback_query.register(deletekurs, F.data.startswith('keyboarddeletekurs'))
dp.callback_query.register(kursdelit, F.data.startswith('delitkurs_'))


dp.callback_query.register(rassilka, F.data.startswith('keyboardrassilka'))
dp.callback_query.register(kurs, F.data == 'sendkurs')
dp.callback_query.register(kurssendall, F.data.startswith('sendkurs_'))
dp.callback_query.register(gaids, F.data == 'sendgaids')
dp.callback_query.register(gaidsendall, F.data.startswith('sendgaid_'))


dp.callback_query.register(statistica, F.data.startswith('keyboardstatistika'))

dp.callback_query.register(payphotocheckget, F.data.startswith('cards_gaid'))
dp.message.register(successfulphoto, Card_Pay_gaid.successful_photo_gaid)
dp.callback_query.register(Trueanswer, F.data.startswith('true_gaid'))
dp.callback_query.register(Falseanswer, F.data.startswith('false_gaid'))
dp.callback_query.register(Confirmanswer, F.data.startswith('yes_false_gaid'))
dp.callback_query.register(UnConfirmanswer, F.data.startswith('no_false_gaid'))
dp.callback_query.register(ConfirmanswerYes, F.data.startswith('ok_gaid'))
dp.callback_query.register(UnConfirmanswerno, F.data.startswith('no_gaid'))

dp.callback_query.register(payphotocheckgetkurs, F.data.startswith('cards_kurs'))
dp.message.register(successfulphotokurs, Card_Pay_kurs.successful_photo_kurs)
dp.callback_query.register(Trueanswerkurs, F.data.startswith('true_kurs'))
dp.callback_query.register(Falseanswerkurs, F.data.startswith('false_kurs'))
dp.callback_query.register(Confirmanswerkurs, F.data.startswith('yes_false_kurs'))
dp.callback_query.register(UnConfirmanswerkurs, F.data.startswith('no_false_kurs'))
dp.callback_query.register(ConfirmanswerYeskurs, F.data.startswith('ok_kurs'))
dp.callback_query.register(UnConfirmanswernokurs, F.data.startswith('no_kurs'))


if __name__ == "__main__":
    try:
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        warnings.filterwarnings("error", category=RuntimeWarning)
        main()
        asyncio.run(mainasync())
    except KeyboardInterrupt:
        print('Бот выключен')