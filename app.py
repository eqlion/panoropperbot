#!/usr/bin/env python3

import os

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)

from cropper import Cropper
from PIL import Image
from os import path
from io import BytesIO

import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


PATH = path.join(path.dirname(__file__), '{}')
PHOTO, CHOICE = range(2)

def start(bot, update):
    update.message.reply_text('Hi! Now send `/crop` command to continue or `/help` to find out what this bot can do!')

def help(bot, update):
    update.message.reply_text('This bot can cut your panorama photo in equal square pieces which can be posted on Instagram in one post. More tech information is available on GitHub: https://github.com/eqlion/cropper-for-instagram')

def crop(bot, update):
    update.message.reply_text('Now please send me your panorama as a photo or a document or `/cancel` if you have changed your mind')

    return PHOTO

def photo(bot, update):
    photo_file = bot.get_file(update.message.photo[-1].file_id)
    photo_file.download('pano.jpg')

    update.message.reply_text('What a great photo!')

    reply_keyboard = [['1', '2', '3']]
    update.message.reply_text('Choose the way of cropping:\n'
                              '1. Auto (will select the best possible way)\n'
                              '2. Square (will create square images cutting off excess pixels from both sides)\n'
                              '3. Square (will create square images adding white stripes to both sides)',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return CHOICE

def choice(bot, update):
    logger.info('{}\'s pano is uploaded'.format(update.message.from_user.first_name))

    update.message.reply_text('Now the magic is happening!',
                                reply_markup=ReplyKeyboardRemove())

    img = Image.open(PATH.format('pano.jpg'))
    cropper = Cropper(img)
    possible = {
      1: 'cropper.auto()',
      2: 'cropper.square_cut()',
      3: 'cropper.square_fill()',
    }

    inp = int(update.message.text)
    parts = eval(possible[inp])
    chat_id = update.message.chat_id

    for i, part in enumerate(parts):
        bio = BytesIO()
        bio.name = '{}.jpg'.format(i + 1)
        part.save(bio, 'JPEG')
        bio.seek(0)
        bot.send_document(chat_id, document=bio)
    update.message.reply_text('That\'s it! Now you\'re ready to collect dozens of likes!')

    return ConversationHandler.END

def cancel(bot, update):
    update.message.reply_text('Bye! Come back when you take a great shot!', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def echo(bot, update):
    update.message.reply_text('Sorry, I don\'t get it :(')

def main():
    token = os.environ['PP_BOT_TOKEN']
    updater = Updater(token=token)

    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('crop', crop)],

        states={
            PHOTO: [MessageHandler(Filters.photo, photo),
                    MessageHandler(Filters.document, photo)],

            CHOICE: [RegexHandler('^(1|2|3)$', choice)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dp.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
