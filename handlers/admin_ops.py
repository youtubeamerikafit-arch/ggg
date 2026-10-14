import os
from datetime import datetime

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import ADMIN_IDS
import database as db
from locales import STRINGS

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


def _admin_menu_text(stats: dict) -> str:
    return (
        "⚙️ **ADMIN PANEL** ⚙️\n\n"
        f"📊 **Statistika:**\n"
        f"👥 Foydalanuvchilar: {stats['total_users']} ta\n"
        f"💰 Umumiy savdo: {stats['total_sales']:,.0f} UZS\n"
        f"💳 Kutilayotgan to'lovlar: {stats['pending_deposits']} ta\n"
        f"🛍️ Kutilayotgan buyurtmalar: {stats['pending_orders']} ta\n\n"
        "Quyidagi tugmalardan foydalaning:"
    )


def _admin_menu_keyboard(stats: dict):
    builder = InlineKeyboardBuilder()
    builder.button(
        text=f"💳 To'lovlar va cheklar ({stats['pending_deposits']})",
        callback_data="admin_deposits",
    )
    builder.button(
        text=f"🛍️ Buyurtmalar ({stats['pending_orders']})",
        callback_data="admin_orders",
    )
    builder.button(text="🔄 Yangilash", callback_data="refresh_stats")
    builder.adjust(1)
    return builder


def _deposit_caption(deposit, user) -> str:
    name = user["first_name"] if user else "Noma'lum"
    username = f"@{user['username']}" if user and user["username"] else "Mavjud emas"
    created = deposit["created_at"] or ""
    try:
        dt = datetime.strptime(str(created).split(".")[0], "%Y-%m-%d %H:%M:%S")
        created = dt.strftime("%d.%m.%Y %H:%M")
    except Exception:
        pass

    return (
        f"💳 **To'lov #{deposit['id']}**\n\n"
        f"👤 Foydalanuvchi: {name} ({username})\n"
        f"🆔 User ID: `{deposit['user_id']}`\n"
        f"💰 Summa: **{deposit['amount']:,.0f} UZS**\n"
        f"📅 Vaqt: {created}\n\n"
        f"Chekni tekshiring va tasdiqlang yoki rad eting."
    )


def _deposit_action_keyboard(deposit_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(text="Tasdiqlash ✅", callback_data=f"approve_dep:{deposit_id}")
    builder.button(text="Rad etish ❌", callback_data=f"reject_dep:{deposit_id}")
    builder.button(text="⬅️ Ro'yxatga qaytish", callback_data="admin_deposits")
    builder.adjust(2, 1)
    return builder


def _order_caption(order) -> str:
    name = order["first_name"] if order["first_name"] else "Noma'lum"
    username = f"@{order['username']}" if order["username"] else "Mavjud emas"
    created = order["created_at"] or ""
    try:
        dt = datetime.strptime(str(created).split(".")[0], "%Y-%m-%d %H:%M:%S")
        created = dt.strftime("%d.%m.%Y %H:%M")
    except Exception:
        pass

    return (
        f"🛍️ **Buyurtma #{order['id']}**\n\n"
        f"👤 Foydalanuvchi: {name} ({username})\n"
        f"🆔 User ID: `{order['user_id']}`\n"
        f"📦 Mahsulot: {order['package_name']}\n"
        f"💰 Narxi: {order['price']:,.0f} UZS\n"
        f"🎯 Qabul qiluvchi: `{order['target_username']}`\n"
        f"📅 Vaqt: {created}"
    )


def _order_action_keyboard(order_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(text="Bajarildi ✅", callback_data=f"complete_ord:{order_id}")
    builder.button(text="Bekor qilish ❌", callback_data=f"cancel_ord:{order_id}")
    builder.button(text="⬅️ Ro'yxatga qaytish", callback_data="admin_orders")
    builder.adjust(2, 1)
    return builder


async def _send_deposit_review(bot, chat_id: int, deposit, user):
    caption = _deposit_caption(deposit, user)
    keyboard = _deposit_action_keyboard(deposit["id"])
    receipt_path = deposit["receipt_photo_id"]

    if receipt_path and os.path.exists(receipt_path):
        await bot.send_photo(
            chat_id=chat_id,
            photo=FSInputFile(receipt_path),
            caption=caption,
            reply_markup=keyboard.as_markup(),
            parse_mode="Markdown",
        )
    else:
        await bot.send_message(
            chat_id=chat_id,
            text=caption + "\n\n⚠️ Chek fayli topilmadi.",
            reply_markup=keyboard.as_markup(),
            parse_mode="Markdown",
        )


@router.message(Command("admin"))
async def cmd_admin(message: types.Message):
    if not is_admin(message.from_user.id):
        return

    stats = await db.get_admin_stats()
    await message.answer(
        _admin_menu_text(stats),
        reply_markup=_admin_menu_keyboard(stats).as_markup(),
        parse_mode="Markdown",
    )


@router.callback_query(F.data == "refresh_stats")
async def cb_refresh_stats(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Siz admin emassiz!", show_alert=True)
        return

    stats = await db.get_admin_stats()
    try:
        await callback.message.edit_text(
            _admin_menu_text(stats),
            reply_markup=_admin_menu_keyboard(stats).as_markup(),
            parse_mode="Markdown",
        )
    except Exception:
        await callback.message.answer(
            _admin_menu_text(stats),
            reply_markup=_admin_menu_keyboard(stats).as_markup(),
            parse_mode="Markdown",
        )
    await callback.answer("Yangilandi!")


@router.callback_query(F.data == "admin_back")
async def cb_admin_back(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Siz admin emassiz!", show_alert=True)
        return

    stats = await db.get_admin_stats()
    try:
        await callback.message.edit_text(
            _admin_menu_text(stats),
            reply_markup=_admin_menu_keyboard(stats).as_markup(),
            parse_mode="Markdown",
        )
    except Exception:
        await callback.message.answer(
            _admin_menu_text(stats),
            reply_markup=_admin_menu_keyboard(stats).as_markup(),
            parse_mode="Markdown",
        )
    await callback.answer()


@router.callback_query(F.data == "admin_deposits")
async def cb_admin_deposits(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Siz admin emassiz!", show_alert=True)
        return

    deposits = await db.get_pending_deposits()
    if not deposits:
        await callback.answer("Kutilayotgan to'lov yo'q.", show_alert=True)
        return

    builder = InlineKeyboardBuilder()
    for deposit in deposits:
        name = deposit["first_name"] or "User"
        builder.button(
            text=f"#{deposit['id']} — {deposit['amount']:,.0f} UZS — {name}",
            callback_data=f"view_dep:{deposit['id']}",
        )
    builder.button(text="⬅️ Admin panel", callback_data="admin_back")
    builder.adjust(1)

    text = (
        f"💳 **Kutilayotgan to'lovlar** ({len(deposits)} ta)\n\n"
        "Chekni ko'rish uchun to'lovni tanlang:"
    )

    try:
        await callback.message.edit_text(
            text,
            reply_markup=builder.as_markup(),
            parse_mode="Markdown",
        )
    except Exception:
        await callback.message.answer(
            text,
            reply_markup=builder.as_markup(),
            parse_mode="Markdown",
        )
    await callback.answer()


@router.callback_query(F.data.startswith("view_dep:"))
async def cb_view_deposit(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Siz admin emassiz!", show_alert=True)
        return

    deposit_id = int(callback.data.split(":")[1])
    deposit = await db.get_deposit(deposit_id)
    if not deposit:
        await callback.answer("To'lov topilmadi!", show_alert=True)
        return

    if deposit["status"] != "pending":
        await callback.answer(f"Bu to'lov allaqachon '{deposit['status']}' holatida!", show_alert=True)
        return

    user = await db.get_user(deposit["user_id"])
    await _send_deposit_review(callback.bot, callback.from_user.id, deposit, user)
    await callback.answer("Chek yuborildi!")


@router.callback_query(F.data == "admin_orders")
async def cb_admin_orders(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Siz admin emassiz!", show_alert=True)
        return

    orders = await db.get_pending_orders()
    if not orders:
        await callback.answer("Kutilayotgan buyurtma yo'q.", show_alert=True)
        return

    builder = InlineKeyboardBuilder()
    for order in orders:
        name = order["first_name"] or "User"
        builder.button(
            text=f"#{order['id']} — {order['package_name']} — {name}",
            callback_data=f"view_ord:{order['id']}",
        )
    builder.button(text="⬅️ Admin panel", callback_data="admin_back")
    builder.adjust(1)

    text = (
        f"🛍️ **Kutilayotgan buyurtmalar** ({len(orders)} ta)\n\n"
        "Batafsil ko'rish uchun buyurtmani tanlang:"
    )

    try:
        await callback.message.edit_text(
            text,
            reply_markup=builder.as_markup(),
            parse_mode="Markdown",
        )
    except Exception:
        await callback.message.answer(
            text,
            reply_markup=builder.as_markup(),
            parse_mode="Markdown",
        )
    await callback.answer()


@router.callback_query(F.data.startswith("view_ord:"))
async def cb_view_order(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Siz admin emassiz!", show_alert=True)
        return

    order_id = int(callback.data.split(":")[1])
    order = await db.get_order(order_id)
    if not order:
        await callback.answer("Buyurtma topilmadi!", show_alert=True)
        return

    if order["status"] != "pending":
        await callback.answer(f"Bu buyurtma allaqachon '{order['status']}' holatida!", show_alert=True)
        return

    user = await db.get_user(order["user_id"])
    order_with_user = dict(order)
    order_with_user["first_name"] = user["first_name"] if user else None
    order_with_user["username"] = user["username"] if user else None

    await callback.message.answer(
        _order_caption(order_with_user),
        reply_markup=_order_action_keyboard(order_id).as_markup(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("approve_dep:"))
async def cb_approve_deposit(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Siz admin emassiz!", show_alert=True)
        return

    deposit_id = int(callback.data.split(":")[1])
    deposit = await db.get_deposit(deposit_id)

    if not deposit:
        await callback.answer("To'lov topilmadi!", show_alert=True)
        return

    if deposit["status"] != "pending":
        await callback.answer(f"Bu to'lov allaqachon '{deposit['status']}' holatida!", show_alert=True)
        return

    await db.update_deposit_status(deposit_id, "approved")
    await db.add_user_balance(deposit["user_id"], deposit["amount"])

    edited_text = callback.message.caption or callback.message.text or ""
    edited_text += f"\n\n✅ **Tasdiqlandi!** (Admin: @{callback.from_user.username or callback.from_user.id})"

    try:
        await callback.message.edit_reply_markup(reply_markup=None)
        if callback.message.photo:
            await callback.message.edit_caption(caption=edited_text, parse_mode="Markdown")
        else:
            await callback.message.edit_text(text=edited_text, parse_mode="Markdown")
    except Exception as e:
        print("Error updating admin message:", e)

    user_lang = "uz"
    db_user = await db.get_user(deposit["user_id"])
    if db_user and "language" in db_user:
        user_lang = db_user["language"] or "uz"

    user_msg = STRINGS[user_lang]["deposit_approved"].format(amount=deposit["amount"])
    try:
        await callback.bot.send_message(chat_id=deposit["user_id"], text=user_msg)
    except Exception as e:
        print(f"Error sending message to user {deposit['user_id']}:", e)

    await callback.answer("To'lov tasdiqlandi! Balansga tushdi ✅")


@router.callback_query(F.data.startswith("reject_dep:"))
async def cb_reject_deposit(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Siz admin emassiz!", show_alert=True)
        return

    deposit_id = int(callback.data.split(":")[1])
    deposit = await db.get_deposit(deposit_id)

    if not deposit:
        await callback.answer("To'lov topilmadi!", show_alert=True)
        return

    if deposit["status"] != "pending":
        await callback.answer(f"Bu to'lov allaqachon '{deposit['status']}' holatida!", show_alert=True)
        return

    await db.update_deposit_status(deposit_id, "rejected")

    edited_text = callback.message.caption or callback.message.text or ""
    edited_text += f"\n\n❌ **Rad etildi!** (Admin: @{callback.from_user.username or callback.from_user.id})"

    try:
        await callback.message.edit_reply_markup(reply_markup=None)
        if callback.message.photo:
            await callback.message.edit_caption(caption=edited_text, parse_mode="Markdown")
        else:
            await callback.message.edit_text(text=edited_text, parse_mode="Markdown")
    except Exception as e:
        print("Error updating admin message:", e)

    user_lang = "uz"
    db_user = await db.get_user(deposit["user_id"])
    if db_user and "language" in db_user:
        user_lang = db_user["language"] or "uz"

    user_msg = STRINGS[user_lang]["deposit_rejected"]
    try:
        await callback.bot.send_message(chat_id=deposit["user_id"], text=user_msg)
    except Exception as e:
        print(f"Error sending message to user {deposit['user_id']}:", e)

    await callback.answer("To'lov rad etildi!")


@router.callback_query(F.data.startswith("complete_ord:"))
async def cb_complete_order(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Siz admin emassiz!", show_alert=True)
        return

    order_id = int(callback.data.split(":")[1])
    order = await db.get_order(order_id)

    if not order:
        await callback.answer("Buyurtma topilmadi!", show_alert=True)
        return

    if order["status"] != "pending":
        await callback.answer(f"Bu buyurtma allaqachon '{order['status']}' holatida!", show_alert=True)
        return

    await db.update_order_status(order_id, "completed")

    edited_text = callback.message.text or ""
    edited_text += f"\n\n✅ **Bajarildi!** (Admin: @{callback.from_user.username or callback.from_user.id})"

    try:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.edit_text(text=edited_text, parse_mode="Markdown")
    except Exception as e:
        print("Error updating admin message:", e)

    user_lang = "uz"
    db_user = await db.get_user(order["user_id"])
    if db_user and "language" in db_user:
        user_lang = db_user["language"] or "uz"

    user_msg = STRINGS[user_lang]["order_completed"].format(
        package_name=order["package_name"],
        target=order["target_username"],
    )
    try:
        await callback.bot.send_message(chat_id=order["user_id"], text=user_msg)
    except Exception as e:
        print(f"Error sending message to user {order['user_id']}:", e)

    await callback.answer("Buyurtma bajarildi!")


@router.callback_query(F.data.startswith("cancel_ord:"))
async def cb_cancel_order(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Siz admin emassiz!", show_alert=True)
        return

    order_id = int(callback.data.split(":")[1])
    order = await db.get_order(order_id)

    if not order:
        await callback.answer("Buyurtma topilmadi!", show_alert=True)
        return

    if order["status"] != "pending":
        await callback.answer(f"Bu buyurtma allaqachon '{order['status']}' holatida!", show_alert=True)
        return

    await db.update_order_status(order_id, "cancelled")
    await db.add_user_balance(order["user_id"], order["price"])

    edited_text = callback.message.text or ""
    edited_text += f"\n\n❌ **Bekor qilindi!** (Mablag' qaytarildi) (Admin: @{callback.from_user.username or callback.from_user.id})"

    try:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.edit_text(text=edited_text, parse_mode="Markdown")
    except Exception as e:
        print("Error updating admin message:", e)

    user_lang = "uz"
    db_user = await db.get_user(order["user_id"])
    if db_user and "language" in db_user:
        user_lang = db_user["language"] or "uz"

    user_msg = STRINGS[user_lang]["order_cancelled"].format(package_name=order["package_name"])
    try:
        await callback.bot.send_message(chat_id=order["user_id"], text=user_msg)
    except Exception as e:
        print(f"Error sending message to user {order['user_id']}:", e)

    await callback.answer("Buyurtma bekor qilindi, pul qaytarildi!")
