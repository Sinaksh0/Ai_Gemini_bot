from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def admin_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="📊 لیست کاربران", callback_data="members")]
    ]

    return InlineKeyboardMarkup(keyboard)

def admin_back() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton('🔙 بازگشت', callback_data='back')]
    ]

    return InlineKeyboardMarkup(keyboard)
