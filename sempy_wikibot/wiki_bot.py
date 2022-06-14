import logging
import re
# import xlsxwriter
import datetime as dt
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, User, Update, \
    Message
import wikipedia
from telegram.ext import Updater, CommandHandler, filters, CallbackQueryHandler, MessageHandler, CallbackContext, \
    Application
from tokens import token

# from telegram.ext.

# import keyboards.disambiguation_keyboard as dkb
# import config

# Messages
# bot = telebot.TeleBot(token.TG_TOKEN)
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


# def create_workbook(user_id):
#     workbook = xlsxwriter.Workbook(f'messages.xlsx')
#     worksheet = workbook.add_worksheet()
#
#     worksheet.write(0, 0, "Дата")
#     worksheet.write(0, 1, "Время")
#     worksheet.write(0, 2, "Вид сообщения")
#     worksheet.write(0, 3, "Отправитель")
#     worksheet.write(0, 4, "ID отправителя")
#     worksheet.write(0, 5, "Сообщение")
#     print("work")
#
#     return worksheet

def log(id_u, user_text, bot_text):
    global count
    # print("Hi")
    # print(update.message.chat.id)
    # print(update.message.text)
    log_file = f'{id_u}.log'
    with open(log_file, "at+", encoding='utf-16') as file:
        file.write('User: ' + user_text + '\n' + 'Bot: ' + bot_text + '\n')


def create_disambiguation_keyboard(disambiguation_options):
    keyboard = []

    for option in disambiguation_options:
        new_option = [InlineKeyboardButton(option, callback_data='ERROR;DISAMBIGUATION;' + option)]
        keyboard.append(new_option)

    return InlineKeyboardMarkup(keyboard)


async def start(update, context):
    await update.message.reply_text('Hi there! \n\n' + HELP_MESSAGE)
    log(update.message.chat.id, update.message.text, 'Hi there! \n\n' + HELP_MESSAGE)
    # Message.from_user(User.id)


async def help(update, context):
    await update.message.reply_text('Sending help now \n\n' + HELP_MESSAGE)
    log(update.message.chat.id, update.message.text, 'Sending help now \n\n' + HELP_MESSAGE)


async def get_lang(update, context):
    global lang
    if lang == "en":
        await update.message.reply_text('Current language: English')
        log(update.message.chat.id, update.message.text,
            'Current language: English')
    # elif lang == "":
    #     update.message.reply_text('Current language: English')
    elif lang == "ru":
        await update.message.reply_text('Текущий язык: Русский')
        log(update.message.chat.id, update.message.text,
            'Текущий язык: Русский')


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

async def set_lang(update, context):
    global lang
    global checklist_eng
    global checklist_ru
    eng_lang_button = KeyboardButton(text='Eng')
    rus_lang_button = KeyboardButton(text='Rus', )
    keyboard_array = [[eng_lang_button, rus_lang_button]]
    reply_markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, keyboard=keyboard_array)
    await update.message.reply_text('Choose language for searching', reply_markup=reply_markup)
    log(update.message.chat.id, update.message.text, 'Choose language for searching')


async def eng(update: Update, context: CallbackContext):
    global lang
    # user_input = query.data
    lang = "en"
    await update.message.reply_text("Selected language: Eng")
    log(update.message.chat.id, update.message.text, "Selected language: Eng")


async def rus(update: Update, context: CallbackContext):
    global lang
    # user_input = query.data
    lang = "ru"
    await update.message.reply_text("Selected language: Rus")
    log(update.message.chat.id, update.message.text, "Selected language: Rus")


async def callback_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    callback_data = query.data
    # print(update.callback_query.from_user.id)

    try:
        if 'ERROR;DISAMBIGUATION;' in callback_data:
            search_input = re.match("ERROR;DISAMBIGUATION;(.+)", callback_data).group(1)
            # search_inputl = re.match(r"\/ERROR;DISAMBIGUATION;([@_\w]+|) (.+)", callback_data).group(2)
            page_result = wikipedia.page(search_input)
            summary = page_result.summary
            message = FIND_OUT_MORE + page_result.url
            await query.edit_message_text(summary + message)
            log(update.callback_query.from_user.id, " ", summary + message)
    except:
        await query.edit_message_text(text="Whut? An unprecedented error has occurred.")
        log(update.callback_query.from_user.id, callback_data, "Whut? An unprecedented error has occurred.")


async def wiki(update, context):
    global lang
    wikipedia.set_lang(lang)
    # print(wikipedia.languages())
    user_input = re.match(r"\/wiki([@_\w]+|) (.+)", update.message.text).group(2)
    try:
        page_result = wikipedia.page(user_input)
        summary = page_result.summary
        message = FIND_OUT_MORE + page_result.url
        await update.message.reply_text(summary + message)
        log(update.message.chat.id, '/wiki ' + user_input, summary + message)
    except wikipedia.exceptions.DisambiguationError as disambiguation:
        try:
            await update.message.reply_text('Please choose:',
                                            reply_markup=create_disambiguation_keyboard(disambiguation.options))
            log(update.message.chat.id, '/wiki ' + user_input, 'Please choose:')

        except:
            await update.message.reply_text("There is disambiguity but an unprecedented error has occurred.")
            log(update.message.chat.id, '/wiki ' + user_input, "There is disambiguity but an unprecedented error has occurred.")

    except wikipedia.exceptions.PageError as page_error:
        await update.message.reply_text("Unable to find wiki page for \'" + user_input + "\'.")
        log(update.message.chat.id, '/wiki ' + user_input,
            "Unable to find wiki page for \'" + user_input + "\'.")

    except wikipedia.exceptions.HTTPTimeoutError as http_timeout:
        await update.message.reply_text("Time out! Mediawiki is giving me trouble...")
        log(update.message.chat.id, '/wiki ' + user_input,
            "Time out! Mediawiki is giving me trouble...")

    except wikipedia.exceptions.RedirectError as redirect_error:
        await update.message.reply_text("Baam! Redirection Error.")
        log(update.message.chat.id, user_input,
            "Baam! Redirection Error.")

    except wikipedia.exceptions.WikipediaException as wiki_exception:
        await update.message.reply_text("Welp... Wiki base class error.")
        log(update.message.chat.id, '/wiki ' +  user_input,
            "Welp... Wiki base class error.")

    except:
        await update.message.reply_text("Whut? An unprecedented error has occurred.")
        log(update.message.chat.id, '/wiki ' +  user_input,
            "Whut? An unprecedented error has occurred.")


async def random_wiki(update, context):
    global lang
    wikipedia.set_lang(lang)
    user_input = wikipedia.random(pages=1)
    try:
        page_result = wikipedia.page(user_input)
        summary = page_result.summary
        message = FIND_OUT_MORE + page_result.url
        await update.message.reply_text(summary + message)
        log(update.message.chat.id, '/random_wiki ' + user_input, summary + message)
    except wikipedia.exceptions.DisambiguationError as disambiguation:
        try:
            await update.message.reply_text('Please choose:',
                                            reply_markup=create_disambiguation_keyboard(disambiguation.options))
            log(update.message.chat.id, '/random_wiki ' + user_input, 'Please choose:')

        except:
            await update.message.reply_text("There is disambiguity but an unprecedented error has occurred.")
            log(update.message.chat.id, '/random_wiki ' + user_input, "There is disambiguity but an unprecedented error has occurred.")

    except wikipedia.exceptions.PageError as page_error:
        await update.message.reply_text("Unable to find wiki page for \'" + user_input + "\'.")
        log(update.message.chat.id, '/random_wiki ' + user_input,
            "Unable to find wiki page for \'" + user_input + "\'.")

    except wikipedia.exceptions.HTTPTimeoutError as http_timeout:
        await update.message.reply_text("Time out! Mediawiki is giving me trouble...")
        log(update.message.chat.id, '/random_wiki ' + user_input,
            "Time out! Mediawiki is giving me trouble...")

    except wikipedia.exceptions.RedirectError as redirect_error:
        await update.message.reply_text("Baam! Redirection Error.")
        log(update.message.chat.id, '/random_wiki ' + user_input,
            "Baam! Redirection Error.")

    except wikipedia.exceptions.WikipediaException as wiki_exception:
        await update.message.reply_text("Welp... Wiki base class error.")
        log(update.message.chat.id, '/random_wiki ' + user_input,
            "Welp... Wiki base class error.")

    except:
        await update.message.reply_text("Whut? An unprecedented error has occurred.")
        log(update.message.chat.id, '/random_wiki ' +  user_input,
            "Whut? An unprecedented error has occurred.")


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)

    # @bot.message_handler(content_types=['text'])
    # async def log(update, context):
    #     global count
    #     print("Hi")
    #     print(update.message.chat.id)
    #     # print(update.message.text)
    #     log_file = f'{update.message.chat.id}.log'
    #     with open(log_file, "at+") as file:
    #         file.write(update.message.text + '\n')
    #     print("Hi")

    # workbook = xlsxwriter.Workbook(f'{update.message.chat.id}.xlsx')
    # worksheet = workbook.add_worksheet()

    # worksheet.write(0, 0, "Дата")
    # worksheet.write(0, 1, "Время")
    # worksheet.write(0, 2, "Вид сообщения")
    # worksheet.write(0, 3, "Отправитель")
    # worksheet.write(0, 4, "ID отправителя")
    # worksheet.write(0, 5, "Сообщение")

    # worksheet = create_workbook(update.message.chat.id)
    # if update.message.text != 'стоп':
    #     worksheet.write(count, 0, str(dt.datetime.now().date()))
    #     worksheet.write(count, 1, str(dt.datetime.now().time())[0:0])
    #     worksheet.write(count, 2, "Текст")
    #     worksheet.write(count, 3, update.message.chat.first_name + '  ' + update.message.chat.last_name)
    #     worksheet.write(count, 4, update.message.chat.id)
    #     worksheet.write(count, 5, update.message.text)
    #     count += 1
    # await update.message.reply_text(update.message.text)
    # workbook.close()
    # print("Hi")


def main():
    # updater = Updater(token.TG_TOKEN, use_context=True)
    app = Application.builder().token(token.TG_TOKEN).build()
    '''Deployment'''
    # updater.start_webhook(listen="0.0.0.0", port=config.PORT, url_path=config.TOKEN)

    # dp = updater.dispatcher
    # app.add_handler(MessageHandler(filters.TEXT & filters.COMMAND, log))
    app.add_handler(MessageHandler(filters.Regex(re.compile(r'start', re.IGNORECASE)), start))
    app.add_handler(MessageHandler(filters.Regex(re.compile(r'help', re.IGNORECASE)), help))
    # dp.add_handler(MessageHandler(Filters.regex(re.compile(r'wiki', re.IGNORECASE)), wiki))
    app.add_handler(MessageHandler(filters.Regex(re.compile(r'random_wiki', re.IGNORECASE)), random_wiki))
    # app.add_handler(MessageHandler(filters.Regex(re.compile(r'wiki', re.IGNORECASE)), wiki))
    app.add_handler(MessageHandler(filters.Regex(re.compile(r'getlang', re.IGNORECASE)), get_lang))
    app.add_handler(MessageHandler(filters.Regex(re.compile(r'setlang', re.IGNORECASE)), set_lang))
    app.add_handler(MessageHandler(filters.Regex("Eng"), eng))
    app.add_handler(MessageHandler(filters.Regex("Rus"), rus))

    '''Old ver'''
    # dp.add_handler(CommandHandler("start", start))
    # dp.add_handler(CommandHandler("help", help))
    app.add_handler(CommandHandler("wiki", wiki))
    # dp.add_handler(CommandHandler("random_wiki", random_wiki))
    # dp.add_handler(CommandHandler("getlang", get_lang))
    # dp.add_handler(CommandHandler("setlang", set_lang))
    # dp.add_handler(CommandHandler("Eng", eng))
    # dp.add_handler(CommandHandler("Rus", rus))

    # app.updater.dispatcher.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(CallbackQueryHandler(callback_handler))

    app.add_error_handler(error)

    '''Deployment'''
    # updater.bot.set_webhook(config.APP_URL + config.TOKEN)

    '''Development'''
    # updater.start_polling()
    app.run_polling()
    # bot.polling(none_stop=True)

    app.idle()

    # print('Hi')

    # log_file = f'{User.id}.txt'
    # with open(log_file, "wb") as file:
    #     file.write(User.id)


if __name__ == '__main__':
    print("Starting bot...")
    main()
    print("Bot stopped.")
