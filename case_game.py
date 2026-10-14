import random
from aiohttp import web
import database as db
import config
from locales import STRINGS

TELEGRAM_GIFTS = {
    "teddy": {
        "id": "teddy",
        "name": "Teddy Bear",
        "icon": "🧸",
        "stars": 15,
        "rarity": "rare",
        "rarity_label": "Nodir",
        "color": "#38bdf8",
        "bg_gradient": "linear-gradient(135deg, rgba(14,165,233,0.2) 0%, rgba(2,132,199,0.4) 100%)",
        "glow": "0 0 20px rgba(56, 189, 248, 0.6)"
    },
    "cookie": {
        "id": "cookie",
        "name": "Ginger Cookie",
        "icon": "🍪",
        "stars": 362,
        "rarity": "epic",
        "rarity_label": "Afsonaviy",
        "color": "#e879f9",
        "bg_gradient": "linear-gradient(135deg, rgba(217,70,239,0.3) 0%, rgba(168,85,247,0.5) 100%)",
        "glow": "0 0 25px rgba(217, 70, 239, 0.8)"
    },
    "heart": {
        "id": "heart",
        "name": "Heart",
        "icon": "💖",
        "stars": 15,
        "rarity": "common",
        "rarity_label": "Oddiy",
        "color": "#38bdf8",
        "bg_gradient": "linear-gradient(135deg, rgba(56,189,248,0.2) 0%, rgba(14,165,233,0.3) 100%)",
        "glow": "0 0 15px rgba(56, 189, 248, 0.5)"
    },
    "rose": {
        "id": "rose",
        "name": "Rose",
        "icon": "🌹",
        "stars": 25,
        "rarity": "rare",
        "rarity_label": "Nodir",
        "color": "#fb7185",
        "bg_gradient": "linear-gradient(135deg, rgba(244,63,94,0.25) 0%, rgba(225,29,72,0.4) 100%)",
        "glow": "0 0 20px rgba(251, 113, 133, 0.6)"
    },
    "cake": {
        "id": "cake",
        "name": "Birthday Cake",
        "icon": "🎂",
        "stars": 50,
        "rarity": "epic",
        "rarity_label": "Ajoyib",
        "color": "#c084fc",
        "bg_gradient": "linear-gradient(135deg, rgba(168,85,247,0.25) 0%, rgba(126,34,206,0.4) 100%)",
        "glow": "0 0 20px rgba(192, 132, 252, 0.7)"
    },
    "champagne": {
        "id": "champagne",
        "name": "Champagne",
        "icon": "🍾",
        "stars": 100,
        "rarity": "epic",
        "rarity_label": "Ajoyib",
        "color": "#a855f7",
        "bg_gradient": "linear-gradient(135deg, rgba(147,51,234,0.3) 0%, rgba(88,28,135,0.5) 100%)",
        "glow": "0 0 25px rgba(168, 85, 247, 0.8)"
    },
    "duck": {
        "id": "duck",
        "name": "Yellow Duck",
        "icon": "🦆",
        "stars": 10,
        "rarity": "common",
        "rarity_label": "Oddiy",
        "color": "#facc15",
        "bg_gradient": "linear-gradient(135deg, rgba(250,204,21,0.2) 0%, rgba(202,138,4,0.3) 100%)",
        "glow": "0 0 15px rgba(250, 204, 21, 0.5)"
    },
    "crown": {
        "id": "crown",
        "name": "Royal Crown",
        "icon": "👑",
        "stars": 250,
        "rarity": "legendary",
        "rarity_label": "Qirollik",
        "color": "#fbbf24",
        "bg_gradient": "linear-gradient(135deg, rgba(245,158,11,0.3) 0%, rgba(180,83,9,0.5) 100%)",
        "glow": "0 0 25px rgba(251, 191, 36, 0.8)"
    },
    "diamond": {
        "id": "diamond",
        "name": "Diamond Gem",
        "icon": "💎",
        "stars": 500,
        "rarity": "mythic",
        "rarity_label": "Mifik",
        "color": "#22d3ee",
        "bg_gradient": "linear-gradient(135deg, rgba(6,182,212,0.35) 0%, rgba(8,145,178,0.6) 100%)",
        "glow": "0 0 30px rgba(34, 211, 238, 0.9)"
    },
    "rocket": {
        "id": "rocket",
        "name": "Super Rocket",
        "icon": "🚀",
        "stars": 1000,
        "rarity": "mythic",
        "rarity_label": "Jackpot",
        "color": "#f43f5e",
        "bg_gradient": "linear-gradient(135deg, rgba(239,68,68,0.35) 0%, rgba(185,28,28,0.6) 100%)",
        "glow": "0 0 35px rgba(244, 63, 94, 0.95)"
    },
    "star_14": {
        "id": "star_14",
        "name": "14 Stars",
        "icon": "⭐",
        "stars": 14,
        "rarity": "common",
        "rarity_label": "Yulduzlar",
        "color": "#f59e0b",
        "bg_gradient": "linear-gradient(135deg, rgba(245,158,11,0.2) 0%, rgba(217,119,6,0.35) 100%)",
        "glow": "0 0 15px rgba(245, 158, 11, 0.5)"
    },
    "star_50": {
        "id": "star_50",
        "name": "50 Stars",
        "icon": "🌟",
        "stars": 50,
        "rarity": "rare",
        "rarity_label": "Yulduzlar",
        "color": "#f59e0b",
        "bg_gradient": "linear-gradient(135deg, rgba(245,158,11,0.3) 0%, rgba(217,119,6,0.45) 100%)",
        "glow": "0 0 20px rgba(245, 158, 11, 0.7)"
    }
}

CASES = [
    {
        "id": "case_14",
        "name": "Teddy & Hearts",
        "badge": "Eng ommabop 🔥",
        "price": 14,
        "category": "stars_14",
        "icon": "🧸",
        "description": "14 Starsga oching! Teddy Bear, Heart yoki 362⭐ Ginger Cookie yutib oling!",
        "gradient": "linear-gradient(135deg, #1e3a8a 0%, #1e40af 50%, #0369a1 100%)",
        "glow_color": "#38bdf8",
        "items": [
            {"gift_id": "cookie", "weight": 4},
            {"gift_id": "star_50", "weight": 8},
            {"gift_id": "rose", "weight": 14},
            {"gift_id": "teddy", "weight": 24},
            {"gift_id": "heart", "weight": 24},
            {"gift_id": "star_14", "weight": 16},
            {"gift_id": "duck", "weight": 10},
        ]
    },
    {
        "id": "case_free",
        "name": "Kunlik Bepul Keys",
        "badge": "Kunlik sovg'a 🎁",
        "price": 0,
        "category": "free",
        "icon": "🎁",
        "description": "Har kuni mutlaqo bepul oching va qimmatbaho sovg'alarni yutib oling!",
        "gradient": "linear-gradient(135deg, #064e3b 0%, #059669 50%, #10b981 100%)",
        "glow_color": "#10b981",
        "items": [
            {"gift_id": "star_50", "weight": 5},
            {"gift_id": "teddy", "weight": 15},
            {"gift_id": "heart", "weight": 25},
            {"gift_id": "star_14", "weight": 25},
            {"gift_id": "duck", "weight": 30},
        ]
    },
    {
        "id": "case_25",
        "name": "Ginger & Sweets",
        "badge": "Xit keys 🍪",
        "price": 25,
        "category": "gifts",
        "icon": "🍪",
        "description": "Ginger Cookie 🍪, Cake 🎂 va Champagne 🍾 yutish imkoniyati!",
        "gradient": "linear-gradient(135deg, #581c87 0%, #a21caf 50%, #d946ef 100%)",
        "glow_color": "#d946ef",
        "items": [
            {"gift_id": "cookie", "weight": 15},
            {"gift_id": "champagne", "weight": 12},
            {"gift_id": "cake", "weight": 18},
            {"gift_id": "rose", "weight": 20},
            {"gift_id": "teddy", "weight": 20},
            {"gift_id": "heart", "weight": 15},
        ]
    },
    {
        "id": "case_50",
        "name": "Royal Crown VIP",
        "badge": "VIP Keys 👑",
        "price": 50,
        "category": "vip",
        "icon": "👑",
        "description": "Qirollik toji 👑, Olmos 💎 va eng sara Telegram sovg'alari!",
        "gradient": "linear-gradient(135deg, #78350f 0%, #b45309 50%, #f59e0b 100%)",
        "glow_color": "#f59e0b",
        "items": [
            {"gift_id": "diamond", "weight": 8},
            {"gift_id": "crown", "weight": 15},
            {"gift_id": "cookie", "weight": 20},
            {"gift_id": "champagne", "weight": 25},
            {"gift_id": "cake", "weight": 32},
        ]
    },
    {
        "id": "case_100",
        "name": "Mega Jackpot Rocket",
        "badge": "Maksimal Yutuq 🚀",
        "price": 100,
        "category": "vip",
        "icon": "💎",
        "description": "Super Raketa 🚀 (1000⭐) va Olmos 💎 (500⭐) kutmoqda!",
        "gradient": "linear-gradient(135deg, #881337 0%, #e11d48 50%, #fb7185 100%)",
        "glow_color": "#f43f5e",
        "items": [
            {"gift_id": "rocket", "weight": 10},
            {"gift_id": "diamond", "weight": 22},
            {"gift_id": "cookie", "weight": 28},
            {"gift_id": "crown", "weight": 40},
        ]
    }
]

# Track free case claims per user in memory (timestamp)
_free_claims = {}

def get_cases_data():
    """Format cases data for API response with populated items."""
    result = []
    for c in CASES:
        populated_items = []
        for it in c["items"]:
            gift = TELEGRAM_GIFTS.get(it["gift_id"])
            if gift:
                populated_items.append({
                    **gift,
                    "weight": it["weight"]
                })
        result.append({
            "id": c["id"],
            "name": c["name"],
            "badge": c["badge"],
            "price": c["price"],
            "category": c["category"],
            "icon": c["icon"],
            "description": c["description"],
            "gradient": c["gradient"],
            "glow_color": c["glow_color"],
            "items": populated_items
        })
    return result


async def get_cases_api(request):
    """Retrieve all available cases."""
    return web.json_response(get_cases_data())


async def open_case_api(request, bot=None):
    """Open a case: validates stars, rolls a winning item, saves to inventory and live feed."""
    try:
        data = await request.json()
        user_id = int(data.get("user_id", 0))
        case_id = data.get("case_id", "")
        
        if not user_id:
            return web.json_response({"detail": "User ID kiritilmagan!"}, status=400)
            
        case = next((c for c in CASES if c["id"] == case_id), None)
        if not case:
            return web.json_response({"detail": "Bunday keys topilmadi!"}, status=404)
            
        user = await db.get_user(user_id)
        if not user:
            await db.create_user_if_not_exists(user_id, "", "Foydalanuvchi")
            user = await db.get_user(user_id)

        user_stars = float(user["stars_balance"]) if "stars_balance" in user.keys() and user["stars_balance"] is not None else 25.0
        
        # Check free case cooldown
        if case["price"] == 0:
            import time
            now = time.time()
            last_claim = _free_claims.get(user_id, 0)
            cooldown_seconds = 86400 # 24 hours
            if now - last_claim < cooldown_seconds:
                remaining_mins = int((cooldown_seconds - (now - last_claim)) // 60)
                return web.json_response({
                    "detail": f"Bepul keysni har 24 soatda ochish mumkin! Qolgan vaqt: {remaining_mins} daqiqa."
                }, status=400)
            _free_claims[user_id] = now
        elif user_stars < case["price"]:
            return web.json_response({
                "detail": f"Stars balansingiz yetarli emas! Sizda {int(user_stars)} ⭐ bor, keys narxi: {case['price']} ⭐."
            }, status=400)
            
        # Deduct stars if not free
        if case["price"] > 0:
            await db.deduct_user_stars(user_id, case["price"])
            
        # Pick winning item based on weights
        items = case["items"]
        weights = [it["weight"] for it in items]
        chosen = random.choices(items, weights=weights, k=1)[0]
        winning_gift = TELEGRAM_GIFTS[chosen["gift_id"]]
        
        # Add to inventory
        inv_id = await db.add_inventory_item(
            user_id=user_id,
            item_name=winning_gift["name"],
            item_icon=winning_gift["icon"],
            stars_value=winning_gift["stars"],
            rarity=winning_gift["rarity"]
        )
        
        # Add to live drops
        user_name = user["first_name"] or "Foydalanuvchi"
        await db.record_live_drop(
            user_name=user_name,
            item_name=winning_gift["name"],
            item_icon=winning_gift["icon"],
            stars_value=winning_gift["stars"],
            rarity=winning_gift["rarity"]
        )
        
        # Build roulette tape for frontend: 50 items with winning gift placed at target_index (e.g. index 35)
        target_index = 35
        all_gift_ids = [it["gift_id"] for it in items]
        tape = []
        for i in range(50):
            if i == target_index:
                tape.append(winning_gift)
            else:
                rand_id = random.choice(all_gift_ids)
                tape.append(TELEGRAM_GIFTS[rand_id])
                
        # Get updated user info
        updated_user = await db.get_user(user_id)
        new_stars = float(updated_user["stars_balance"]) if "stars_balance" in updated_user.keys() and updated_user["stars_balance"] is not None else 0.0

        return web.json_response({
            "success": True,
            "winning_item": {
                **winning_gift,
                "inventory_id": inv_id
            },
            "tape": tape,
            "target_index": target_index,
            "new_stars_balance": new_stars
        })
    except Exception as e:
        print("API Error in open_case_api:", e)
        return web.json_response({"detail": str(e)}, status=500)


async def get_inventory_api(request):
    """Retrieve items won and currently held by user."""
    try:
        user_id_str = request.query.get('user_id')
        if not user_id_str or not user_id_str.isdigit():
            return web.json_response({"detail": "Invalid user_id"}, status=400)
            
        user_id = int(user_id_str)
        items = await db.get_user_inventory(user_id)
        
        result = []
        for it in items:
            gift_def = next((g for g in TELEGRAM_GIFTS.values() if g["name"] == it["item_name"]), None)
            color = gift_def["color"] if gift_def else "#38bdf8"
            bg = gift_def["bg_gradient"] if gift_def else "rgba(56,189,248,0.2)"
            result.append({
                "id": it["id"],
                "name": it["item_name"],
                "icon": it["item_icon"],
                "stars_value": it["stars_value"],
                "rarity": it["rarity"],
                "color": color,
                "bg_gradient": bg,
                "created_at": str(it["created_at"])
            })
        return web.json_response(result)
    except Exception as e:
        print("API Error in get_inventory_api:", e)
        return web.json_response({"detail": str(e)}, status=500)


async def sell_inventory_api(request):
    """Sell a won gift to instantly get its stars added to balance."""
    try:
        data = await request.json()
        user_id = int(data.get("user_id", 0))
        item_id = int(data.get("item_id", 0))
        
        if not user_id or not item_id:
            return web.json_response({"detail": "Ma'lumotlar to'liq emas!"}, status=400)
            
        stars_added = await db.sell_inventory_item(user_id, item_id)
        if stars_added is None:
            return web.json_response({"detail": "Buyum topilmadi yoki allaqachon sotilgan!"}, status=404)
            
        user = await db.get_user(user_id)
        new_stars = float(user["stars_balance"]) if "stars_balance" in user.keys() and user["stars_balance"] is not None else 0.0

        return web.json_response({
            "success": True,
            "stars_added": stars_added,
            "new_stars_balance": new_stars
        })
    except Exception as e:
        print("API Error in sell_inventory_api:", e)
        return web.json_response({"detail": str(e)}, status=500)


async def claim_inventory_api(request, bot=None):
    """Claim a gift (request send to Telegram account)."""
    try:
        data = await request.json()
        user_id = int(data.get("user_id", 0))
        item_id = int(data.get("item_id", 0))
        target = data.get("target", "").strip()
        
        if not user_id or not item_id or not target:
            return web.json_response({"detail": "Telegram username yoki ID kiritilishi shart!"}, status=400)
            
        ok = await db.claim_inventory_item(user_id, item_id)
        if not ok:
            return web.json_response({"detail": "Buyum topilmadi yoki allaqachon qabul qilingan!"}, status=404)
            
        # Notify admins
        user = await db.get_user(user_id)
        u_name = user["first_name"] if user else "Noma'lum"
        
        if bot and config.ADMIN_IDS:
            admin_msg = (
                f"🎁 **Yangi Telegram Gift chiqarib olish so'rovi!**\n\n"
                f"👤 Foydalanuvchi: {u_name} (ID: `{user_id}`)\n"
                f"🎯 Kimga yuborish: `{target}`\n"
                f"📦 Item ID: #{item_id}\n\n"
                f"Iltimos, Telegram orqali sovg'ani yuboring!"
            )
            for a_id in config.ADMIN_IDS:
                try:
                    await bot.send_message(chat_id=a_id, text=admin_msg, parse_mode="Markdown")
                except Exception as ex:
                    print("Failed to notify admin of gift claim:", ex)

        return web.json_response({"success": True})
    except Exception as e:
        print("API Error in claim_inventory_api:", e)
        return web.json_response({"detail": str(e)}, status=500)


async def get_live_drops_api(request):
    """Retrieve recent live drops."""
    try:
        drops = await db.get_live_drops(limit=25)
        result = []
        for d in drops:
            gift_def = next((g for g in TELEGRAM_GIFTS.values() if g["name"] == d["item_name"]), None)
            color = gift_def["color"] if gift_def else "#38bdf8"
            result.append({
                "id": d["id"],
                "user_name": d["user_name"],
                "item_name": d["item_name"],
                "item_icon": d["item_icon"],
                "stars_value": d["stars_value"],
                "rarity": d["rarity"],
                "color": color
            })
        return web.json_response(result)
    except Exception as e:
        print("API Error in get_live_drops_api:", e)
        return web.json_response({"detail": str(e)}, status=500)


async def convert_uzs_to_stars_api(request):
    """Convert UZS balance to Stars directly (Rate: 1 Star = 280 UZS)."""
    try:
        data = await request.json()
        user_id = int(data.get("user_id", 0))
        stars_amount = int(data.get("stars_amount", 0))
        
        if not user_id or stars_amount <= 0:
            return web.json_response({"detail": "Yaroqsiz miqdor!"}, status=400)
            
        user = await db.get_user(user_id)
        if not user:
            return web.json_response({"detail": "Foydalanuvchi topilmadi!"}, status=404)
            
        rate_per_star = 280.0
        total_uzs_cost = stars_amount * rate_per_star
        
        if user["balance"] < total_uzs_cost:
            return web.json_response({
                "detail": f"Mablag' yetarli emas! {stars_amount} ⭐ olish uchun {total_uzs_cost:,.0f} UZS kerak."
            }, status=400)
            
        # Deduct UZS and Add Stars
        await db.deduct_user_balance(user_id, total_uzs_cost)
        await db.add_user_stars(user_id, stars_amount)
        
        updated_user = await db.get_user(user_id)
        new_stars = float(updated_user["stars_balance"]) if "stars_balance" in updated_user.keys() and updated_user["stars_balance"] is not None else 0.0
        new_uzs = updated_user["balance"]

        return web.json_response({
            "success": True,
            "stars_added": stars_amount,
            "new_stars_balance": new_stars,
            "new_uzs_balance": new_uzs
        })
    except Exception as e:
        print("API Error in convert_uzs_to_stars_api:", e)
        return web.json_response({"detail": str(e)}, status=500)
