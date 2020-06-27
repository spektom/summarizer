import logging

from telegram.ext import Updater, CallbackQueryHandler
from . import token, promote_message


def callback_handler(update, context):
    query = update.callback_query
    if query.data == 'promote':
        promote_message(query.message)


def start():
    updater = Updater(token, use_context=True)
    updater.dispatcher.add_handler(CallbackQueryHandler(callback_handler))

    logging.info('Started listening to incoming messages')

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(module)s: %(message)s')
    start()
