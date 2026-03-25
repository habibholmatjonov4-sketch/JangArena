from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from database import Database
from keyboards import get_admin_keyboard, get_admin_categories_keyboard, get_admin_fighters_keyboard
import os
import html

admin_router = Router()
db = Database()

# Fighters data with categories
BOXERS = [
    {"id": 1, "name": "👑 Muhammad Ali", "category": "boxing"},
    {"id": 2, "name": "👊 Mike Tyson", "category": "boxing"},
    {"id": 3, "name": "💰 Floyd Mayweather", "category": "boxing"},
    {"id": 4, "name": "🇵🇭 Manny Pacquiao", "category": "boxing"},
    {"id": 5, "name": "🥊 Rocky Marciano", "category": "boxing"},
    {"id": 6, "name": "⚡ Joe Frazier", "category": "boxing"},
    {"id": 7, "name": "🇲🇽 George Alvarez", "category": "boxing"},
    {"id": 8, "name": "🇬🇧 Tyson Fury", "category": "boxing"},
    {"id": 9, "name": "🇺🇦 Oleksandr Usyk", "category": "boxing"},
]

UFC_FIGHTERS = [
    {"id": 10, "name": "🦍 Francis Ngannou", "category": "ufc"},
    {"id": 11, "name": "🐉 Jon Jones", "category": "ufc"},
    {"id": 12, "name": "🔥 Stipe Miocic", "category": "ufc"},
    {"id": 13, "name": "🌋 Cain Velasquez", "category": "ufc"},
    {"id": 14, "name": "👨‍🏫 Daniel Cormier", "category": "ufc"},
    {"id": 15, "name": "🐻 Khabib Nurmagomedov", "category": "ufc"},
    {"id": 16, "name": "🏹 Islam Makhachev", "category": "ufc"},
    {"id": 17, "name": "🐍 Charles Oliveira", "category": "ufc"},
    {"id": 18, "name": "💀 Dustin Poirier", "category": "ufc"},
    {"id": 19, "name": "🤠 Justin Gaethje", "category": "ufc"},
    {"id": 20, "name": "🇸🇪 Khamzat Chimaev", "category": "ufc"},
    {"id": 21, "name": "👸 Amanda Nunes", "category": "ufc"},
    {"id": 22, "name": "💪 Ronda Rousey", "category": "ufc"},
    {"id": 23, "name": "🦅 Valentina Shevchenko", "category": "ufc"},
    {"id": 24, "name": "🇨🇳 Zhang Weili", "category": "ufc"},
    {"id": 25, "name": "🌸 Rose Namajunas", "category": "ufc"},
    {"id": 26, "name": "🇵🇱 Joanna Jedrzejczyk", "category": "ufc"},
]

ALL_FIGHTERS = BOXERS + UFC_FIGHTERS

class AdminStates(StatesGroup):
    # Add fight states
    waiting_for_category = State()
    waiting_for_fighter = State()
    waiting_for_fight_title = State()
    waiting_for_fight_price = State()
    waiting_for_fight_video = State()
    
    # Other admin states
    waiting_for_broadcast = State()
    waiting_for_fighter_edit = State()
    waiting_for_fight_edit = State()

def is_admin(user_id):
    """Check if user is admin"""
    admins = os.getenv('ADMIN_IDS', '').split(',')
    return str(user_id) in admins

@admin_router.message(Command('admin'))
async def admin_panel(message: types.Message):
    """Admin panel entry"""
    if not is_admin(message.from_user.id):
        return
    
    await message.answer(
        "👨‍💼 Admin paneliga xush kelibsiz!\n\nQuyidagi bo'limlardan birini tanlang:",
        reply_markup=get_admin_keyboard('uz')
    )

@admin_router.message(F.text == '📊 Statistika')
async def admin_statistics(message: types.Message):
    """Show bot statistics"""
    if not is_admin(message.from_user.id):
        return
    
    stats = db.get_statistics()
    
    # Get fights count by category
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT category, COUNT(*) 
            FROM fights 
            GROUP BY category
        ''')
        category_counts = cursor.fetchall()
    
    boxing_count = 0
    ufc_count = 0
    for cat, count in category_counts:
        if cat == 'boxing':
            boxing_count = count
        elif cat == 'ufc':
            ufc_count = count
    
    text = f"""
📊 BOT STATISTIKASI
━━━━━━━━━━━━━━━
👥 Umumiy foydalanuvchilar: {stats['total_users']}
📅 Bugun qo'shilganlar: {stats['users_today']}

👑 Boks janglari: {boxing_count} ta
⚔️ UFC janglari: {ufc_count} ta
💰 Jami xaridlar: {stats['total_purchases']}
💵 Umumiy daromad: {stats['total_revenue']:,} so'm
⏳ Kutilayotgan xaridlar: {stats['pending_purchases']}
💭 Fikrlar soni: {stats['total_feedback']}
    """
    
    await message.answer(text)

@admin_router.message(F.text == '➕ Jang Qo\'shish')
async def add_fight_start(message: types.Message, state: FSMContext):
    """Start adding new fight - choose category with reply keyboard"""
    if not is_admin(message.from_user.id):
        return
    
    await message.answer(
        "📂 Jang qaysi bo'limga tegishli?",
        reply_markup=get_admin_categories_keyboard()  # Reply keyboard for categories
    )
    await state.set_state(AdminStates.waiting_for_category)

@admin_router.message(AdminStates.waiting_for_category)
async def process_category(message: types.Message, state: FSMContext):
    """Process category selection from reply keyboard"""
    if not is_admin(message.from_user.id):
        return
    
    category = None
    if message.text == '👑 Boks Ring Qirollari':
        category = 'boxing'
    elif message.text == '⚔️ UFC Janglari':
        category = 'ufc'
    elif message.text == '🔙 Admin Menyu':
        await message.answer(
            "Admin paneliga qaytish",
            reply_markup=get_admin_keyboard('uz')
        )
        await state.clear()
        return
    else:
        await message.answer("❌ Noto'g'ri tanlov. Iltimos, bo'limni tanlang:")
        return
    
    await state.update_data(category=category)
    
    # Show fighters based on category
    fighters = BOXERS if category == 'boxing' else UFC_FIGHTERS
    await message.answer(
        "👊 Jangchi tanlang:",
        reply_markup=get_admin_fighters_keyboard(fighters)  # Reply keyboard for fighters
    )
    await state.set_state(AdminStates.waiting_for_fighter)

@admin_router.message(AdminStates.waiting_for_fighter)
async def process_fighter_selection(message: types.Message, state: FSMContext):
    """Process fighter selection from reply keyboard"""
    if not is_admin(message.from_user.id):
        return
    
    data = await state.get_data()
    category = data.get('category')
    
    fighters = BOXERS if category == 'boxing' else UFC_FIGHTERS
    
    # Find selected fighter
    selected_fighter = None
    for fighter in fighters:
        if message.text == fighter['name']:
            selected_fighter = fighter
            break
    
    if message.text == '🔙 Bo\'limlar':  # Tuzatildi: qo'shtirnoq to'g'ri
        await message.answer(
            "📂 Jang qaysi bo'limga tegishli?",
            reply_markup=get_admin_categories_keyboard()
        )
        await state.set_state(AdminStates.waiting_for_category)
        return
    elif message.text == '🔙 Admin Menyu':
        await message.answer(
            "Admin paneliga qaytish",
            reply_markup=get_admin_keyboard('uz')
        )
        await state.clear()
        return
    elif not selected_fighter:
        await message.answer("❌ Noto'g'ri tanlov. Iltimos, jangchini tanlang:")
        return
    
    await state.update_data(
        fighter_id=selected_fighter['id'],
        fighter_name=selected_fighter['name']
    )
    
    await message.answer(
        f"✍️ {selected_fighter['name']} uchun jang nomini kiriting:\n\n"
        f"Masalan: {selected_fighter['name']} vs Raqib - 2024",
        reply_markup=types.ReplyKeyboardRemove()  # Remove keyboard for text input
    )
    await state.set_state(AdminStates.waiting_for_fight_title)

@admin_router.message(AdminStates.waiting_for_fight_title)
async def add_fight_title(message: types.Message, state: FSMContext):
    """Process fight title"""
    if not is_admin(message.from_user.id):
        return
    
    title = html.escape(message.text[:200])
    await state.update_data(title=title)
    
    await message.answer(
        "💰 Jang narxini kiriting (so'mda):\n"
        "Agar bepul bo'lsa 0 deb yozing\n\n"
        "Masalan: 50000 yoki 0"
    )
    await state.set_state(AdminStates.waiting_for_fight_price)

@admin_router.message(AdminStates.waiting_for_fight_price)
async def add_fight_price(message: types.Message, state: FSMContext):
    """Process fight price"""
    if not is_admin(message.from_user.id):
        return
    
    try:
        price = int(message.text.replace(' ', ''))
        if price < 0:
            raise ValueError
    except:
        await message.answer("❌ Noto'g'ri narx. Iltimos qaytadan kiriting (faqat son):")
        return
    
    await state.update_data(price=price)
    
    await message.answer(
        "🎬 Endi jang videosini yuboring.\n\n"
        "⚠️ Diqqat: Video avtomatik himoyalangan bo'ladi!"
    )
    await state.set_state(AdminStates.waiting_for_fight_video)

@admin_router.message(AdminStates.waiting_for_fight_video)
async def add_fight_video(message: types.Message, state: FSMContext):
    """Process fight video"""
    if not is_admin(message.from_user.id):
        return
    
    if not message.video:
        await message.answer("❌ Iltimos, video fayl yuboring:")
        return
    
    data = await state.get_data()
    
    # Save to database with category
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO fights (fighter_id, title, price, video_id, is_paid, category)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data['fighter_id'],
            data['title'],
            data['price'],
            message.video.file_id,
            1 if data['price'] > 0 else 0,
            data['category']
        ))
        conn.commit()
        fight_id = cursor.lastrowid
    
    # Send confirmation
    category_name = "👑 Boks" if data['category'] == 'boxing' else "⚔️ UFC"
    
    await message.answer(
        f"✅ Jang muvaffaqiyatli qo'shildi!\n\n"
        f"📂 Bo'lim: {category_name}\n"
        f"👊 Jangchi: {data['fighter_name']}\n"
        f"📋 Jang: {data['title']}\n"
        f"💰 Narx: {data['price']:,} so'm\n"
        f"🆔 ID: {fight_id}",
        reply_markup=get_admin_keyboard('uz')
    )
    await state.clear()

@admin_router.message(F.text == '👥 Foydalanuvchilar')
async def admin_users(message: types.Message):
    """Show users list"""
    if not is_admin(message.from_user.id):
        return
    
    users = db.get_all_users()
    
    if not users:
        await message.answer("📭 Hozircha foydalanuvchilar yo'q")
        return
    
    text = "👥 FOYDALANUVCHILAR RO'YXATI\n\n"
    for user in users[:10]:  # Show first 10
        text += f"🆔 {user[0]}\n👤 {user[1]}\n📞 {user[2]}\n🌐 {user[3]}\n📅 {user[4]}\n{'-'*20}\n"
    
    if len(users) > 10:
        text += f"\n... va yana {len(users) - 10} ta foydalanuvchi"
    
    await message.answer(text)

@admin_router.message(F.text == '💰 Xaridlar')
async def admin_purchases(message: types.Message):
    """Show purchases"""
    if not is_admin(message.from_user.id):
        return
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.*, u.name, f.title 
            FROM purchases p
            JOIN users u ON p.user_id = u.user_id
            JOIN fights f ON p.fight_id = f.id
            ORDER BY p.purchased_at DESC
            LIMIT 20
        ''')
        purchases = cursor.fetchall()
    
    if not purchases:
        await message.answer("📭 Hozircha xaridlar yo'q")
        return
    
    text = "💰 OXIRGI XARIDLAR\n\n"
    for p in purchases:
        status_emoji = "✅" if p[4] == "completed" else "⏳" if p[4] == "pending" else "❌"
        text += f"{status_emoji} {p[7]}\n"  # p[7] - fight title
        text += f"👤 {p[6]}\n"  # p[6] - user name
        text += f"💵 {p[3]:,} so'm\n"  # p[3] - amount
        text += f"📅 {p[5]}\n"  # p[5] - purchased_at
        text += f"{'='*25}\n"
    
    await message.answer(text)

@admin_router.message(F.text == '💭 Fikrlar')
async def admin_feedback(message: types.Message):
    """Show feedback"""
    if not is_admin(message.from_user.id):
        return
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT f.*, u.name, u.phone FROM feedback f
            JOIN users u ON f.user_id = u.user_id
            ORDER BY f.created_at DESC
            LIMIT 10
        ''')
        feedbacks = cursor.fetchall()
    
    if not feedbacks:
        await message.answer("📭 Hozircha fikrlar yo'q")
        return
    
    text = "💭 FIKR VA TAKLIFLAR\n\n"
    for f in feedbacks:
        text += f"👤 {f[4]}\n"
        text += f"📞 {f[5]}\n"
        text += f"📝 {f[2]}\n"
        text += f"📅 {f[3]}\n"
        text += f"{'─'*25}\n"
    
    await message.answer(text)

@admin_router.message(F.text == '📢 Xabar Yuborish')
async def admin_broadcast(message: types.Message, state: FSMContext):
    """Start broadcast"""
    if not is_admin(message.from_user.id):
        return
    
    await message.answer(
        "📝 Barcha foydalanuvchilarga yuboriladigan xabarni yozing:\n\n"
        "💡 Xabaringizga rasm, video yoki boshqa fayl ham qo'shishingiz mumkin.",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AdminStates.waiting_for_broadcast)

@admin_router.message(AdminStates.waiting_for_broadcast)
async def admin_broadcast_send(message: types.Message, state: FSMContext):
    """Send broadcast"""
    if not is_admin(message.from_user.id):
        return
    
    users = db.get_all_users()
    sent = 0
    failed = 0
    
    status_msg = await message.answer("⏳ Xabar yuborilmoqda...")
    
    for user in users:
        try:
            # Copy message to user
            await message.copy_to(
                user[0],
                caption=f"📢 ADMIN XABARI\n\n{message.caption if message.caption else ''}"
            )
            sent += 1
        except Exception as e:
            failed += 1
            print(f"Failed to send to {user[0]}: {e}")
    
    await status_msg.delete()
    await message.answer(
        f"✅ Xabar yuborildi!\n\n"
        f"📊 Natijalar:\n"
        f"📤 Yuborildi: {sent}\n"
        f"❌ Yuborilmadi: {failed}\n"
        f"👥 Jami foydalanuvchilar: {len(users)}",
        reply_markup=get_admin_keyboard('uz')
    )
    await state.clear()

@admin_router.message(F.text == '⚙️ Sozlamalar')
async def admin_settings(message: types.Message):
    """Admin settings"""
    if not is_admin(message.from_user.id):
        return
    
    # Get fights count by fighter
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT fighter_id, COUNT(*) FROM fights GROUP BY fighter_id
        ''')
        fights_count = cursor.fetchall()
    
    fights_by_fighter = {str(f[0]): f[1] for f in fights_count}
    
    text = """
⚙️ SOZLAMALAR

👨‍💼 Admin ma'lumotlari:
🆔 Admin ID: {admin_ids}
🔢 Jami adminlar: {admin_count}

📊 Janglarning taqsimlanishi:
━━━━━━━━━━━━━━━
👑 BOKS RING QIROLLARI ({boxing_count} ta):
""".format(
        admin_ids=os.getenv('ADMIN_IDS', ''),
        admin_count=len(os.getenv('ADMIN_IDS', '').split(',')),
        boxing_count=len(BOXERS)
    )
    
    # Add boxers with fight counts
    for boxer in BOXERS:
        count = fights_by_fighter.get(str(boxer['id']), 0)
        text += f"  {boxer['name']}: {count} ta jang\n"
    
    text += "\n⚔️ UFC JANGLARI ({ufc_count} ta):\n".format(ufc_count=len(UFC_FIGHTERS))
    
    # Add UFC fighters with fight counts
    for ufc in UFC_FIGHTERS:
        count = fights_by_fighter.get(str(ufc['id']), 0)
        text += f"  {ufc['name']}: {count} ta jang\n"
    
    await message.answer(text)