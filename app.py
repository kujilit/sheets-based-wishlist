import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import os
from dotenv import load_dotenv
import json

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource
def get_google_sheets_client():
    """Инициализация клиента Google Sheets"""
    try:
        credentials_path = os.getenv('GOOGLE_CREDENTIALS_PATH', './credentials.json')
        
        if not os.path.exists(credentials_path):
            st.error(f"Файл с учетными данными не найден: {credentials_path}")
            st.info("Загрузите credentials.json из Google Cloud Console")
            return None
            
        credentials = Credentials.from_service_account_file(
            credentials_path, 
            scopes=SCOPES
        )
        return gspread.authorize(credentials)
    except Exception as e:
        st.error(f"Ошибка при инициализации Google Sheets: {str(e)}")
        return None

def get_sheet_from_url(client, url):
    """Получение листа Google Sheets по URL"""
    try:
        sheet_id = url.split('/d/')[1].split('/')[0]
        spreadsheet = client.open_by_key(sheet_id)
        sheet_name = os.getenv('SHEET_NAME', 'Sheet1')
        return spreadsheet.worksheet(sheet_name)
    except Exception as e:
        st.error(f"Ошибка при открытии таблицы: {str(e)}")
        return None

def load_wishlist_data(sheet):
    """Загрузка данных вишлиста"""
    try:
        data = sheet.get_all_records()
        if not data:
            headers = ['Выбрано', 'Подарок', 'Категория', 'Описание', 'Ссылка']
            sheet.append_row(headers)
            return pd.DataFrame(columns=headers)
        
        df = pd.DataFrame(data)
        # Найти правильный столбец для статуса выбора
        selected_col = None
        for col in df.columns:
            if 'выбрано' in col.lower():
                selected_col = col
                break
        
        if selected_col:
            df['Выбрано'] = df[selected_col].astype(str).str.lower().map({'true': True, 'false': False}).fillna(False)
            if selected_col != 'Выбрано':
                df = df.drop(columns=[selected_col])
        else:
            df['Выбрано'] = False
        return df
    except Exception as e:
        st.error(f"Ошибка при загрузке данных: {str(e)}")
        return pd.DataFrame()

def add_wishlist_item(sheet, item_data):
    """Добавление нового элемента в вишлист"""
    try:
        row_data = [
            "" if not item_data['selected'] else "TRUE",
            item_data['gift'],
            item_data['category'],
            item_data['description'],
            item_data['link']
        ]
        sheet.append_row(row_data)
        return True
    except Exception as e:
        st.error(f"Ошибка при добавлении элемента: {str(e)}")
        return False

def update_wishlist_item(sheet, row_num, item_data):
    """Обновление элемента вишлиста"""
    try:
        row_data = [
            "" if not item_data['selected'] else "TRUE",
            item_data['gift'],
            item_data['category'],
            item_data['description'],
            item_data['link']
        ]
        for col, value in enumerate(row_data, 1):
            sheet.update_cell(row_num, col, value)
        return True
    except Exception as e:
        st.error(f"Ошибка при обновлении элемента: {str(e)}")
        return False

def delete_wishlist_item(sheet, row_num):
    """Удаление элемента из вишлиста"""
    try:
        sheet.delete_rows(row_num)
        return True
    except Exception as e:
        st.error(f"Ошибка при удалении элемента: {str(e)}")
        return False

def main():
    st.set_page_config(
        page_title="Вишлист",
        page_icon="🎁",
        layout="wide"
    )
    
    st.title("Вишлист")
    
    sheets_url = os.getenv('SHEETS_URL')
    st.write(f"**Ссылка на таблицу:** [перейти]({sheets_url})")

    if not sheets_url or 'YOUR_SHEET_ID' in sheets_url:
        st.error("Пожалуйста, настройте SHEETS_URL в файле .env")
        st.info("1. Создайте Google Sheets таблицу\n2. Поделитесь ей с email из credentials.json\n3. Скопируйте URL в .env файл")
        return
    
    client = get_google_sheets_client()
    if not client:
        return
    
    sheet = get_sheet_from_url(client, sheets_url)
    if not sheet:
        return
    
    df = load_wishlist_data(sheet)
    
    tab1, tab2 = st.tabs(["📋 Просмотр", "➕ Добавить/Редактировать"])
    
    with tab1:
        st.subheader("Текущий вишлист")
        
        if df.empty:
            st.info("Вишлист пуст. Добавьте первый элемент во вкладке 'Добавить/Редактировать'")
        else:
            col1, col2 = st.columns([3, 1])
            
            with col2:
                
                category_filter = st.selectbox(
                    "Категория",
                    ["Все"] + list(df['Категория'].unique()) if 'Категория' in df.columns else ["Все"]
                )
            
            filtered_df = df.copy()
                
            if category_filter != "Все" and 'Категория' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['Категория'] == category_filter]
            
            with col1:
                for idx, row in filtered_df.iterrows():
                    with st.expander(f"{row.get('Подарок', 'Без названия')}"):
                        col_info, col_actions = st.columns([3, 1])
                        
                        with col_info:
                            st.write(f"**Категория:** {row.get('Категория', 'Не указана')}")
                            st.write(f"**Описание:** {row.get('Описание', 'Нет описания')}")
                            if row.get('Ссылка'):
                                st.write(f"**Ссылка:** [Перейти]({row['Ссылка']})")
                        
                        with col_actions:
                            if st.button(f"🗑️ Удалить", key=f"delete_{idx}"):
                                if delete_wishlist_item(sheet, idx + 2):
                                    st.success("Элемент удален!")
                                    st.rerun()
    
    with tab2:
        st.subheader("Добавить новый элемент")
        
        with st.form("add_item_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                gift_name = st.text_input("Название подарка *", key="gift_name")
                category = st.text_input("Категория", key="category")
            
            with col2:
                description = st.text_area("Описание", key="description")
                link = st.text_input("Ссылка", key="link")
            
            submitted = st.form_submit_button("Добавить в вишлист")
            
            if submitted:
                if not gift_name.strip():
                    st.error("Пожалуйста, укажите название подарка")
                else:
                    item_data = {
                        'selected': False,
                        'gift': gift_name.strip(),
                        'category': category.strip(),
                        'description': description.strip(),
                        'link': link.strip()
                    }
                    
                    if add_wishlist_item(sheet, item_data):
                        st.success("Элемент добавлен в вишлист!")
                        st.rerun()
        
        if not df.empty:
            st.subheader("Редактировать существующие элементы")
            
            edit_item = st.selectbox(
                "Выберите элемент для редактирования",
                options=range(len(df)),
                format_func=lambda x: df.iloc[x].get('Подарок', f'Элемент {x+1}'),
                key="edit_select"
            )
            
            if edit_item is not None:
                selected_row = df.iloc[edit_item]
                
                with st.form("edit_item_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        edit_gift_name = st.text_input(
                            "Название подарка *", 
                            value=selected_row.get('Подарок', ''),
                            key="edit_gift_name"
                        )
                        edit_category = st.text_input(
                            "Категория", 
                            value=selected_row.get('Категория', ''),
                            key="edit_category"
                        )
                    
                    with col2:
                        edit_description = st.text_area(
                            "Описание", 
                            value=selected_row.get('Описание', ''),
                            key="edit_description"
                        )
                        edit_link = st.text_input(
                            "Ссылка", 
                            value=selected_row.get('Ссылка', ''),
                            key="edit_link"
                        )
                    
                    updated = st.form_submit_button("Обновить элемент")
                    
                    if updated:
                        if not edit_gift_name.strip():
                            st.error("Пожалуйста, укажите название подарка")
                        else:
                            item_data = {
                                'selected': selected_row.get('Выбрано', False),
                                'gift': edit_gift_name.strip(),
                                'category': edit_category.strip(),
                                'description': edit_description.strip(),
                                'link': edit_link.strip()
                            }
                            
                            if update_wishlist_item(sheet, edit_item + 2, item_data):
                                st.success("Элемент обновлен!")
                                st.rerun()

if __name__ == "__main__":
    main()