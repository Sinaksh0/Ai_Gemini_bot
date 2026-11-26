import io
from telegram import Update
from telegram.ext import ContextTypes
from google import genai
from google.genai import types
from keyboard.keyboards import admin_keyboard
from src.api import GEN_AI, ADMIN_ID
from src.data import load_users, upload_github

client = genai.Client(api_key=GEN_AI)
chats = {}


def check_user(name: str, chat_id: int, user_name):
    users = load_users()
    flag = True
    for id in users:
        if chat_id == id['ID']:
            flag = False
            break
        
    if flag:
        users.append({
            "Name": name,
            "ID": chat_id,
            "username": user_name
        })
        upload_github(users)
    return

async def reaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.set_message_reaction(chat_id=update.message.chat_id,
        message_id=update.message.message_id,
        reaction=['\U0001f44d']
    )
    return

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await reaction(update, context)
    name = update.effective_user.full_name
    chat_id = update.effective_chat.id
    user_name = update.effective_user.username or None

    text = f"""
سلام {name} عزیز 👋✨

خوش اومدی! دستیار هوشمندت برای فهمیدن سریع‌تر درس‌ها یا جزوه‌ها و یا هر سوالی که داری 📚🤖

اینجا میتونی:
📄 فایل‌های درسی (مثل PDF یا جزوه) و 🖼 عکس از اسلاید، کتاب یا تخته بفرستی تا برات ساده، منظم و دسته‌بندی‌شده خلاصه و تحلیل بشن.
💬 هر سوال متنی یا ابهامی هم که داشتی بپرسی تا مرحله‌به‌مرحله توضیح بدم.

همین الان فایلت، عکست یا هر سوالی داری بفرست تا شروع کنیم! 🚀
    """

    if chat_id == ADMIN_ID:
        keyboard = admin_keyboard()
    else:
        keyboard = None

    await update.message.reply_text(text, reply_markup=keyboard)
    check_user(name, chat_id, user_name)
    return

async def handle_study_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message:
        return

    caption = message.caption or (
        "این محتوای درسی را به زبان ساده و منظم خلاصه کن، "
        "مفاهیم و فرمول‌ها/نکات اصلی را دسته‌بندی کن و در پایان ۵ نکته مهم بنویس."
    )

    user_instruction = f"""
        با لحن صمیمی و دوستانه صحبت کن با کاربر
        اسم کاربر: {message.from_user.first_name or "ناشناس"}
        ⚠️ قوانین مهم نگارشی:
        1. به هیچ وجه از علامت ستاره (* یا **) برای بولد کردن یا لیست‌سازی استفاده نکن.
        2. اگر خواسته‌ایی چیزی را برجسته کنی یا تیتربندی کنی، از اعداد یا ایموجی‌ها استفاده کن و به جای ستاره از تگ‌های HTML مثل <b>متن</b> بهره ببر.
        3. برای ریاضی به فرمتی بده تا بشه در تلگرام استفاده کرد.
        4. خروجی را کاملاً مناسب خواندن در پیام‌رسان تلگرام بنویس. به هیچ وجه از کدها و نمادهای LaTeX مثل علامت $، $$، \frac، \log یا \text استفاده نکن. فرمول‌ها، روابط ریاضی و نمادهای پیچیدگی الگوریتمی را به صورت متن ساده و خوانا بنویس؛ مثلاً به جای فرمول کسری بنویس: mid = (low + high) / 2 و به جای عبارت ریاضی بنویس: O(log n) و T(n) = n.
        5. اگه خواستی یک نمونه کد به کاربر بدی اون کد رو داخل: <pre>....</pre> بزار. مثل: <pre>print("Hello World")</pre>
    """

    if update.effective_user.id not in chats:
        chats[update.effective_user.id] = client.chats.create(
            model='gemini-3.5-flash-lite',
            config={"system_instruction": user_instruction},
        )

    chat = chats[update.effective_user.id]

    status_msg = await message.reply_text(
        "📚 در حال دریافت پاسخ..."
    )

    buf = None
    try:
        if message.text:
            await reaction(update, context)
            response = chat.send_message(message.text)

        elif message.photo:
            await reaction(update, context)
            buf = io.BytesIO()
            photo = message.photo[-1]
            if photo.file_size and photo.file_size > 15 * 1024 * 1024:
                await status_msg.edit_text(
                    "⚠️ حجم عکس زیاد است. لطفاً عکس زیر ۱۵ مگابایت بفرستید."
                )
                return

            tg_file = await photo.get_file()
            await tg_file.download_to_memory(out=buf)

            image_part = types.Part.from_bytes(
                data=buf.getvalue(),
                mime_type="image/jpeg",
            )

            response = chat.send_message([image_part, caption])

        elif message.document:
            await reaction(update, context)
            buf = io.BytesIO()
            doc = message.document
            if doc.file_size and doc.file_size > 15 * 1024 * 1024:
                await status_msg.edit_text(
                    "⚠️ حجم فایل زیاد است. لطفاً فایل زیر ۱۵ مگابایت بفرستید."
                )
                return

            tg_file = await doc.get_file()
            await tg_file.download_to_memory(out=buf)
            doc_part = types.Part.from_bytes(
                data=buf.getvalue(),
                mime_type=doc.mime_type or "application/pdf",
            )

            response = chat.send_message([doc_part, caption])

        else:
            await status_msg.edit_text("⚠️ لطفاً یک عکس یا فایل PDF ارسال کنید.")
            return

        await status_msg.delete()
        await update.message.reply_text(response.text or "⚠️ پاسخی دریافت نشد.", parse_mode="HTML")

    except Exception as e:
        await status_msg.edit_text(f"❌ خطا در تحلیل محتوا: {str(e)}")

    finally:
        if buf is not None:
            buf.close()
