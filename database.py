import aiosqlite
import os

DB_PATH = "bot_database.db"

STAR_PACKAGES = [
    ('stars', '100 Stars 🌟', 28000.0, 100, 'stars_100.png'),
    ('stars', '150 Stars 🌟', 41000.0, 150, 'stars_150.png'),
    ('stars', '250 Stars 🌟', 66000.0, 250, 'stars_250.png'),
    ('stars', '500 Stars 🌟', 130000.0, 500, 'stars_500.png'),
    ('stars', '1000 Stars 🌟', 257000.0, 1000, 'stars_1000.png'),
]

PREMIUM_PACKAGES = [
    ('premium', 'Premium 3 Oylik 💎', 90000.0, 3, 'premium_3.png'),
    ('premium', 'Premium 6 Oylik 💎', 160000.0, 6, 'premium_6.png'),
    ('premium', 'Premium 12 Oylik 💎', 290000.0, 12, 'premium_12.png'),
]

async def _sync_packages(db, packages, category):
    """Keep catalog in sync with configured package list."""
    active_values = [pkg[3] for pkg in packages]
    placeholders = ",".join("?" for _ in active_values)
    await db.execute(
        f"UPDATE packages SET is_active = 0 WHERE category = ? AND value NOT IN ({placeholders})",
        (category, *active_values),
    )

    for category_name, name, price, value, image_url in packages:
        cursor = await db.execute(
            "SELECT id FROM packages WHERE category = ? AND value = ?",
            (category_name, value),
        )
        row = await cursor.fetchone()
        if row:
            await db.execute(
                "UPDATE packages SET name = ?, price = ?, image_url = ?, is_active = 1 WHERE id = ?",
                (name, price, image_url, row[0]),
            )
        else:
            await db.execute(
                """
                INSERT INTO packages (category, name, price, value, image_url, is_active)
                VALUES (?, ?, ?, ?, ?, 1)
                """,
                (category_name, name, price, value, image_url),
            )

async def db_init():
    async with aiosqlite.connect(DB_PATH) as db:
        # Create users table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                balance REAL DEFAULT 0.0,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create packages table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS packages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT, -- 'stars', 'premium'
                name TEXT,
                price REAL, -- in UZS
                value INTEGER, -- stars count or months
                image_url TEXT,
                is_active INTEGER DEFAULT 1
            )
        """)
        
        # Create deposits table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS deposits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount REAL,
                payment_method TEXT,
                receipt_photo_id TEXT,
                click_trans_id TEXT, -- for automatic click payments
                status TEXT DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        """)
        
        # Create payme_transactions table for JSON-RPC API
        await db.execute("""
            CREATE TABLE IF NOT EXISTS payme_transactions (
                id TEXT PRIMARY KEY,
                time INTEGER,
                state INTEGER,
                amount REAL,
                deposit_id INTEGER,
                create_time INTEGER,
                perform_time INTEGER,
                cancel_time INTEGER,
                reason INTEGER,
                FOREIGN KEY(deposit_id) REFERENCES deposits(id)
            )
        """)
        
        # Create orders table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                package_id INTEGER,
                target_username TEXT,
                price REAL,
                status TEXT DEFAULT 'pending', -- 'pending', 'completed', 'cancelled'
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(user_id),
                FOREIGN KEY(package_id) REFERENCES packages(id)
            )
        """)
        
        await _sync_packages(db, STAR_PACKAGES, 'stars')
        await _sync_packages(db, PREMIUM_PACKAGES, 'premium')
        await db.commit()

async def create_user_if_not_exists(user_id: int, username: str, first_name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR IGNORE INTO users (user_id, username, first_name)
            VALUES (?, ?, ?)
        """, (user_id, username or "", first_name or ""))
        # If user exists, update their username & first_name in case it changed
        await db.execute("""
            UPDATE users SET username = ?, first_name = ? WHERE user_id = ?
        """, (username or "", first_name or "", user_id))
        await db.commit()

async def get_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchone()

async def add_user_balance(user_id: int, amount: float):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
        await db.commit()

async def deduct_user_balance(user_id: int, amount: float):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (amount, user_id))
        await db.commit()

async def create_deposit_request(user_id: int, amount: float, payment_method: str, receipt_photo_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO deposits (user_id, amount, payment_method, receipt_photo_id)
            VALUES (?, ?, ?, ?)
        """, (user_id, amount, payment_method, receipt_photo_id))
        deposit_id = cursor.lastrowid
        await db.commit()
        return deposit_id

async def get_deposit(deposit_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM deposits WHERE id = ?", (deposit_id,)) as cursor:
            return await cursor.fetchone()

async def update_deposit_status(deposit_id: int, status: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE deposits SET status = ? WHERE id = ?", (status, deposit_id))
        await db.commit()

async def get_user_deposits(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM deposits WHERE user_id = ? ORDER BY created_at DESC", (user_id,)) as cursor:
            return await cursor.fetchall()

async def get_packages(category: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if category:
            query = "SELECT * FROM packages WHERE category = ? AND is_active = 1"
            params = (category,)
        else:
            query = "SELECT * FROM packages WHERE is_active = 1"
            params = ()
        async with db.execute(query, params) as cursor:
            return await cursor.fetchall()

async def get_package(package_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM packages WHERE id = ?", (package_id,)) as cursor:
            return await cursor.fetchone()

async def create_order(user_id: int, package_id: int, target_username: str, price: float):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO orders (user_id, package_id, target_username, price)
            VALUES (?, ?, ?, ?)
        """, (user_id, package_id, target_username, price))
        order_id = cursor.lastrowid
        await db.commit()
        return order_id

async def get_order(order_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT o.*, p.name as package_name, p.category as package_category
            FROM orders o
            JOIN packages p ON o.package_id = p.id
            WHERE o.id = ?
        """, (order_id,)) as cursor:
            return await cursor.fetchone()

async def update_order_status(order_id: int, status: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
        await db.commit()

async def get_user_orders(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT o.*, p.name as package_name
            FROM orders o
            JOIN packages p ON o.package_id = p.id
            WHERE o.user_id = ?
            ORDER BY o.created_at DESC
        """, (user_id,)) as cursor:
            return await cursor.fetchall()

async def get_all_deposits_admin(status: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        query = """
            SELECT d.*, u.first_name, u.username
            FROM deposits d
            LEFT JOIN users u ON d.user_id = u.user_id
        """
        params = ()
        if status and status != "all":
            query += " WHERE d.status = ?"
            params = (status,)
        query += " ORDER BY d.created_at DESC"
        async with db.execute(query, params) as cursor:
            return await cursor.fetchall()

async def get_all_orders_admin(status: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        query = """
            SELECT o.*, p.name as package_name, u.first_name, u.username
            FROM orders o
            JOIN packages p ON o.package_id = p.id
            LEFT JOIN users u ON o.user_id = u.user_id
        """
        params = ()
        if status and status != "all":
            query += " WHERE o.status = ?"
            params = (status,)
        query += " ORDER BY o.created_at DESC"
        async with db.execute(query, params) as cursor:
            return await cursor.fetchall()

async def get_pending_deposits():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT d.*, u.first_name, u.username
            FROM deposits d
            LEFT JOIN users u ON d.user_id = u.user_id
            WHERE d.status = 'pending'
            ORDER BY d.created_at ASC
        """) as cursor:
            return await cursor.fetchall()

async def get_pending_orders():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT o.*, p.name as package_name, u.first_name, u.username
            FROM orders o
            JOIN packages p ON o.package_id = p.id
            LEFT JOIN users u ON o.user_id = u.user_id
            WHERE o.status = 'pending'
            ORDER BY o.created_at ASC
        """) as cursor:
            return await cursor.fetchall()

async def get_admin_stats():
    async with aiosqlite.connect(DB_PATH) as db:
        stats = {}
        # Total users
        async with db.execute("SELECT COUNT(*) FROM users") as c:
            stats["total_users"] = (await c.fetchone())[0]
            
        # Total sales amount (completed orders)
        async with db.execute("SELECT SUM(price) FROM orders WHERE status = 'completed'") as c:
            val = (await c.fetchone())[0]
            stats["total_sales"] = val if val is not None else 0.0
            
        # Pending orders count
        async with db.execute("SELECT COUNT(*) FROM orders WHERE status = 'pending'") as c:
            stats["pending_orders"] = (await c.fetchone())[0]
            
        # Pending deposits count
        async with db.execute("SELECT COUNT(*) FROM deposits WHERE status = 'pending'") as c:
            stats["pending_deposits"] = (await c.fetchone())[0]
            
        return stats

async def get_all_users():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT user_id FROM users") as cursor:
            rows = await cursor.fetchall()
            return [r[0] for r in rows]

async def create_empty_deposit(user_id: int, amount: float, payment_method: str):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO deposits (user_id, amount, payment_method, status)
            VALUES (?, ?, ?, 'pending')
        """, (user_id, amount, payment_method))
        deposit_id = cursor.lastrowid
        await db.commit()
        return deposit_id

async def get_deposit_by_click_trans(click_trans_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM deposits WHERE click_trans_id = ?", (click_trans_id,)) as cursor:
            return await cursor.fetchone()

async def update_deposit_click_trans(deposit_id: int, click_trans_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE deposits SET click_trans_id = ? WHERE id = ?", (click_trans_id, deposit_id))
        await db.commit()

async def get_payme_transaction(payme_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM payme_transactions WHERE id = ?", (payme_id,)) as cursor:
            return await cursor.fetchone()

async def create_payme_transaction(payme_id: str, time: int, amount: float, deposit_id: int, create_time: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO payme_transactions (id, time, amount, deposit_id, state, create_time)
            VALUES (?, ?, ?, ?, 1, ?)
        """, (payme_id, time, amount, deposit_id, create_time))
        await db.commit()

async def perform_payme_transaction(payme_id: str, perform_time: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE payme_transactions
            SET state = 2, perform_time = ?
            WHERE id = ?
        """, (perform_time, payme_id))
        await db.commit()

async def cancel_payme_transaction(payme_id: str, cancel_time: int, reason: int, state: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE payme_transactions
            SET state = ?, cancel_time = ?, reason = ?
            WHERE id = ?
        """, (state, cancel_time, reason, payme_id))
        await db.commit()
