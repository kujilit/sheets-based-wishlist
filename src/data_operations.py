import streamlit as st
import pandas as pd
from .config import WISHLIST_COLUMNS


def load_wishlist_data(sheet):
    """Загрузка данных вишлиста"""
    try:
        data = sheet.get_all_records()
        if not data:
            sheet.append_row(WISHLIST_COLUMNS)
            return pd.DataFrame(columns=WISHLIST_COLUMNS)
        
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


def validate_item_data(gift_name):
    """Валидация данных элемента"""
    if not gift_name.strip():
        return False, "Пожалуйста, укажите название подарка"
    return True, ""


def prepare_item_data(gift, category, description, link, selected=False):
    """Подготовка данных элемента для сохранения"""
    return {
        'selected': selected,
        'gift': gift.strip(),
        'category': category.strip(),
        'description': description.strip(),
        'link': link.strip()
    }