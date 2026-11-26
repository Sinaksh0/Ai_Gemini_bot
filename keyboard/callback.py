from telegram import Update
from telegram.ext import ContextTypes
from src.data import load_users
from keyboard.keyboards import admin_keyboard, admin_back

async def callback_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer(text='⚙️ در حال پردازش درخواست...', show_alert=False)
    data = query.data

    admin = admin_keyboard()
    back = admin_back()

    if data == "members":
        users = load_users()
        count = len(users)
        message = f'👥 کاربران ثبت‌شده: {count}\n'
        message += '📋 فهرست کاربران\n\n'
        for i, user in enumerate(users, start=1):
            message += f'{i}. {user['Name']} (<code>{user['ID']}</code>) | @{user['username']}\n\n'

        await query.edit_message_text(message, parse_mode='HTML', reply_markup=back)

    elif data == 'back':
        await query.edit_message_text('📋 لیست کاربران آماده است. 👥', reply_markup=admin)

    return
