summarizer
===========

Short summaries of Tech news delivered to a Telegram channel.

More specifically, the project consists of the following parts:

 - `manager`: Listens to the RSS feeds of various popular Tech news.
 - `firefox`: Headless Firefox instance used for extracting text of a news article.
 - `pagesaver`: Firefox addon that extracts text of a news article.
 - `summarizer`: Uses pre-trained model for extracting short summary of a text.
 - `bot`: Telegram bot used for sending a short summary to a channel.

