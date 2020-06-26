import logging
import os
import telegram

bot = telegram.Bot(token=os.getenv('TOKEN'))


def send_summary(source, uri, title, summary):
    summary_text = '\n'.join([f'— {sentence}' for sentence in summary])
    message = f'<b>{title}</b>\n\n{summary_text}\n\n<a href="{uri}"><i>{source}</i></a>'

    bot.send_message(chat_id='@brieftech',
                     parse_mode='html',
                     disable_web_page_preview=True,
                     disable_notification=True,
                     text=message)
