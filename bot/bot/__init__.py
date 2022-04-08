import logging
import os
import telegram

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove

token = os.getenv("TOKEN")
bot = telegram.Bot(token=token)


def send_to_editors(source, uri, title, summary, importance):
    summary_text = "\n".join([f"— {sentence}" for sentence in summary])
    message = f'<b>{title}</b>\n\n{summary_text}\n\n<a href="{uri}"><i>{source}</i></a>'

    icon = "\U0001F525" * importance
    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton(f"Promote {icon}", callback_data="promote")]]
    )

    bot.send_message(
        chat_id=-1001306868978,
        parse_mode="html",
        disable_web_page_preview=True,
        disable_notification=True,
        text=message,
        reply_markup=reply_markup,
    )


def promote_message(message):
    bot.send_message(
        chat_id="@brieftech",
        parse_mode="html",
        disable_web_page_preview=True,
        disable_notification=True,
        text=message.text_html,
    )

    bot.edit_message_reply_markup(
        message.chat.id, message.message_id, reply_markup=InlineKeyboardMarkup([[]])
    )


def send_directly(source, uri, title, summary):
    summary_text = "\n".join([f"— {sentence}" for sentence in summary])
    message = f'<b>{title}</b>\n\n{summary_text}\n\n<a href="{uri}"><i>{source}</i></a>'

    bot.send_message(
        chat_id="@brieftech",
        parse_mode="html",
        disable_web_page_preview=True,
        disable_notification=True,
        text=message,
    )
