from telegram.ext import ApplicationBuilder, MessageHandler, filters, CommandHandler, CallbackQueryHandler
from src.api import BOT_TOKEN
from src.message import start, handle_study_ai
from keyboard.callback import callback_data

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler((filters.TEXT & ~filters.COMMAND ) | filters.PHOTO | filters.Document.ALL, handle_study_ai, block=False))
    app.add_handler(CallbackQueryHandler(callback_data))

    print('Bot is running...')
    app.run_polling()
