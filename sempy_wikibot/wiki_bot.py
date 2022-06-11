import logging
import re
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import wikipedia
from telegram.ext import Updater, CommandHandler, Filters, CallbackQueryHandler
from tokens import token

# import keyboards.disambiguation_keyboard as dkb
# import config

# Messages


FIND_OUT_MORE = '\n\n Find out more at '
HELP_MESSAGE = 'To wiki: \n\n /wiki [search input] \n\n To get random article from wikipedia: \n\n /random_wiki \n\n'

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def create_disambiguation_keyboard(disambiguation_options):
    keyboard = []

    for option in disambiguation_options:
        new_option = [InlineKeyboardButton(option, callback_data='ERROR;DISAMBIGUATION;' + option)]
        keyboard.append(new_option)

    return InlineKeyboardMarkup(keyboard)


def start(update, context):
    update.message.reply_text('Hi there! \U0001F60A \n\n' + HELP_MESSAGE)


def help(update, context):
    update.message.reply_text('Sending help now \U0001F60A \n\n' + HELP_MESSAGE)


def callback_handler(update, context):
    query = update.callback_query
    callback_data = query.data

    try:
        if 'ERROR;DISAMBIGUATION;' in callback_data:
            search_input = re.match("ERROR;DISAMBIGUATION;(.+)", callback_data).group(1)
            page_result = wikipedia.page(search_input)
            summary = page_result.summary
            message = FIND_OUT_MORE + page_result.url
            query.edit_message_text(text=summary + message)
    except:
        query.edit_message_text(text="Whut? An unprecedented error has occurred.")


def wiki(update, context):
    user_input = re.match("\/wiki([@_\w]+|) (.+)", update.message.text).group(2)
    try:
        page_result = wikipedia.page(user_input)
        summary = page_result.summary
        message = FIND_OUT_MORE + page_result.url
        update.message.reply_text(summary + message)
    except wikipedia.exceptions.DisambiguationError as disambiguation:
        try:
            update.message.reply_text('Please choose:',
                                      reply_markup=create_disambiguation_keyboard(disambiguation.options))
        except:
            update.message.reply_text("There is disambiguity but an unprecedented error has occurred.")

    except wikipedia.exceptions.PageError as page_error:
        update.message.reply_text("Unable to find wiki page for \'" + user_input + "\'.")

    except wikipedia.exceptions.HTTPTimeoutError as http_timeout:
        update.message.reply_text("Time out! Mediawiki is giving me trouble...")

    except wikipedia.exceptions.RedirectError as redirect_error:
        update.message.reply_text("Baam! Redirection Error.")

    except wikipedia.exceptions.WikipediaException as wiki_exception:
        update.message.reply_text("Welp... Wiki base class error.")

    except:
        update.message.reply_text("Whut? An unprecedented error has occurred.")


def random_wiki(update, context):
    user_input = wikipedia.random(pages=1)
    try:
        page_result = wikipedia.page(user_input)
        summary = page_result.summary
        message = FIND_OUT_MORE + page_result.url
        update.message.reply_text(summary + message)
    except wikipedia.exceptions.DisambiguationError as disambiguation:
        try:
            update.message.reply_text('Please choose:',
                                      reply_markup=create_disambiguation_keyboard(disambiguation.options))
        except:
            update.message.reply_text("There is disambiguity but an unprecedented error has occurred.")

    except wikipedia.exceptions.PageError as page_error:
        update.message.reply_text("Unable to find wiki page for \'" + user_input + "\'.")

    except wikipedia.exceptions.HTTPTimeoutError as http_timeout:
        update.message.reply_text("Time out! Mediawiki is giving me trouble...")

    except wikipedia.exceptions.RedirectError as redirect_error:
        update.message.reply_text("Baam! Redirection Error.")

    except wikipedia.exceptions.WikipediaException as wiki_exception:
        update.message.reply_text("Welp... Wiki base class error.")

    except:
        update.message.reply_text("Whut? An unprecedented error has occurred.")


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    updater = Updater(token.TG_TOKEN, use_context=True)

    '''Deployment'''
    # updater.start_webhook(listen="0.0.0.0", port=config.PORT, url_path=config.TOKEN)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("wiki", wiki))
    dp.add_handler(CommandHandler("random_wiki", random_wiki))
    updater.dispatcher.add_handler(CallbackQueryHandler(callback_handler))

    dp.add_error_handler(error)

    '''Deployment'''
    # updater.bot.set_webhook(config.APP_URL + config.TOKEN)

    '''Development'''
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    print("Starting bot...")
    main()
    print("Bot stopped.")
