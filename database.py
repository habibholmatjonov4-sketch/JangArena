import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_name='bot_database.db'):
        self.db_name = db_name
        self.create_tables()
    
    def get_connection(self):
        return sqlite3.connect(self.db_name)
    
    def create_tables(self):
        """Create all necessary tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    phone TEXT,
                    language TEXT DEFAULT 'uz',
                    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Fighters table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS fighters (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    category TEXT,
                    fights_count INTEGER DEFAULT 0,
                    wins INTEGER DEFAULT 0,
                    losses INTEGER DEFAULT 0,
                    draws INTEGER DEFAULT 0
                )
            ''')
            
            # Fights table - CATEGORY QO'SHILDI
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS fights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fighter_id INTEGER,
                    title TEXT NOT NULL,
                    price INTEGER DEFAULT 0,
                    video_id TEXT,
                    is_paid BOOLEAN DEFAULT 0,
                    category TEXT DEFAULT 'boxing',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (fighter_id) REFERENCES fighters(id)
                )
            ''')
            
            # Purchases table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS purchases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    fight_id INTEGER,
                    amount INTEGER,
                    status TEXT DEFAULT 'pending',
                    purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    FOREIGN KEY (fight_id) REFERENCES fights(id)
                )
            ''')
            
            # Feedback table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')
            
            # Downloads table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS downloads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    fight_id INTEGER,
                    downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    FOREIGN KEY (fight_id) REFERENCES fights(id)
                )
            ''')
            
            # Insert fighters if not exists
            fighters = [
                (1, "Muhammad Ali", "boxing", 61, 56, 5, 0),
                (2, "Mike Tyson", "boxing", 58, 50, 6, 2),
                (3, "Floyd Mayweather", "boxing", 50, 50, 0, 0),
                (4, "Manny Pacquiao", "boxing", 72, 62, 8, 2),
                (5, "Rocky Marciano", "boxing", 49, 49, 0, 0),
                (6, "Joe Frazier", "boxing", 37, 32, 4, 1),
                (7, "George Alvarez", "boxing", 45, 40, 5, 0),
                (8, "Tyson Fury", "boxing", 35, 34, 0, 1),
                (9, "Oleksandr Usyk", "boxing", 22, 22, 0, 0),
                (10, "Francis Ngannou", "ufc", 20, 17, 3, 0),
                (11, "Jon Jones", "ufc", 28, 27, 1, 0),
                (12, "Stipe Miocic", "ufc", 24, 20, 4, 0),
                (13, "Cain Velasquez", "ufc", 17, 14, 3, 0),
                (14, "Daniel Cormier", "ufc", 26, 22, 3, 1),
                (15, "Khabib Nurmagomedov", "ufc", 29, 29, 0, 0),
                (16, "Islam Makhachev", "ufc", 27, 26, 1, 0),
                (17, "Charles Oliveira", "ufc", 41, 34, 7, 0),
                (18, "Dustin Poirier", "ufc", 38, 29, 8, 1),
                (19, "Justin Gaethje", "ufc", 29, 25, 4, 0),
                (20, "Khamzat Chimaev", "ufc", 14, 14, 0, 0),
                (21, "Amanda Nunes", "ufc", 27, 23, 4, 0),
                (22, "Ronda Rousey", "ufc", 14, 12, 2, 0),
                (23, "Valentina Shevchenko", "ufc", 29, 23, 4, 1),
                (24, "Zhang Weili", "ufc", 26, 24, 2, 0),
                (25, "Rose Namajunas", "ufc", 18, 12, 6, 0),
                (26, "Joanna Jedrzejczyk", "ufc", 20, 16, 4, 0),
            ]
            
            cursor.executemany('''
                INSERT OR IGNORE INTO fighters (id, name, category, fights_count, wins, losses, draws)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', fighters)
            
            conn.commit()
    
    def add_user(self, user_id, name, phone, language='uz'):
        """Add new user to database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO users (user_id, name, phone, language, last_active)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, name, phone, language))
            conn.commit()
    
    def get_user(self, user_id):
        """Get user by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT user_id, name, phone, registered_at, language, last_active FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            return result if result else None
    
    def get_user_language(self, user_id):
        """Get user language"""
        user = self.get_user(user_id)
        if user and len(user) > 4:
            return user[4] if user[4] in ['uz', 'ru', 'en'] else 'uz'
        return 'uz'
    
    def update_user_language(self, user_id, language):
        """Update user language"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET language = ?, last_active = CURRENT_TIMESTAMP WHERE user_id = ?', 
                         (language, user_id))
            conn.commit()
    
    def add_fight(self, fighter_id, title, price, video_id, is_paid, category):
        """Add new fight"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO fights (fighter_id, title, price, video_id, is_paid, category)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (fighter_id, title, price, video_id, is_paid, category))
            conn.commit()
            return cursor.lastrowid
    
    def get_fights(self, fighter_id=None, paid_only=None):
        """Get fights with optional filters"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = 'SELECT * FROM fights WHERE 1=1'
            params = []
            
            if fighter_id:
                query += ' AND fighter_id = ?'
                params.append(fighter_id)
            
            if paid_only is not None:
                query += ' AND is_paid = ?'
                params.append(1 if paid_only else 0)
            
            query += ' ORDER BY created_at DESC'
            
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def get_fight(self, fight_id):
        """Get fight by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM fights WHERE id = ?', (fight_id,))
            return cursor.fetchone()
    
    def add_purchase(self, user_id, fight_id, amount):
        """Add purchase record"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO purchases (user_id, fight_id, amount, status)
                VALUES (?, ?, ?, 'pending')
            ''', (user_id, fight_id, amount))
            conn.commit()
            return cursor.lastrowid
    
    def update_purchase_status(self, purchase_id, status):
        """Update purchase status"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE purchases SET status = ? WHERE id = ?', (status, purchase_id))
            conn.commit()
    
    def get_user_purchases(self, user_id):
        """Get user's purchases"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.*, f.title FROM purchases p
                JOIN fights f ON p.fight_id = f.id
                WHERE p.user_id = ? AND p.status = 'completed'
            ''', (user_id,))
            return cursor.fetchall()
    
    def add_feedback(self, user_id, message):
        """Add user feedback"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO feedback (user_id, message) VALUES (?, ?)', (user_id, message))
            conn.commit()
    
    def log_download(self, user_id, fight_id):
        """Log content download attempt"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO downloads (user_id, fight_id) VALUES (?, ?)', (user_id, fight_id))
            conn.commit()
    
    def get_all_users(self):
        """Get all users"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT user_id, name, phone, language, registered_at FROM users ORDER BY registered_at DESC')
            return cursor.fetchall()
    
    def get_statistics(self):
        """Get bot statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total users
            cursor.execute('SELECT COUNT(*) FROM users')
            total_users = cursor.fetchone()[0]
            
            # Users today
            cursor.execute('SELECT COUNT(*) FROM users WHERE DATE(registered_at) = DATE("now")')
            users_today = cursor.fetchone()[0]
            
            # Total purchases
            cursor.execute('SELECT COUNT(*), SUM(amount) FROM purchases WHERE status = "completed"')
            purchases = cursor.fetchone()
            total_purchases = purchases[0] or 0
            total_revenue = purchases[1] or 0
            
            # Pending purchases
            cursor.execute('SELECT COUNT(*) FROM purchases WHERE status = "pending"')
            pending_purchases = cursor.fetchone()[0]
            
            # Total feedback
            cursor.execute('SELECT COUNT(*) FROM feedback')
            total_feedback = cursor.fetchone()[0]
            
            return {
                'total_users': total_users,
                'users_today': users_today,
                'total_purchases': total_purchases,
                'total_revenue': total_revenue,
                'pending_purchases': pending_purchases,
                'total_feedback': total_feedback
            }