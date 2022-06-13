import logging
import re
import xlsxwriter
import datetime as dt
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, User, Update, \
    Message
import wikipedia
from telegram.ext import Updater, CommandHandler, Filters, CallbackQueryHandler, MessageHandler, CallbackContext
from tokens import token

# import keyboards.disambiguation_keyboard as dkb
# import config

# Messages

lang = "en"
count = 1
checklist_eng = {'Eng', 'eng', 'ENG', 'EN', 'en', 'English', 'english', 'En', 'англ', 'Англ', 'Английский',
                 'английский'}
checklist_ru = {'Rus', 'rus', 'RUS', 'RU', 'ru', 'Russian', 'russian', 'Ru', 'рус', 'Рус', 'Русский', 'русский'}

FIND_OUT_MORE = '\n\n Find out more at '
HELP_MESSAGE = 'To wiki: \n\n /wiki [search input] \n\n To get random article from wikipedia: \n\n /random_wiki \n\n To get current language: \n\n /getlang \n\n To set new language:  \n\n /setlang'

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def create_workbook(user_id):
    workbook = xlsxwriter.Workbook(f'{user_id}.xlsx')
    worksheet = workbook.add_worksheet()

    worksheet.write(0, 0, "Дата")
    worksheet.write(0, 1, "Время")
    worksheet.write(0, 2, "Вид сообщения")
    worksheet.write(0, 3, "Отправитель")
    worksheet.write(0, 4, "ID отправителя")
    worksheet.write(0, 5, "Сообщение")

    return worksheet


def create_disambiguation_keyboard(disambiguation_options):
    keyboard = []

    for option in disambiguation_options:
        new_option = [InlineKeyboardButton(option, callback_data='ERROR;DISAMBIGUATION;' + option)]
        keyboard.append(new_option)

    return InlineKeyboardMarkup(keyboard)


def start(update, context):
    update.message.reply_text('Hi there! \U0001F60A \n\n' + HELP_MESSAGE)
    # Message.from_user(User.id)


def help(update, context):
    update.message.reply_text('Sending help now \U0001F60A \n\n' + HELP_MESSAGE)


def get_lang(update, context):
    global lang
    if lang == "en":
        update.message.reply_text('Current language: English')
    # elif lang == "":
    #     update.message.reply_text('Current language: English')
    elif lang == "ru":
        update.message.reply_text('Текущий язык: Русский')


# async def set_lang(update, context):
#     global lang
#     global checklist_eng
#     global checklist_ru
#     eng_lang_button = KeyboardButton('Eng')
#     rus_lang_button = KeyboardButton('Rus')
#     keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(eng_lang_button, rus_lang_button)
#     await update.message.reply_text('Choose language for searching', reply_markup=keyboard)
#     # user_input = update.message.text
#     # user_input = re.match("\/setlang([@_\w]+|) (.+)", update.message.text, flags=re.IGNORECASE).group(2)
#     # if user_input in checklist_eng:
#     #     lang = "en"
#     # elif user_input in checklist_ru:
#     #     lang = "ru"
#     # # if user_input == "english":
#     #     lang = "en"
#     # elif user_input == "en":
#     #     lang = "en"
#     # elif user_input == "русский":
#     #     lang = "ru"
#     # elif user_input == "ru":
#     #     lang = "ru"
#
# async def eng(update, context):
#     global lang
#     query = update.callback_query
#     # user_input = query.data
#     lang = "en"
#     await query.answer()
#
#     await query.edit_message_text(text=f"Selected language: {query.data}")
#
# async def rus(update, context):
#     global lang
#     query = update.callback_query
#     # user_input = query.data
#     lang = "ru"
#     await query.answer()
#
#     await query.edit_message_text(text=f"Selected language: {query.data}")

def set_lang(update, context):
    global lang
    global checklist_eng
    global checklist_ru
    eng_lang_button = KeyboardButton(text='Eng')
    rus_lang_button = KeyboardButton(text='Rus', )
    keyboard_array = [[eng_lang_button, rus_lang_button]]
    reply_markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, keyboard=keyboard_array)
    update.message.reply_text('Choose language for searching', reply_markup=reply_markup)


def eng(update: Update, context: CallbackContext):
    global lang
    # user_input = query.data
    lang = "en"
    update.message.reply_text("Selected language: Eng")


def rus(update: Update, context: CallbackContext):
    global lang
    # user_input = query.data
    lang = "ru"
    update.message.reply_text("Selected language: Rus")


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
    global lang
    wikipedia.set_lang(lang)
    # print(wikipedia.languages())
    user_input = re.match(r"\/wiki([@_\w]+|) (.+)", update.message.text).group(2)
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
    global lang
    wikipedia.set_lang(lang)
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


def log(update: Update, context):
    print("Hi")
    print(Message.from_user)
    global count
    worksheet = create_workbook(Message.from_user)
    print("Hi")
    worksheet.write(count, 0, str(dt.datetime.now().date()))
    worksheet.write(count, 1, str(dt.datetime.now().time()[0:0]))
    worksheet.write(count, 2, "Текст")
    worksheet.write(count, 3, Message.from_user(User.first_name) + '  ' + Message.from_user(User.last_name))
    worksheet.write(count, 4, Message.from_user(User.id))
    worksheet.write(count, 5, update.message.text)
    count += 1


def main():
    updater = Updater(token.TG_TOKEN, use_context=True)

    '''Deployment'''
    # updater.start_webhook(listen="0.0.0.0", port=config.PORT, url_path=config.TOKEN)

    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.regex(re.compile(r'start', re.IGNORECASE)), start))
    dp.add_handler(MessageHandler(Filters.regex(re.compile(r'help', re.IGNORECASE)), help))
    # dp.add_handler(MessageHandler(Filters.regex(re.compile(r'wiki', re.IGNORECASE)), wiki))
    dp.add_handler(MessageHandler(Filters.regex(re.compile(r'random_wiki', re.IGNORECASE)), random_wiki))
    dp.add_handler(MessageHandler(Filters.regex(re.compile(r'getlang', re.IGNORECASE)), get_lang))
    dp.add_handler(MessageHandler(Filters.regex(re.compile(r'setlang', re.IGNORECASE)), set_lang))
    dp.add_handler(MessageHandler(Filters.regex("Eng"), eng))
    dp.add_handler(MessageHandler(Filters.regex("Rus"), rus))
    dp.add_handler(MessageHandler(Filters.regex("log"), log))

    '''Old ver'''
    # dp.add_handler(CommandHandler("start", start))
    # dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("wiki", wiki))
    # dp.add_handler(CommandHandler("random_wiki", random_wiki))
    # dp.add_handler(CommandHandler("getlang", get_lang))
    # dp.add_handler(CommandHandler("setlang", set_lang))
    # dp.add_handler(CommandHandler("Eng", eng))
    # dp.add_handler(CommandHandler("Rus", rus))

    updater.dispatcher.add_handler(CallbackQueryHandler(callback_handler))

    dp.add_error_handler(error)

    '''Deployment'''
    # updater.bot.set_webhook(config.APP_URL + config.TOKEN)

    '''Development'''
    updater.start_polling()

    updater.idle()

    # print('Hi')

    # log_file = f'{User.id}.txt'
    # with open(log_file, "wb") as file:
    #     file.write(User.id)


if __name__ == '__main__':
    print("Starting bot...")
    main()

    print("Bot stopped.")
