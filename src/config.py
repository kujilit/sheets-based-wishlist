import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

CREDENTIALS_PATH = os.getenv('GOOGLE_CREDENTIALS_PATH', './credentials.json')
SHEETS_URL = os.getenv('SHEETS_URL')
SHEET_NAME = os.getenv('SHEET_NAME', 'Sheet1')

WISHLIST_COLUMNS = ['Выбрано', 'Подарок', 'Категория', 'Описание', 'Ссылка']

PAGE_CONFIG = {
    "page_title": "Вишлист",
    "page_icon": "🎁",
    "layout": "wide"
}