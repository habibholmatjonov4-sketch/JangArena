from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

def get_language_keyboard():
    """Language selection keyboard"""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text='🇺🇿 UZ'),
        KeyboardButton(text='🇷🇺 RU'),
        KeyboardButton(text='🇬🇧 EN')
    )
    builder.adjust(3)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

def get_phone_keyboard(lang='uz'):
    """Phone number request keyboard"""
    texts = {
        'uz': '📞 Telefon Raqamni Yuborish',
        'ru': '📞 Отправить номер',
        'en': '📞 Send Phone Number'
    }
    
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text=texts[lang], request_contact=True))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

def get_main_keyboard(user_id=None, lang='uz'):
    """Main menu keyboard"""
    texts = {
        'uz': {
            'boxing': '👑 Boks Ring Qirollari',
            'ufc': '⚔️ UFC Janglari',
            'change_lang': '🔄 Tilni O\'zgartirish',
            'paid': '💰 Pullik Janglarni Ko\'rish',
            'contact': '👨‍💼 Admin Bilan Aloqa',
            'feedback': '💭 Takliflar va Fikrlar'
        },
        'ru': {
            'boxing': '👑 Короли бокса',
            'ufc': '⚔️ Бои UFC',
            'change_lang': '🔄 Изменить язык',
            'paid': '💰 Платные бои',
            'contact': '👨‍💼 Связаться с админом',
            'feedback': '💭 Предложения и отзывы'
        },
        'en': {
            'boxing': '👑 Boxing Ring Kings',
            'ufc': '⚔️ UFC Fights',
            'change_lang': '🔄 Change Language',
            'paid': '💰 Paid Fights',
            'contact': '👨‍💼 Contact Admin',
            'feedback': '💭 Suggestions & Feedback'
        }
    }
    
    t = texts.get(lang, texts['uz'])
    
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text=t['boxing']),
        KeyboardButton(text=t['ufc'])
    )
    builder.row(
        KeyboardButton(text=t['change_lang']),
        KeyboardButton(text=t['paid'])
    )
    builder.row(
        KeyboardButton(text=t['contact']),
        KeyboardButton(text=t['feedback'])
    )
    
    return builder.as_markup(resize_keyboard=True)

def get_fighters_reply_keyboard(fighters, lang='uz', category='boxing'):
    """Create reply keyboard with fighters list for users"""
    builder = ReplyKeyboardBuilder()
    
    # Add fighters in rows of 2
    for i in range(0, len(fighters), 2):
        row = []
        row.append(KeyboardButton(text=fighters[i]['name']))
        if i + 1 < len(fighters):
            row.append(KeyboardButton(text=fighters[i + 1]['name']))
        builder.row(*row)
    
    # Add back button
    back_texts = {
        'uz': '🔙 Asosiy Menyu',
        'ru': '🔙 Главное меню',
        'en': '🔙 Main Menu'
    }
    builder.row(KeyboardButton(text=back_texts.get(lang, '🔙 Asosiy Menyu')))
    
    return builder.as_markup(resize_keyboard=True)

def get_admin_keyboard(lang='uz'):
    """Admin panel main keyboard"""
    texts = {
        'uz': {
            'stats': '📊 Statistika',
            'add_fight': '➕ Jang Qo\'shish',
            'users': '👥 Foydalanuvchilar',
            'purchases': '💰 Xaridlar',
            'feedback': '💭 Fikrlar',
            'broadcast': '📢 Xabar Yuborish',
            'settings': '⚙️ Sozlamalar'
        },
        'ru': {
            'stats': '📊 Статистика',
            'add_fight': '➕ Добавить бой',
            'users': '👥 Пользователи',
            'purchases': '💰 Покупки',
            'feedback': '💭 Отзывы',
            'broadcast': '📢 Рассылка',
            'settings': '⚙️ Настройки'
        },
        'en': {
            'stats': '📊 Statistics',
            'add_fight': '➕ Add Fight',
            'users': '👥 Users',
            'purchases': '💰 Purchases',
            'feedback': '💭 Feedback',
            'broadcast': '📢 Broadcast',
            'settings': '⚙️ Settings'
        }
    }
    
    t = texts.get(lang, texts['uz'])
    
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text=t['stats']),
        KeyboardButton(text=t['add_fight'])
    )
    builder.row(
        KeyboardButton(text=t['users']),
        KeyboardButton(text=t['purchases'])
    )
    builder.row(
        KeyboardButton(text=t['feedback']),
        KeyboardButton(text=t['broadcast'])
    )
    builder.row(
        KeyboardButton(text=t['settings'])
    )
    
    return builder.as_markup(resize_keyboard=True)

def get_admin_categories_keyboard():
    """Admin categories selection keyboard"""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text='👑 Boks Ring Qirollari'),
        KeyboardButton(text='⚔️ UFC Janglari')
    )
    builder.row(
        KeyboardButton(text='🔙 Admin Menyu')
    )
    return builder.as_markup(resize_keyboard=True)

def get_admin_fighters_keyboard(fighters):
    """Admin fighters selection keyboard"""
    builder = ReplyKeyboardBuilder()
    
    # Add fighters in rows of 2
    for i in range(0, len(fighters), 2):
        row = []
        row.append(KeyboardButton(text=fighters[i]['name']))
        if i + 1 < len(fighters):
            row.append(KeyboardButton(text=fighters[i + 1]['name']))
        builder.row(*row)
    
    # Add navigation buttons
    builder.row(
        KeyboardButton(text='🔙 Bo\'limlar'),
        KeyboardButton(text='🔙 Admin Menyu')
    )
    
    return builder.as_markup(resize_keyboard=True)