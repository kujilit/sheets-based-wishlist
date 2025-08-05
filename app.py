import streamlit as st
from src.config import PAGE_CONFIG, SHEETS_URL, SHEET_NAME
from src.google_sheets import get_google_sheets_client, get_sheet_from_url
from src.data_operations import load_wishlist_data
from src.ui_components import render_view_tab, render_add_edit_tab

def main():
    st.set_page_config(**PAGE_CONFIG)
    
    if not SHEETS_URL or 'YOUR_SHEET_ID' in SHEETS_URL:
        st.title("Вишлист")
        st.error("Пожалуйста, настройте SHEETS_URL в файле .env")
        st.info("1. Создайте Google Sheets таблицу\n2. Поделитесь ей с email из credentials.json\n3. Скопируйте URL в .env файл")
        return
    
    client = get_google_sheets_client()
    if not client:
        st.title("Вишлист")
        return
    
    sheet, spreadsheet_title = get_sheet_from_url(client, SHEETS_URL, SHEET_NAME)
    if not sheet:
        st.title("Вишлист")
        return
    
    st.title(spreadsheet_title or "Вишлист")
    st.write(f"**Ссылка на таблицу:** [перейти]({SHEETS_URL})")
    
    df = load_wishlist_data(sheet)
    
    tab1, tab2 = st.tabs(["📋 Просмотр", "➕ Добавить/Редактировать"])
    
    with tab1:
        render_view_tab(df, sheet)
    
    with tab2:
        render_add_edit_tab(df, sheet)

if __name__ == "__main__":
    main()