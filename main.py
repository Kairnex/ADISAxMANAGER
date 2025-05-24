from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler,
    filters
)
import logging
import config
import handlers

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    app = ApplicationBuilder().token(config.TOKEN).build()

    app.add_handler(CommandHandler("start", handlers.start))
    app.add_handler(CommandHandler("auth", handlers.auth))
    app.add_handler(CommandHandler("unauth", handlers.unauth))
    app.add_handler(CommandHandler("authlist", handlers.authlist))
    app.add_handler(CommandHandler("broadcast", handlers.broadcast))
    app.add_handler(CommandHandler("maintenance", handlers.maintenance))

    app.add_handler(MessageHandler(filters.UpdateType.EDITED_MESSAGE, handlers.edited_message_handler))
    app.add_handler(CallbackQueryHandler(handlers.remove_warning_button, pattern=r"remwarn:"))
    app.add_handler(CallbackQueryHandler(handlers.help_button, pattern=r"help"))

    app.run_polling()

if __name__ == "__main__":
    main()
