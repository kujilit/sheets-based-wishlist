import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import os
from .config import GOOGLE_SCOPES, CREDENTIALS_PATH


@st.cache_resource
def get_google_sheets_client():
    """Инициализация клиента Google Sheets"""
    try:
        if not os.path.exists(CREDENTIALS_PATH):
            st.error(f"Файл с учетными данными не найден: {CREDENTIALS_PATH}")
            st.info("Загрузите credentials.json из Google Cloud Console")
            return None
            
        credentials = Credentials.from_service_account_file(
            CREDENTIALS_PATH, 
            scopes=GOOGLE_SCOPES
        )
        return gspread.authorize(credentials)
    except Exception as e:
        st.error(f"Ошибка при инициализации Google Sheets: {str(e)}")
        return None


def get_sheet_from_url(client, url, sheet_name):
    """Получение листа Google Sheets по URL"""
    try:
        sheet_id = url.split('/d/')[1].split('/')[0]
        spreadsheet = client.open_by_key(sheet_id)
        return spreadsheet.worksheet(sheet_name), spreadsheet.title
    except Exception as e:
        st.error(f"Ошибка при открытии таблицы: {str(e)}")
        return None, None