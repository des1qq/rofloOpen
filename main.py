import os
import json
import logging
from pathlib import Path
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# settings
ROOT_DIR = Path(__file__).parent
CONFIG_PATH = ROOT_DIR / "config.json"

# logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# load
def load_config():
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Configuration file not found: {CONFIG_PATH}")
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

config = load_config()
BOT_TOKEN = config["telegram"]["bot_token"]
ALLOWED_USER_ID = config["telegram"]["allowed_user_id"]
ALLOWED_COMMANDS = config["games"]

# handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        logger.warning(f"Unauthorized access attempt by user ID: {update.effective_user.id}")
        return
    await update.message.reply_text("Use /run <game_name> to launch a game.")

async def run_app(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ALLOWED_USER_ID:
        logger.warning(f"Unauthorized command attempt by user ID: {user_id}")
        await update.message.reply_text("Access denied.")
        return

    if not context.args or context.args[0] not in ALLOWED_COMMANDS:
        valid_names = ", ".join(ALLOWED_COMMANDS.keys())
        await update.message.reply_text(f"Specify a valid game: {valid_names}")
        return

    game_alias = context.args[0]
    uri = ALLOWED_COMMANDS[game_alias]

    try:
        os.startfile(uri)
        logger.info(f"Launched game '{game_alias}' for user ID: {user_id}")
        await update.message.reply_text(f"Launching {game_alias}...")
    except OSError as e:
        logger.error(f"Failed to launch '{game_alias}': {e}")
        await update.message.reply_text(f"Error: Steam protocol handler not found.")
    except Exception as e:
        logger.exception("Unexpected error during game launch")
        await update.message.reply_text(f"Error: {str(e)}")


def main():
    logger.info("Initializing bot...")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("run", run_app))
    logger.info("Bot is running.")
    app.run_polling()

if __name__ == "__main__":
    main()