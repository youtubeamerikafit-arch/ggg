import asyncio
import os
import base64
import hashlib
import socket
import time
from datetime import datetime
from pathlib import Path
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.types import FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

import config
import database as db
import case_game
from handlers import bot_start, admin_ops
from locales import STRINGS

# Ensure receipts folder exists
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
RECEIPTS_DIR = os.path.join(BASE_DIR, "receipts")
os.makedirs(RECEIPTS_DIR, exist_ok=True)

# Global bot reference for API handlers
bot: Bot = None


def find_available_port(start_port: int, host: str = "0.0.0.0", max_attempts: int = 20) -> int:
    """Return the first free TCP port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind((host, port))
                return port
            except OSError:
                continue
    raise RuntimeError(f"No free port found in range {start_port}-{start_port + max_attempts - 1}")


# AIOHTTP API Request Handlers

async def handle_index(request):
    """Serve the WebApp index file."""
    return web.FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

async def get_user_api(request):
    """Fetch user profile information."""
    try:
        user_id_str = request.query.get('user_id')
        if not user_id_str or not user_id_str.isdigit():
            return web.json_response({"detail": "Invalid user_id parameter"}, status=400)
            
        user_id = int(user_id_str)
        user = await db.get_user(user_id)
        if not user:
            # Create user if they don't exist (e.g., opened webapp directly)
            await db.create_user_if_not_exists(user_id, "", "Foydalanuvchi")
            user = await db.get_user(user_id)
            
        # Get completed orders count for stats
        orders = await db.get_user_orders(user_id)
        completed_orders = sum(1 for o in orders if o["status"] == 'completed')
        
        # Format registration date
        joined_at_formatted = "26.07.2026"
        if user["joined_at"]:
            try:
                # SQLite timestamp parsing
                dt = datetime.strptime(user["joined_at"].split('.')[0], "%Y-%m-%d %H:%M:%S")
                joined_at_formatted = dt.strftime("%d.%m.%Y")
            except Exception:
                joined_at_formatted = str(user["joined_at"])
                
        settings = {
            "card_number": config.CARD_NUMBER,
            "card_owner": config.CARD_OWNER,
            "news_link": config.NEWS_LINK,
            "support_link": config.SUPPORT_LINK,
        }
        
        stars_balance = 25.0
        try:
            stars_balance = float(user["stars_balance"]) if "stars_balance" in user.keys() and user["stars_balance"] is not None else 25.0
        except Exception:
            stars_balance = 25.0

        inventory = await db.get_user_inventory(user_id)
        
        return web.json_response({
            "user_id": user["user_id"],
            "username": user["username"],
            "first_name": user["first_name"],
            "balance": user["balance"],
            "stars_balance": stars_balance,
            "inventory_count": len(inventory),
            "completed_orders": completed_orders,
            "joined_at_formatted": joined_at_formatted,
            "settings": settings
        })
    except Exception as e:
        print("API Error in get_user_api:", e)
        return web.json_response({"detail": str(e)}, status=500)

async def get_packages_api(request):
    """Retrieve catalog items (Stars & Premium)."""
    try:
        packages = await db.get_packages()
        return web.json_response([dict(p) for p in packages])
    except Exception as e:
        print("API Error in get_packages_api:", e)
        return web.json_response({"detail": str(e)}, status=500)

async def get_history_api(request):
    """Fetch user deposit and purchase orders history."""
    try:
        user_id_str = request.query.get('user_id')
        if not user_id_str or not user_id_str.isdigit():
            return web.json_response({"detail": "Invalid user_id parameter"}, status=400)
            
        user_id = int(user_id_str)
        orders = await db.get_user_orders(user_id)
        deposits = await db.get_user_deposits(user_id)
        
        return web.json_response({
            "orders": [dict(o) for o in orders],
            "deposits": [dict(d) for d in deposits]
        })
    except Exception as e:
        print("API Error in get_history_api:", e)
        return web.json_response({"detail": str(e)}, status=500)

async def post_deposit_api(request):
    """Handle balance topup requests and upload payment receipt."""
    try:
        data = await request.json()
        user_id = int(data.get('user_id'))
        amount = float(data.get('amount'))
        payment_method = data.get('payment_method', 'manual')
        receipt_base64 = data.get('receipt_base64')
        file_name = data.get('file_name', 'receipt.png')
        
        if not user_id or not amount or not receipt_base64:
            return web.json_response({"detail": "Yetarli ma'lumot kiritilmagan!"}, status=400)
            
        # Decode and save screenshot
        header, encoded = receipt_base64.split(",", 1) if "," in receipt_base64 else (None, receipt_base64)
        file_data = base64.b64decode(encoded)
        
        # Save temp file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ext = file_name.split(".")[-1] if "." in file_name else "png"
        filepath = os.path.join(RECEIPTS_DIR, f"receipt_{user_id}_{timestamp}.{ext}")
        with open(filepath, "wb") as f:
            f.write(file_data)
            
        # Store in DB
        deposit_id = await db.create_deposit_request(user_id, amount, payment_method, filepath)
        
        # Notify Admins via Bot
        user = await db.get_user(user_id)
        user_display_name = user["first_name"] if user else "Noma'lum"
        username_str = f"@{user['username']}" if user and user["username"] else "Mavjud emas"
        
        notify_msg = STRINGS["uz"]["deposit_request_notify"].format(
            name=f"{user_display_name} ({username_str})",
            user_id=user_id,
            amount=amount,
            method=payment_method.upper(),
            time=datetime.now().strftime("%d.%m.%Y %H:%M")
        )
        
        # Create action buttons
        builder = InlineKeyboardBuilder()
        builder.button(text="Tasdiqlash ✅", callback_data=f"approve_dep:{deposit_id}")
        builder.button(text="Rad etish ❌", callback_data=f"reject_dep:{deposit_id}")
        builder.adjust(2)
        
        # Send receipt photo to all configured admin IDs
        for admin_id in config.ADMIN_IDS:
            try:
                photo_file = FSInputFile(filepath)
                await bot.send_photo(
                    chat_id=admin_id,
                    photo=photo_file,
                    caption=notify_msg,
                    reply_markup=builder.as_markup(),
                    parse_mode="Markdown"
                )
            except Exception as e:
                print(f"Failed to notify admin {admin_id} about deposit:", e)
                
        return web.json_response({"status": "pending", "deposit_id": deposit_id})
    except Exception as e:
        print("API Error in post_deposit_api:", e)
        return web.json_response({"detail": str(e)}, status=500)

async def _verify_admin_key(request):
    key = request.query.get('key') or request.headers.get('X-Admin-Key')
    return key == config.ADMIN_PANEL_KEY


async def get_admin_deposits_api(request):
    """Return pending deposits for the browser admin panel."""
    try:
        if not await _verify_admin_key(request):
            return web.json_response({"detail": "Unauthorized"}, status=401)

        deposits = await db.get_pending_deposits()
        result = []
        for item in deposits:
            result.append({
                "id": item["id"],
                "user_id": item["user_id"],
                "user_name": item["first_name"] or item["username"] or "Noma'lum",
                "amount": item["amount"],
                "payment_method": item["payment_method"],
                "created_at": str(item["created_at"]),
            })
        return web.json_response(result)
    except Exception as e:
        print("Admin deposits API error:", e)
        return web.json_response({"detail": str(e)}, status=500)


async def get_admin_receipt_api(request):
    """Serve a deposit receipt image to the browser admin panel."""
    try:
        if not await _verify_admin_key(request):
            return web.json_response({"detail": "Unauthorized"}, status=401)

        deposit_id = int(request.match_info['deposit_id'])
        deposit = await db.get_deposit(deposit_id)
        if not deposit or not deposit["receipt_photo_id"]:
            return web.json_response({"detail": "Receipt not found"}, status=404)

        receipt_path = deposit["receipt_photo_id"]
        if not os.path.exists(receipt_path):
            return web.json_response({"detail": "Receipt file missing"}, status=404)

        return web.FileResponse(receipt_path)
    except Exception as e:
        print("Admin receipt API error:", e)
        return web.json_response({"detail": str(e)}, status=500)


async def post_admin_deposit_action_api(request):
    """Approve or reject a deposit from the browser admin panel."""
    try:
        if not await _verify_admin_key(request):
            return web.json_response({"detail": "Unauthorized"}, status=401)

        deposit_id = int(request.match_info['deposit_id'])
        action = request.match_info['action']
        deposit = await db.get_deposit(deposit_id)
        if not deposit:
            return web.json_response({"detail": "Deposit not found"}, status=404)
        if deposit["status"] != "pending":
            return web.json_response({"detail": "Deposit already processed"}, status=400)

        if action == 'approve':
            await db.update_deposit_status(deposit_id, 'approved')
            await db.add_user_balance(deposit["user_id"], deposit["amount"])
            await bot.send_message(
                chat_id=deposit["user_id"],
                text=STRINGS["uz"]["deposit_approved"].format(amount=deposit["amount"]),
            )
            return web.json_response({"message": "To'lov tasdiqlandi"})
        elif action == 'reject':
            await db.update_deposit_status(deposit_id, 'rejected')
            await bot.send_message(
                chat_id=deposit["user_id"],
                text=STRINGS["uz"]["deposit_rejected"],
            )
            return web.json_response({"message": "To'lov rad etildi"})
        else:
            return web.json_response({"detail": "Invalid action"}, status=400)
    except Exception as e:
        print("Admin deposit action error:", e)
        return web.json_response({"detail": str(e)}, status=500)


async def post_purchase_api(request):
    """Handle product purchases using the wallet balance."""
    try:
        data = await request.json()
        user_id = int(data.get('user_id'))
        package_id = int(data.get('package_id'))
        target_username = data.get('target_username', '').strip()
        
        if not user_id or not package_id or not target_username:
            return web.json_response({"detail": "Ma'lumotlar to'liq kiritilmagan!"}, status=400)
            
        # Fetch user and package
        user = await db.get_user(user_id)
        pkg = await db.get_package(package_id)
        
        if not user:
            return web.json_response({"detail": "Foydalanuvchi topilmadi!"}, status=404)
        if not pkg:
            return web.json_response({"detail": "Mahsulot topilmadi!"}, status=404)
            
        # Check balance
        if user["balance"] < pkg["price"]:
            return web.json_response({"detail": "Balansda mablag' yetarli emas!"}, status=400)
            
        # Deduct balance & create order
        await db.deduct_user_balance(user_id, pkg["price"])
        order_id = await db.create_order(user_id, package_id, target_username, pkg["price"])
        
        # Get updated user info
        updated_user = await db.get_user(user_id)
        new_balance = updated_user["balance"]
        
        # Notify Admins via Bot
        user_display_name = user["first_name"]
        username_str = f"@{user['username']}" if user['username'] else "Mavjud emas"
        
        notify_msg = STRINGS["uz"]["order_request_notify"].format(
            name=f"{user_display_name} ({username_str})",
            user_id=user_id,
            package_name=pkg["name"],
            price=pkg["price"],
            target=target_username,
            time=datetime.now().strftime("%d.%m.%Y %H:%M")
        )
        
        builder = InlineKeyboardBuilder()
        builder.button(text="Bajarildi ✅", callback_data=f"complete_ord:{order_id}")
        builder.button(text="Bekor qilish ❌ (Qaytarish)", callback_data=f"cancel_ord:{order_id}")
        builder.adjust(2)
        
        # Send order alert to admins
        for admin_id in config.ADMIN_IDS:
            try:
                await bot.send_message(
                    chat_id=admin_id,
                    text=notify_msg,
                    reply_markup=builder.as_markup(),
                    parse_mode="Markdown"
                )
            except Exception as e:
                print(f"Failed to notify admin {admin_id} about purchase:", e)
                
        return web.json_response({
            "status": "pending",
            "order_id": order_id,
            "new_balance": new_balance
        })
    except Exception as e:
        print("API Error in post_purchase_api:", e)
        return web.json_response({"detail": str(e)}, status=500)


async def post_create_payment_link_api(request):
    """Generate automated Click or Payme checkout URL."""
    try:
        data = await request.json()
        user_id = int(data.get('user_id'))
        amount = float(data.get('amount'))
        payment_method = data.get('payment_method') # 'click_auto' or 'payme_auto'
        
        if not user_id or not amount or not payment_method:
            return web.json_response({"detail": "Ma'lumotlar to'liq kiritilmagan!"}, status=400)
            
        # Verify billing keys are loaded
        if payment_method == 'click_auto' and not config.CLICK_SECRET_KEY:
            return web.json_response({"detail": "Click to'lov tizimi sozlanmagan!"}, status=400)
        if payment_method == 'payme_auto' and not config.PAYME_SECRET_KEY:
            return web.json_response({"detail": "Payme to'lov tizimi sozlanmagan!"}, status=400)

        # Create a pending deposit record
        deposit_id = await db.create_empty_deposit(user_id, amount, payment_method)
        
        payment_url = ""
        if payment_method == 'click_auto':
            payment_url = (
                f"https://my.click.uz/services/pay"
                f"?service_id={config.CLICK_SERVICE_ID}"
                f"&merchant_id={config.CLICK_MERCHANT_ID}"
                f"&amount={amount}"
                f"&transaction_param={deposit_id}"
                f"&return_url={config.WEBAPP_URL}"
            )
        elif payment_method == 'payme_auto':
            # Payme expects amount in tiyins
            amount_tiyins = int(amount * 100)
            payload = f"m={config.PAYME_MERCHANT_ID};ac.deposit_id={deposit_id};a={amount_tiyins}"
            encoded = base64.b64encode(payload.encode()).decode()
            payment_url = f"https://checkout.paycom.uz/{encoded}"
            
        return web.json_response({
            "payment_url": payment_url,
            "deposit_id": deposit_id
        })
    except Exception as e:
        print("API Error in post_create_payment_link_api:", e)
        return web.json_response({"detail": str(e)}, status=500)


async def post_click_webhook(request):
    """Handle Click payment callbacks (Prepare and Complete)."""
    try:
        data = await request.post()
        click_trans_id = data.get('click_trans_id')
        service_id = data.get('service_id')
        click_paydoc_id = data.get('click_paydoc_id')
        merchant_trans_id = data.get('merchant_trans_id')
        amount = data.get('amount')
        action = data.get('action') # 0 = Prepare, 1 = Complete
        error = data.get('error')
        sign_time = data.get('sign_time')
        sign_string = data.get('sign_string')

        if not all([click_trans_id, service_id, merchant_trans_id, amount, action, error, sign_time, sign_string]):
            return web.json_response({"error": -8, "error_note": "MISSING_PARAMETERS"})

        # Calculate signatures
        if action == '0':
            sign_src = f"{click_trans_id}{service_id}{config.CLICK_SECRET_KEY}{merchant_trans_id}{amount}{action}{sign_time}{error}"
        else:
            sign_src = f"{click_trans_id}{service_id}{config.CLICK_SECRET_KEY}{merchant_trans_id}{merchant_trans_id}{amount}{action}{sign_time}{error}"
        
        calculated_sign = hashlib.md5(sign_src.encode()).hexdigest()

        if calculated_sign != sign_string:
            return web.json_response({"error": -1, "error_note": "SIGN_CHECK_FAILED"})

        deposit_id = int(merchant_trans_id)
        deposit = await db.get_deposit(deposit_id)
        
        if not deposit:
            return web.json_response({"error": -5, "error_note": "ORDER_NOT_FOUND"})

        if abs(float(deposit["amount"]) - float(amount)) > 0.01:
            return web.json_response({"error": -2, "error_note": "INCORRECT_AMOUNT"})

        if action == '0': # Prepare
            if deposit["status"] != 'pending':
                return web.json_response({"error": -4, "error_note": "ORDER_ALREADY_PAID"})
            
            await db.update_deposit_click_trans(deposit_id, click_trans_id)
            return web.json_response({
                "click_trans_id": click_trans_id,
                "merchant_trans_id": merchant_trans_id,
                "error": 0,
                "error_note": "Success"
            })
            
        elif action == '1': # Complete
            if deposit["status"] == 'approved':
                return web.json_response({
                    "click_trans_id": click_trans_id,
                    "merchant_trans_id": merchant_trans_id,
                    "merchant_prepare_id": merchant_trans_id,
                    "error": 0,
                    "error_note": "Success"
                })
                
            if deposit["status"] != 'pending':
                return web.json_response({"error": -9, "error_note": "ORDER_ALREADY_CANCELLED"})

            # Credit user balance
            await db.update_deposit_status(deposit_id, 'approved')
            await db.add_user_balance(deposit["user_id"], deposit["amount"])

            # Notify User
            user_msg = f"✅ Sizning hisobingiz Click orqali {deposit['amount']:,} UZS ga to'ldirildi! 💸"
            try:
                await bot.send_message(chat_id=deposit["user_id"], text=user_msg)
            except Exception as e:
                print("Error notifying user of auto click deposit:", e)

            return web.json_response({
                "click_trans_id": click_trans_id,
                "merchant_trans_id": merchant_trans_id,
                "merchant_prepare_id": merchant_trans_id,
                "error": 0,
                "error_note": "Success"
            })
    except Exception as e:
        print("Click Webhook Error:", e)
        return web.json_response({"error": -9, "error_note": f"SYSTEM_ERROR: {str(e)}"})


async def post_payme_webhook(request):
    """Handle Payme JSON-RPC 2.0 Webhook request."""
    try:
        # Verify Basic Authentication
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Basic '):
            return web.json_response({"jsonrpc": "2.0", "error": {"code": -32504, "message": "Unauthorized"}, "id": None})
        
        encoded = auth_header.split(' ', 1)[1]
        decoded = base64.b64decode(encoded).decode()
        if ':' not in decoded:
            return web.json_response({"jsonrpc": "2.0", "error": {"code": -32504, "message": "Unauthorized"}, "id": None})
        
        username, password = decoded.split(':', 1)
        if password != config.PAYME_SECRET_KEY:
            return web.json_response({"jsonrpc": "2.0", "error": {"code": -32504, "message": "Unauthorized"}, "id": None})

        data = await request.json()
        method = data.get('method')
        params = data.get('params', {})
        request_id = data.get('id')

        if method == 'CheckPerformTransaction':
            account = params.get('account', {})
            deposit_id_str = account.get('deposit_id')
            amount = params.get('amount')

            if not deposit_id_str or not str(deposit_id_str).isdigit():
                return web.json_response({"jsonrpc": "2.0", "error": {"code": -31050, "message": {"uz": "Tranzaksiya topilmadi", "ru": "Транзакция не найдена"}}, "id": request_id})

            deposit_id = int(deposit_id_str)
            deposit = await db.get_deposit(deposit_id)
            if not deposit:
                return web.json_response({"jsonrpc": "2.0", "error": {"code": -31050, "message": {"uz": "To'lov topilmadi", "ru": "Платеж не найден"}}, "id": request_id})

            if int(deposit["amount"] * 100) != int(amount):
                return web.json_response({"jsonrpc": "2.0", "error": {"code": -31001, "message": {"uz": "Noto'g'ri summa", "ru": "Неверная сумма"}}, "id": request_id})

            if deposit["status"] != 'pending':
                return web.json_response({"jsonrpc": "2.0", "error": {"code": -31099, "message": {"uz": "To'lov allaqachon bajarilgan", "ru": "Платеж уже обработан"}}, "id": request_id})

            return web.json_response({"jsonrpc": "2.0", "result": {"allow": True}, "id": request_id})

        elif method == 'CreateTransaction':
            account = params.get('account', {})
            deposit_id_str = account.get('deposit_id')
            amount = params.get('amount')
            payme_trans_id = params.get('id')
            payme_time = params.get('time')

            deposit_id = int(deposit_id_str)
            deposit = await db.get_deposit(deposit_id)
            if not deposit or int(deposit["amount"] * 100) != int(amount):
                return web.json_response({"jsonrpc": "2.0", "error": {"code": -31050, "message": {"uz": "To'lov topilmadi", "ru": "Платеж не найден"}}, "id": request_id})

            tx = await db.get_payme_transaction(payme_trans_id)
            current_time_ms = int(time.time() * 1000)

            if tx:
                if tx["state"] == 1:
                    # Check timeout (12 hours)
                    if current_time_ms - tx["create_time"] > 12 * 60 * 60 * 1000:
                        await db.cancel_payme_transaction(payme_trans_id, current_time_ms, -1, -1)
                        return web.json_response({"jsonrpc": "2.0", "error": {"code": -31008, "message": {"uz": "Muddati o'tgan", "ru": "Время истекло"}}, "id": request_id})
                    return web.json_response({"jsonrpc": "2.0", "result": {"create_time": tx["create_time"], "transaction": str(deposit_id), "state": 1}, "id": request_id})
                else:
                    return web.json_response({"jsonrpc": "2.0", "error": {"code": -31008, "message": {"uz": "Holat noto'g'ri", "ru": "Неверное состояние"}}, "id": request_id})

            if deposit["status"] != 'pending':
                return web.json_response({"jsonrpc": "2.0", "error": {"code": -31099, "message": {"uz": "To'lov allaqachon bajarilgan", "ru": "Платеж уже обработан"}}, "id": request_id})

            # Create transaction record
            await db.create_payme_transaction(payme_trans_id, payme_time, amount/100, deposit_id, current_time_ms)
            return web.json_response({"jsonrpc": "2.0", "result": {"create_time": current_time_ms, "transaction": str(deposit_id), "state": 1}, "id": request_id})

        elif method == 'PerformTransaction':
            payme_trans_id = params.get('id')
            tx = await db.get_payme_transaction(payme_trans_id)

            if not tx:
                return web.json_response({"jsonrpc": "2.0", "error": {"code": -31003, "message": {"uz": "Tranzaksiya topilmadi", "ru": "Транзакция не найдена"}}, "id": request_id})

            current_time_ms = int(time.time() * 1000)

            if tx["state"] == 1:
                await db.perform_payme_transaction(payme_trans_id, current_time_ms)
                await db.update_deposit_status(tx["deposit_id"], 'approved')
                
                deposit = await db.get_deposit(tx["deposit_id"])
                await db.add_user_balance(deposit["user_id"], deposit["amount"])

                # Notify User
                user_msg = f"✅ Sizning hisobingiz Payme orqali {deposit['amount']:,} UZS ga to'ldirildi! 💸"
                try:
                    await bot.send_message(chat_id=deposit["user_id"], text=user_msg)
                except Exception as e:
                    print("Error notifying user of auto payme deposit:", e)

                return web.json_response({"jsonrpc": "2.0", "result": {"transaction": str(tx["deposit_id"]), "perform_time": current_time_ms, "state": 2}, "id": request_id})
                
            elif tx["state"] == 2:
                return web.json_response({"jsonrpc": "2.0", "result": {"transaction": str(tx["deposit_id"]), "perform_time": tx["perform_time"], "state": 2}, "id": request_id})
            else:
                return web.json_response({"jsonrpc": "2.0", "error": {"code": -31008, "message": {"uz": "Bekor qilingan", "ru": "Отменена"}}, "id": request_id})

        elif method == 'CancelTransaction':
            payme_trans_id = params.get('id')
            reason = params.get('reason')
            tx = await db.get_payme_transaction(payme_trans_id)

            if not tx:
                return web.json_response({"jsonrpc": "2.0", "error": {"code": -31003, "message": {"uz": "Tranzaksiya topilmadi", "ru": "Транзакция не найдена"}}, "id": request_id})

            current_time_ms = int(time.time() * 1000)

            if tx["state"] == 1:
                await db.cancel_payme_transaction(payme_trans_id, current_time_ms, reason, -1)
                await db.update_deposit_status(tx["deposit_id"], 'rejected')
                return web.json_response({"jsonrpc": "2.0", "result": {"transaction": str(tx["deposit_id"]), "cancel_time": current_time_ms, "state": -1}, "id": request_id})
                
            elif tx["state"] == 2:
                # Refund balance
                deposit = await db.get_deposit(tx["deposit_id"])
                await db.deduct_user_balance(deposit["user_id"], deposit["amount"])
                await db.cancel_payme_transaction(payme_trans_id, current_time_ms, reason, -2)
                await db.update_deposit_status(tx["deposit_id"], 'rejected')
                return web.json_response({"jsonrpc": "2.0", "result": {"transaction": str(tx["deposit_id"]), "cancel_time": current_time_ms, "state": -2}, "id": request_id})
            else:
                return web.json_response({"jsonrpc": "2.0", "result": {"transaction": str(tx["deposit_id"]), "cancel_time": tx["cancel_time"], "state": tx["state"]}, "id": request_id})

        elif method == 'CheckTransaction':
            payme_trans_id = params.get('id')
            tx = await db.get_payme_transaction(payme_trans_id)

            if not tx:
                return web.json_response({"jsonrpc": "2.0", "error": {"code": -31003, "message": {"uz": "Tranzaksiya topilmadi", "ru": "Транзакция не найдена"}}, "id": request_id})

            return web.json_response({
                "jsonrpc": "2.0",
                "result": {
                    "create_time": tx["create_time"],
                    "perform_time": tx["perform_time"] or 0,
                    "cancel_time": tx["cancel_time"] or 0,
                    "transaction": str(tx["deposit_id"]),
                    "state": tx["state"],
                    "reason": tx["reason"]
                },
                "id": request_id
            })
            
        else:
            return web.json_response({"jsonrpc": "2.0", "error": {"code": -32601, "message": "Method not found"}, "id": request_id})
    except Exception as e:
        print("Payme Webhook Error:", e)
        return web.json_response({"jsonrpc": "2.0", "error": {"code": -32603, "message": f"Internal error: {str(e)}"}, "id": None})


# Main Entry Point
async def main():
    global bot
    
    # Initialize DB schema & default packages
    await db.db_init()
    print("Database initialized successfully.")
    
    if not config.BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is not configured. Please set it in the .env file before starting the bot.")

    # Initialize Bot & Dispatcher
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()
    
    # Include Bot Routers
    dp.include_router(bot_start.router)
    dp.include_router(admin_ops.router)
    
    # Initialize AIOHTTP Web application
    app = web.Application()
    
    # Register static and API routes
    app.router.add_get('/', handle_index)
    app.router.add_get('/index.html', handle_index)
    app.router.add_get('/admin', lambda req: web.FileResponse(os.path.join(FRONTEND_DIR, 'admin.html')))
    app.router.add_get('/api/user', get_user_api)
    app.router.add_get('/api/admin/deposits', get_admin_deposits_api)
    app.router.add_get('/api/admin/deposits/{deposit_id}/receipt', get_admin_receipt_api)
    app.router.add_post('/api/admin/deposits/{deposit_id}/{action}', post_admin_deposit_action_api)
    app.router.add_get('/api/packages', get_packages_api)
    app.router.add_get('/api/history', get_history_api)
    app.router.add_post('/api/deposit', post_deposit_api)
    app.router.add_post('/api/deposit/create_link', post_create_payment_link_api)
    app.router.add_post('/api/purchase', post_purchase_api)
    
    # Stars Cases & Telegram Gifts Routes
    app.router.add_get('/api/cases', case_game.get_cases_api)
    app.router.add_post('/api/case/open', lambda req: case_game.open_case_api(req, bot=bot))
    app.router.add_get('/api/inventory', case_game.get_inventory_api)
    app.router.add_post('/api/inventory/sell', case_game.sell_inventory_api)
    app.router.add_post('/api/inventory/claim', lambda req: case_game.claim_inventory_api(req, bot=bot))
    app.router.add_get('/api/live_drops', case_game.get_live_drops_api)
    app.router.add_post('/api/convert_uzs_to_stars', case_game.convert_uzs_to_stars_api)
    
    # Billing Webhooks
    app.router.add_post('/api/payments/click/webhook', post_click_webhook)
    app.router.add_post('/api/payments/payme/webhook', post_payme_webhook)
    
    # Serving other frontend assets (style.css, app.js, images, etc.)
    app.router.add_static('/', FRONTEND_DIR)
    
    # Start Telegram Bot Polling in the background
    polling_task = asyncio.create_task(dp.start_polling(bot))
    print("Telegram Bot polling started.")
    
    # Start web app runner on configured port
    runner = web.AppRunner(app)
    await runner.setup()

    resolved_port = config.PORT
    try:
        site = web.TCPSite(runner, config.HOST, resolved_port)
        await site.start()
    except OSError as exc:
        if exc.errno != 10048:
            raise
        resolved_port = find_available_port(config.PORT)
        print(f"Port {config.PORT} is busy, using fallback port {resolved_port} instead.")
        if not os.getenv("WEBAPP_URL", "").strip():
            config.WEBAPP_URL = f"http://localhost:{resolved_port}"
        site = web.TCPSite(runner, config.HOST, resolved_port)
        await site.start()

    if not os.getenv("WEBAPP_URL", "").strip() and config.WEBAPP_URL.endswith(f":{config.PORT}"):
        config.WEBAPP_URL = f"http://localhost:{resolved_port}"

    print(f"Web application server started at http://localhost:{resolved_port}")
    print(f"Payment links and webapp URL: {config.WEBAPP_URL}")
    
    # Keep application running
    try:
        await polling_task
    except asyncio.CancelledError:
        pass
    finally:
        # Shutdown cleanup
        print("Shutting down bot and web server...")
        await runner.cleanup()
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Application stopped manually.")
