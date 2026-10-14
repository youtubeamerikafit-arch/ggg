from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import WEBAPP_URL, ADMIN_IDS
from database import create_user_if_not_exists, get_user
from locales import STRINGS

router = Router()

# Default welcome photo (matching a premium gaming design)
WELCOME_PHOTO_URL = "https://images.unsplash.com/photo-1612287230202-1bf1d85d1bdf?q=80&w=1000&auto=format&fit=crop"

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    # Save user to DB
    await create_user_if_not_exists(user_id, username, first_name)
    
    # Determine language (default to 'uz' for now)
    lang = "uz"
    db_user = await get_user(user_id)
    if db_user and "language" in db_user:
        lang = db_user["language"] or "uz"
        
    welcome_text = STRINGS[lang]["welcome"].format(name=first_name)
    
    # Create keyboards matching screenshots
    builder = InlineKeyboardBuilder()
    
    # WebApp Button: Open Mini App
    # We append user_id as query parameter to identify the user easily in the WebApp
    webapp_link = f"{WEBAPP_URL}/?user_id={user_id}"
    builder.button(
        text=STRINGS[lang]["open_webapp"],
        web_app=types.WebAppInfo(url=webapp_link)
    )
    
    # Secondary Buttons
    builder.button(
        text=STRINGS[lang]["news_channel"],
        url="https://t.me/YAKUDZA_UC_NEWS"
    )
    builder.button(
        text=STRINGS[lang]["support"],
        url="https://t.me/yakfast_support"
    )
    
    # Layout: Row 1 = WebApp (Full width), Row 2 = News + Support (50/50 split)
    builder.adjust(1, 2)
    
    # Send welcoming photo with text & keyboard
    try:
        await message.answer_photo(
            photo=WELCOME_PHOTO_URL,
            caption=welcome_text,
            reply_markup=builder.as_markup(),
            parse_mode="Markdown"
        )
    except Exception as e:
        # Fallback to plain text if photo sending fails
        await message.answer(
            text=welcome_text,
            reply_markup=builder.as_markup(),
            parse_mode="Markdown"
        )

    # If user is admin, notify them of their admin status
    if user_id in ADMIN_IDS:
        admin_text = (
            "⚙️ **Admin Panel**\n\n"
            "Siz administrator sifatida ro'yxatdan o'tgansiz.\n"
            "To'lov cheklari va buyurtmalarni ko'rish uchun:\n"
            "`/admin` — admin panel"
        )
        await message.answer(admin_text, parse_mode="Markdown")
