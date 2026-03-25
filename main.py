import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from database import Database
from keyboards import get_main_keyboard, get_language_keyboard, get_phone_keyboard, get_admin_keyboard, get_fighters_reply_keyboard
from admin import admin_router
import os
from dotenv import load_dotenv
from keep_alive import keep_alive
import html
from datetime import datetime

load_dotenv()

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot initialization
bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher(storage=MemoryStorage())
db = Database()

# Include admin router
dp.include_router(admin_router)

# States
class UserStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_feedback = State()
    viewing_boxers = State()
    viewing_ufc = State()
    changing_language = State()  # Yangi state

# Language dictionaries
translations = {
    'uz': {
        'welcome': '👋 Assalomu Alaykum Dunyo Jang ustalari Botiga Xush Kelibsiz!\n\n🥊 Bu Botimizda Siz Eng Sara Janglardan Birinchilardan Bo\'lib Xabardor Bo\'lasiz',
        'choose_lang': '🌐 O\'zingizga Kerakli Tilni Tanlang:',
        'enter_name': '✍️ Iltimos, Ismingizni Kiriting:',
        'enter_phone': '📱 Iltimos, Telefon Raqamingizni Kiriting:',
        'thanks': '✅ Rahmat! Endi botdan to\'liq foydalanishingiz mumkin.',
        'main_menu': '🥊 Assalomu Aleykum Dunyo Janglari va Eng Qisqa Nokautlarni Ko\'rish uchun Kerakli Bo\'limlarni Tanlang:',
        'boxing_kings': '👑 Boks Ring Qirollari',
        'ufc_fights': '⚔️ UFC Janglari',
        'change_lang': '🔄 Tilni O\'zgartirish',
        'paid_fights': '💰 Pullik Janglarni Ko\'rish',
        'contact_admin': '👨‍💼 Admin Bilan Aloqa',
        'feedback': '💭 Takliflar va Fikrlar',
        'phone_btn': '📞 Telefon Raqamni Yuborish',
        'back': '🔙 Orqaga',
        'back_to_menu': '🔙 Asosiy Menyu',
        'invalid_phone': '❌ Noto\'g\'ri telefon raqam. Iltimos qaytadan urinib ko\'ring:',
        'feedback_sent': '✅ Fikringiz uchun rahmat! Admin tez orada ko\'rib chiqadi.',
        'choose_fighter': '👊 Quyidagi jangchilardan birini tanlang:',
        'fighter_info': '👤 Jangchi: {name}\n🥊 Janglar soni: {fights}\n🏆 G\'alabalar: {wins}\n💔 Mag\'lubiyatlar: {losses}\n🤝 Durang: {draws}\n\n🎬 Janglarni ko\'rish uchun quyidagi tugmalardan foydalaning:',
        'free_fights': '🆓 Bepul Janglarni Ko\'rish',
        'paid_fights_list': '💳 Pullik Janglarni Ko\'rish',
        'no_fights': '📭 Hozircha janglar mavjud emas',
        'purchase_fight': '💰 Sotib olish - {price} so\'m',
        'payment_info': '💳 To\'lov uchun ma\'lumot:\nKarta: 8600 1234 5678 9012\nSumma: {price} so\'m\n\nTo\'lov amalga oshirilgach, admin tasdiqlaydi',
        'content_protected': '🔒 Bu kontent himoyalangan. Yuklab olish, skrinshot va ekran yozib olish taqiqlangan!',
        'select_boxer': '👑 Boks Ring Qirollaridan birini tanlang:',
        'select_ufc_fighter': '⚔️ UFC jangchilaridan birini tanlang:',
        'lang_changed': '✅ Til muvaffaqiyatli o\'zgartirildi!',
    },
    'ru': {
        'welcome': '👋 Здравствуйте! Добро пожаловать в бот Мировых Бойцов!\n\n🥊 В нашем боте вы узнаете о лучших боях одними из первых',
        'choose_lang': '🌐 Выберите нужный язык:',
        'enter_name': '✍️ Пожалуйста, введите ваше имя:',
        'enter_phone': '📱 Пожалуйста, введите ваш номер телефона:',
        'thanks': '✅ Спасибо! Теперь вы можете полностью пользоваться ботом.',
        'main_menu': '🥊 Здравствуйте! Выберите нужный раздел для просмотра боёв и самых быстрых нокаутов:',
        'boxing_kings': '👑 Короли бокса',
        'ufc_fights': '⚔️ Бои UFC',
        'change_lang': '🔄 Изменить язык',
        'paid_fights': '💰 Платные бои',
        'contact_admin': '👨‍💼 Связаться с админом',
        'feedback': '💭 Предложения и отзывы',
        'phone_btn': '📞 Отправить номер',
        'back': '🔙 Назад',
        'back_to_menu': '🔙 Главное меню',
        'invalid_phone': '❌ Неверный номер. Пожалуйста, попробуйте снова:',
        'feedback_sent': '✅ Спасибо за отзыв! Админ скоро рассмотрит его.',
        'choose_fighter': '👊 Выберите бойца:',
        'fighter_info': '👤 Боец: {name}\n🥊 Боев: {fights}\n🏆 Побед: {wins}\n💔 Поражений: {losses}\n🤝 Ничьих: {draws}\n\n🎬 Для просмотра боев используйте кнопки:',
        'free_fights': '🆓 Бесплатные бои',
        'paid_fights_list': '💳 Платные бои',
        'no_fights': '📭 Пока нет доступных боев',
        'purchase_fight': '💰 Купить - {price} сум',
        'payment_info': '💳 Информация об оплате:\nКарта: 8600 1234 5678 9012\nСумма: {price} сум\n\nПосле оплаты админ подтвердит',
        'content_protected': '🔒 Этот контент защищен. Скачивание, скриншоты и запись экрана запрещены!',
        'select_boxer': '👑 Выберите одного из королей бокса:',
        'select_ufc_fighter': '⚔️ Выберите одного из бойцов UFC:',
        'lang_changed': '✅ Язык успешно изменен!',
    },
    'en': {
        'welcome': '👋 Hello! Welcome to the World Warriors Bot!\n\n🥊 In this bot you will be among the first to know about the best fights',
        'choose_lang': '🌐 Choose your language:',
        'enter_name': '✍️ Please enter your name:',
        'enter_phone': '📱 Please enter your phone number:',
        'thanks': '✅ Thank you! Now you can fully use the bot.',
        'main_menu': '🥊 Hello! Choose the section to watch fights and fastest knockouts:',
        'boxing_kings': '👑 Boxing Ring Kings',
        'ufc_fights': '⚔️ UFC Fights',
        'change_lang': '🔄 Change Language',
        'paid_fights': '💰 Paid Fights',
        'contact_admin': '👨‍💼 Contact Admin',
        'feedback': '💭 Suggestions & Feedback',
        'phone_btn': '📞 Send Phone Number',
        'back': '🔙 Back',
        'back_to_menu': '🔙 Main Menu',
        'invalid_phone': '❌ Invalid phone number. Please try again:',
        'feedback_sent': '✅ Thank you for your feedback! Admin will review it soon.',
        'choose_fighter': '👊 Choose a fighter:',
        'fighter_info': '👤 Fighter: {name}\n🥊 Fights: {fights}\n🏆 Wins: {wins}\n💔 Losses: {losses}\n🤝 Draws: {draws}\n\n🎬 Use buttons below to watch fights:',
        'free_fights': '🆓 Free Fights',
        'paid_fights_list': '💳 Paid Fights',
        'no_fights': '📭 No fights available yet',
        'purchase_fight': '💰 Buy - {price} UZS',
        'payment_info': '💳 Payment information:\nCard: 8600 1234 5678 9012\nAmount: {price} UZS\n\nAdmin will confirm after payment',
        'content_protected': '🔒 This content is protected. Downloading, screenshots and screen recording are prohibited!',
        'select_boxer': '👑 Select a boxing king:',
        'select_ufc_fighter': '⚔️ Select a UFC fighter:',
        'lang_changed': '✅ Language changed successfully!',
    }
}

# Fighters data
boxers = [
    {"id": 1, "name": "👑 Muhammad Ali", "fights": 61, "wins": 56, "losses": 5, "draws": 0},
    {"id": 2, "name": "👊 Mike Tyson", "fights": 58, "wins": 50, "losses": 6, "draws": 2},
    {"id": 3, "name": "💰 Floyd Mayweather", "fights": 50, "wins": 50, "losses": 0, "draws": 0},
    {"id": 4, "name": "🇵🇭 Manny Pacquiao", "fights": 72, "wins": 62, "losses": 8, "draws": 2},
    {"id": 5, "name": "🥊 Rocky Marciano", "fights": 49, "wins": 49, "losses": 0, "draws": 0},
    {"id": 6, "name": "⚡ Joe Frazier", "fights": 37, "wins": 32, "losses": 4, "draws": 1},
    {"id": 7, "name": "🇲🇽 George Alvarez", "fights": 45, "wins": 40, "losses": 5, "draws": 0},
    {"id": 8, "name": "🇬🇧 Tyson Fury", "fights": 35, "wins": 34, "losses": 0, "draws": 1},
    {"id": 9, "name": "🇺🇦 Oleksandr Usyk", "fights": 22, "wins": 22, "losses": 0, "draws": 0},
]

ufc_fighters = [
    {"id": 10, "name": "🦍 Francis Ngannou", "fights": 20, "wins": 17, "losses": 3, "draws": 0},
    {"id": 11, "name": "🐉 Jon Jones", "fights": 28, "wins": 27, "losses": 1, "draws": 0},
    {"id": 12, "name": "🔥 Stipe Miocic", "fights": 24, "wins": 20, "losses": 4, "draws": 0},
    {"id": 13, "name": "🌋 Cain Velasquez", "fights": 17, "wins": 14, "losses": 3, "draws": 0},
    {"id": 14, "name": "👨‍🏫 Daniel Cormier", "fights": 26, "wins": 22, "losses": 3, "draws": 1},
    {"id": 15, "name": "🐻 Khabib Nurmagomedov", "fights": 29, "wins": 29, "losses": 0, "draws": 0},
    {"id": 16, "name": "🏹 Islam Makhachev", "fights": 27, "wins": 26, "losses": 1, "draws": 0},
    {"id": 17, "name": "🐍 Charles Oliveira", "fights": 41, "wins": 34, "losses": 7, "draws": 0},
    {"id": 18, "name": "💀 Dustin Poirier", "fights": 38, "wins": 29, "losses": 8, "draws": 1},
    {"id": 18, "name": "💀 Conor McGregor", "fights": 38, "wins": 29, "losses": 8, "draws": 1},
    {"id": 19, "name": "🤠 Justin Gaethje", "fights": 29, "wins": 25, "losses": 4, "draws": 0},
    {"id": 20, "name": "🇸🇪 Khamzat Chimaev", "fights": 14, "wins": 14, "losses": 0, "draws": 0},
    {"id": 21, "name": "👸 Amanda Nunes", "fights": 27, "wins": 23, "losses": 4, "draws": 0},
    {"id": 22, "name": "💪 Ronda Rousey", "fights": 14, "wins": 12, "losses": 2, "draws": 0},
    {"id": 23, "name": "🦅 Valentina Shevchenko", "fights": 29, "wins": 23, "losses": 4, "draws": 1},
    {"id": 24, "name": "🇨🇳 Zhang Weili", "fights": 26, "wins": 24, "losses": 2, "draws": 0},
    {"id": 25, "name": "🌸 Rose Namajunas", "fights": 18, "wins": 12, "losses": 6, "draws": 0},
    {"id": 26, "name": "🇵🇱 Joanna Jedrzejczyk", "fights": 20, "wins": 16, "losses": 4, "draws": 0},
]

ALL_FIGHTERS = boxers + ufc_fighters

# Helper functions
def get_text(user_id: int, key: str, **kwargs) -> str:
    """Get translated text for user"""
    try:
        user_data = db.get_user(user_id)
        if user_data and len(user_data) > 4:
            lang = user_data[4] if user_data[4] in ['uz', 'ru', 'en'] else 'uz'
        else:
            lang = 'uz'
        
        if key in translations[lang]:
            text = translations[lang][key]
        else:
            text = translations['uz'].get(key, key)
        
        return text.format(**kwargs) if kwargs else text
    except Exception as e:
        logger.error(f"Error in get_text: {e}")
        return key

def create_fight_options_keyboard(fighter_id, user_id):
    """Create inline keyboard for fight options"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=get_text(user_id, 'free_fights'),
            callback_data=f"free_fights_{fighter_id}"
        ),
        InlineKeyboardButton(
            text=get_text(user_id, 'paid_fights_list'),
            callback_data=f"paid_fights_{fighter_id}"
        )
    )
    builder.row(InlineKeyboardButton(
        text=get_text(user_id, 'back_to_menu'),
        callback_data="back_to_main"
    ))
    return builder.as_markup()

def protect_content_kwargs():
    """Return kwargs for content protection"""
    return {
        'protect_content': True,
        'allow_sending_without_reply': True
    }

# Handlers
@dp.message(Command('start'))
async def cmd_start(message: types.Message, state: FSMContext):
    """Start command handler"""
    user_id = message.from_user.id
    logger.info(f"User {user_id} started the bot")
    
    try:
        # Check if user exists
        user = db.get_user(user_id)
        
        # Check if user is admin
        admins = os.getenv('ADMIN_IDS', '').split(',')
        if str(user_id) in admins:
            await message.answer(
                "👨‍💼 Admin paneliga xush kelibsiz!",
                reply_markup=get_admin_keyboard('uz')
            )
            return
        
        if not user:
            # New user - ask for language
            await message.answer(
                translations['uz']['welcome'] + "\n\n" + translations['uz']['choose_lang'],
                reply_markup=get_language_keyboard()
            )
            await state.set_state(UserStates.waiting_for_name)
        else:
            # Existing user - show main menu
            lang = user[4] if len(user) > 4 and user[4] in ['uz', 'ru', 'en'] else 'uz'
            await message.answer(
                translations[lang]['main_menu'],
                reply_markup=get_main_keyboard(user_id, lang)
            )
    except Exception as e:
        logger.error(f"Error in cmd_start: {e}")
        await message.answer("Xatolik yuz berdi. Iltimos qaytadan urinib ko'ring.")

# Tilni o'zgartirish - TO'G'IRLANGAN VERSIYA
@dp.message(lambda message: message.text in ['🔄 Tilni O\'zgartirish', '🔄 Изменить язык', '🔄 Change Language'])
async def change_language(message: types.Message, state: FSMContext):
    """Change language without re-registration"""
    try:
        user_id = message.from_user.id
        user = db.get_user(user_id)
        
        if not user:
            # Agar user topilmasa, start ga o'tkazish
            await cmd_start(message, state)
            return
        
        # User ma'lumotlarini to'g'ri olish
        # user = (user_id, name, phone, registered_at, language, last_active)
        if len(user) >= 5:
            current_lang = user[4] if user[4] in ['uz', 'ru', 'en'] else 'uz'
        else:
            current_lang = 'uz'
        
        # Til tanlash keyboardini ko'rsatish
        await message.answer(
            translations[current_lang]['choose_lang'],
            reply_markup=get_language_keyboard()
        )
        
        # Til o'zgartirish state ini o'rnatish
        await state.set_state(UserStates.changing_language)
        
    except Exception as e:
        logger.error(f"Error in change_language: {e}")
        await message.answer("Xatolik yuz berdi. Iltimos qaytadan urinib ko'ring.")

@dp.message(lambda message: message.text in ['🇺🇿 UZ', '🇷🇺 RU', '🇬🇧 EN'])
async def process_language(message: types.Message, state: FSMContext):
    """Process language selection"""
    try:
        user_id = message.from_user.id
        lang_map = {'🇺🇿 UZ': 'uz', '🇷🇺 RU': 'ru', '🇬🇧 EN': 'en'}
        selected_lang = lang_map.get(message.text, 'uz')
        
        current_state = await state.get_state()
        
        if current_state == UserStates.changing_language.state:
            # User is changing language (not new registration)
            db.update_user_language(user_id, selected_lang)
            
            # Til o'zgarganligi haqida xabar
            await message.answer(
                translations[selected_lang]['lang_changed'],
                reply_markup=types.ReplyKeyboardRemove()
            )
            
            # Asosiy menyuni ko'rsatish
            await message.answer(
                translations[selected_lang]['main_menu'],
                reply_markup=get_main_keyboard(user_id, selected_lang)
            )
            await state.clear()
        else:
            # New user registration
            await state.update_data(lang=selected_lang)
            await message.answer(
                translations[selected_lang]['enter_name'],
                reply_markup=types.ReplyKeyboardRemove()
            )
            await state.set_state(UserStates.waiting_for_name)
    except Exception as e:
        logger.error(f"Error in process_language: {e}")
        await message.answer("Xatolik yuz berdi. Iltimos qaytadan urinib ko'ring.")

@dp.message(UserStates.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    """Process user name"""
    try:
        user_id = message.from_user.id
        name = html.escape(message.text[:100])  # Sanitize input
        
        await state.update_data(name=name)
        
        data = await state.get_data()
        lang = data.get('lang', 'uz')
        
        await message.answer(
            translations[lang]['enter_phone'],
            reply_markup=get_phone_keyboard(lang)
        )
        await state.set_state(UserStates.waiting_for_phone)
    except Exception as e:
        logger.error(f"Error in process_name: {e}")

@dp.message(UserStates.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    """Process phone number"""
    try:
        user_id = message.from_user.id
        
        if message.contact:
            phone = message.contact.phone_number
        else:
            phone = message.text.strip()
            # Simple phone validation
            if not phone.replace('+', '').replace(' ', '').isdigit():
                data = await state.get_data()
                lang = data.get('lang', 'uz')
                await message.answer(translations[lang]['invalid_phone'])
                return
        
        data = await state.get_data()
        name = data.get('name', 'User')
        lang = data.get('lang', 'uz')
        
        # Save user to database
        db.add_user(user_id, name, phone, lang)
        
        await message.answer(
            translations[lang]['thanks'],
            reply_markup=types.ReplyKeyboardRemove()
        )
        
        await message.answer(
            translations[lang]['main_menu'],
            reply_markup=get_main_keyboard(user_id, lang)
        )
        
        await state.clear()
    except Exception as e:
        logger.error(f"Error in process_phone: {e}")

# Boks Ring Qirollari - Reply Keyboard bilan
@dp.message(lambda message: message.text in ['👑 Boks Ring Qirollari', '👑 Короли бокса', '👑 Boxing Ring Kings'])
async def boxing_kings(message: types.Message, state: FSMContext):
    """Show boxing kings with reply keyboard"""
    try:
        user_id = message.from_user.id
        user = db.get_user(user_id)
        lang = user[4] if user and len(user) > 4 else 'uz'
        
        # Create reply keyboard with boxers
        keyboard = get_fighters_reply_keyboard(boxers, lang, 'boxing')
        
        await message.answer(
            get_text(user_id, 'select_boxer'),
            reply_markup=keyboard
        )
        await state.set_state(UserStates.viewing_boxers)
    except Exception as e:
        logger.error(f"Error in boxing_kings: {e}")

# UFC Janglari - Reply Keyboard bilan
@dp.message(lambda message: message.text in ['⚔️ UFC Janglari', '⚔️ Бои UFC', '⚔️ UFC Fights'])
async def ufc_fights(message: types.Message, state: FSMContext):
    """Show UFC fighters with reply keyboard"""
    try:
        user_id = message.from_user.id
        user = db.get_user(user_id)
        lang = user[4] if user and len(user) > 4 else 'uz'
        
        # Create reply keyboard with UFC fighters
        keyboard = get_fighters_reply_keyboard(ufc_fighters, lang, 'ufc')
        
        await message.answer(
            get_text(user_id, 'select_ufc_fighter'),
            reply_markup=keyboard
        )
        await state.set_state(UserStates.viewing_ufc)
    except Exception as e:
        logger.error(f"Error in ufc_fights: {e}")

# Handle boxer selection from reply keyboard
@dp.message(UserStates.viewing_boxers)
async def handle_boxer_selection(message: types.Message, state: FSMContext):
    """Handle boxer selection from reply keyboard"""
    try:
        user_id = message.from_user.id
        
        # Find selected boxer
        selected_boxer = None
        for boxer in boxers:
            if message.text == boxer['name']:
                selected_boxer = boxer
                break
        
        if selected_boxer:
            # Show fighter info with inline options
            await message.answer(
                get_text(user_id, 'fighter_info', 
                        name=selected_boxer['name'],
                        fights=selected_boxer['fights'],
                        wins=selected_boxer['wins'],
                        losses=selected_boxer['losses'],
                        draws=selected_boxer['draws']),
                reply_markup=create_fight_options_keyboard(selected_boxer['id'], user_id)
            )
        elif message.text == get_text(user_id, 'back_to_menu'):
            # Back to main menu
            user = db.get_user(user_id)
            lang = user[4] if user and len(user) > 4 else 'uz'
            await message.answer(
                get_text(user_id, 'main_menu'),
                reply_markup=get_main_keyboard(user_id, lang)
            )
            await state.clear()
        else:
            # Invalid selection
            await message.answer(get_text(user_id, 'choose_fighter'))
    except Exception as e:
        logger.error(f"Error in handle_boxer_selection: {e}")

# Handle UFC fighter selection from reply keyboard
@dp.message(UserStates.viewing_ufc)
async def handle_ufc_selection(message: types.Message, state: FSMContext):
    """Handle UFC fighter selection from reply keyboard"""
    try:
        user_id = message.from_user.id
        
        # Find selected UFC fighter
        selected_fighter = None
        for fighter in ufc_fighters:
            if message.text == fighter['name']:
                selected_fighter = fighter
                break
        
        if selected_fighter:
            # Show fighter info with inline options
            await message.answer(
                get_text(user_id, 'fighter_info', 
                        name=selected_fighter['name'],
                        fights=selected_fighter['fights'],
                        wins=selected_fighter['wins'],
                        losses=selected_fighter['losses'],
                        draws=selected_fighter['draws']),
                reply_markup=create_fight_options_keyboard(selected_fighter['id'], user_id)
            )
        elif message.text == get_text(user_id, 'back_to_menu'):
            # Back to main menu
            user = db.get_user(user_id)
            lang = user[4] if user and len(user) > 4 else 'uz'
            await message.answer(
                get_text(user_id, 'main_menu'),
                reply_markup=get_main_keyboard(user_id, lang)
            )
            await state.clear()
        else:
            # Invalid selection
            await message.answer(get_text(user_id, 'choose_fighter'))
    except Exception as e:
        logger.error(f"Error in handle_ufc_selection: {e}")

@dp.message(lambda message: message.text in ['💰 Pullik Janglarni Ko\'rish', '💰 Платные бои', '💰 Paid Fights'])
async def paid_fights(message: types.Message):
    """Show paid fights"""
    try:
        user_id = message.from_user.id
        fights = db.get_fights(paid_only=True)
        
        if not fights:
            await message.answer(get_text(user_id, 'no_fights'))
            return
        
        builder = InlineKeyboardBuilder()
        for fight in fights:
            builder.row(InlineKeyboardButton(
                text=f"{fight[2]} - {fight[3]} so'm",
                callback_data=f"buy_fight_{fight[0]}"
            ))
        builder.row(InlineKeyboardButton(
            text=get_text(user_id, 'back_to_menu'),
            callback_data="back_to_main"
        ))
        
        await message.answer(
            get_text(user_id, 'paid_fights_list'),
            reply_markup=builder.as_markup()
        )
    except Exception as e:
        logger.error(f"Error in paid_fights: {e}")

@dp.message(lambda message: message.text in ['👨‍💼 Admin Bilan Aloqa', '👨‍💼 Связаться с админом', '👨‍💼 Contact Admin'])
async def contact_admin(message: types.Message):
    """Contact admin"""
    try:
        admin_phone = "+998880445550"
        user_id = message.from_user.id
        
        text = get_text(user_id, 'contact_admin') + f"\n\n📞 {admin_phone}"
        await message.answer(text)
    except Exception as e:
        logger.error(f"Error in contact_admin: {e}")

@dp.message(lambda message: message.text in ['💭 Takliflar va Fikrlar', '💭 Предложения и отзывы', '💭 Suggestions & Feedback'])
async def feedback(message: types.Message, state: FSMContext):
    """Start feedback process"""
    try:
        user_id = message.from_user.id
        await message.answer(
            get_text(user_id, 'feedback') + "\n\n✍️ Fikringizni yozib qoldiring:"
        )
        await state.set_state(UserStates.waiting_for_feedback)
    except Exception as e:
        logger.error(f"Error in feedback: {e}")

@dp.message(UserStates.waiting_for_feedback)
async def process_feedback(message: types.Message, state: FSMContext):
    """Process feedback"""
    try:
        user_id = message.from_user.id
        feedback_text = html.escape(message.text[:500])
        
        # Save feedback to database
        db.add_feedback(user_id, feedback_text)
        
        # Notify admins
        admins = os.getenv('ADMIN_IDS', '').split(',')
        for admin_id in admins:
            if admin_id.strip():
                try:
                    await bot.send_message(
                        int(admin_id),
                        f"💭 Yangi fikr:\n\nFoydalanuvchi: {user_id}\nXabar: {feedback_text}"
                    )
                except:
                    pass
        
        # Return to main menu
        user = db.get_user(user_id)
        lang = user[4] if user and len(user) > 4 else 'uz'
        await message.answer(
            get_text(user_id, 'feedback_sent'),
            reply_markup=get_main_keyboard(user_id, lang)
        )
        await state.clear()
    except Exception as e:
        logger.error(f"Error in process_feedback: {e}")

# Callback query handlers
@dp.callback_query(lambda c: c.data.startswith('free_fights_'))
async def free_fights_callback(callback: types.CallbackQuery):
    """Show free fights for fighter"""
    try:
        fighter_id = int(callback.data.split('_')[2])
        user_id = callback.from_user.id
        
        # Get free fights from database
        fights = db.get_fights(fighter_id=fighter_id, paid_only=False)
        
        if not fights:
            await callback.message.edit_text(
                get_text(user_id, 'no_fights'),
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(
                        text=get_text(user_id, 'back_to_menu'),
                        callback_data="back_to_main"
                    )
                ]])
            )
            await callback.answer()
            return
        
        await callback.message.delete()
        
        # Show all free fights with protection
        for fight in fights:
            if fight[4]:  # video_id
                await callback.message.answer_video(
                    fight[4],
                    caption=f"🥊 {fight[2]}\n\n{get_text(user_id, 'content_protected')}",
                    **protect_content_kwargs()
                )
        
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in free_fights_callback: {e}")
        await callback.answer("Xatolik yuz berdi")

@dp.callback_query(lambda c: c.data.startswith('paid_fights_'))
async def paid_fights_callback(callback: types.CallbackQuery):
    """Show paid fights for fighter"""
    try:
        fighter_id = int(callback.data.split('_')[2])
        user_id = callback.from_user.id
        
        # Get paid fights from database
        fights = db.get_fights(fighter_id=fighter_id, paid_only=True)
        
        if not fights:
            await callback.message.edit_text(
                get_text(user_id, 'no_fights'),
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(
                        text=get_text(user_id, 'back_to_menu'),
                        callback_data="back_to_main"
                    )
                ]])
            )
            await callback.answer()
            return
        
        # Show purchase options
        builder = InlineKeyboardBuilder()
        for fight in fights:
            builder.row(InlineKeyboardButton(
                text=get_text(user_id, 'purchase_fight', price=fight[3]),
                callback_data=f"buy_fight_{fight[0]}"
            ))
        builder.row(InlineKeyboardButton(
            text=get_text(user_id, 'back_to_menu'),
            callback_data="back_to_main"
        ))
        
        await callback.message.edit_text(
            get_text(user_id, 'paid_fights_list'),
            reply_markup=builder.as_markup()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in paid_fights_callback: {e}")
        await callback.answer("Xatolik yuz berdi")

@dp.callback_query(lambda c: c.data.startswith('buy_fight_'))
async def buy_fight_callback(callback: types.CallbackQuery):
    """Handle fight purchase"""
    try:
        fight_id = int(callback.data.split('_')[2])
        user_id = callback.from_user.id
        
        # Get fight details
        fight = db.get_fight(fight_id)
        
        if fight:
            await callback.message.edit_text(
                get_text(user_id, 'payment_info', price=fight[3]),
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(
                        text=get_text(user_id, 'back_to_menu'),
                        callback_data="back_to_main"
                    )
                ]])
            )
            
            # Notify admin about purchase
            admins = os.getenv('ADMIN_IDS', '').split(',')
            for admin_id in admins:
                if admin_id.strip():
                    try:
                        await bot.send_message(
                            int(admin_id),
                            f"💰 Yangi to'lov so'rovi:\n\nFoydalanuvchi: {user_id}\nJang: {fight[2]}\nNarx: {fight[3]} so'm"
                        )
                    except:
                        pass
        
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in buy_fight_callback: {e}")
        await callback.answer("Xatolik yuz berdi")

@dp.callback_query(lambda c: c.data == 'back_to_main')
async def back_to_main_callback(callback: types.CallbackQuery, state: FSMContext):
    """Back to main menu"""
    try:
        user_id = callback.from_user.id
        user = db.get_user(user_id)
        lang = user[4] if user and len(user) > 4 else 'uz'
        
        await callback.message.delete()
        await callback.message.answer(
            get_text(user_id, 'main_menu'),
            reply_markup=get_main_keyboard(user_id, lang)
        )
        await state.clear()
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in back_to_main_callback: {e}")

# Error handler
@dp.error()
async def error_handler(event: types.ErrorEvent):
    """Handle errors globally"""
    logger.error(f"Update {event.update} caused error {event.exception}")
    try:
        if event.update.message:
            await event.update.message.answer("❌ Xatolik yuz berdi. Iltimos qaytadan urinib ko'ring.")
        elif event.update.callback_query:
            await event.update.callback_query.answer("❌ Xatolik yuz berdi")
    except:
        pass

# Main function
async def main():
    """Main function"""
    try:
        # Start keep_alive
        keep_alive()
        
        # Initialize database
        db.create_tables()
        
        # Notify admin that bot is started
        admins = os.getenv('ADMIN_IDS', '').split(',')
        for admin_id in admins:
            if admin_id.strip():
                try:
                    await bot.send_message(
                        int(admin_id),
                        "✅ Bot ishga tushdi!\n\nBot muvaffaqiyatli ishga tushirildi."
                    )
                except:
                    pass
        
        logger.info("Bot started!")
        print("🤖 Bot ishga tushdi!")
        
        # Start polling
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error in main: {e}")

if __name__ == '__main__':
    asyncio.run(main())