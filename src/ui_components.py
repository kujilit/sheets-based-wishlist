import streamlit as st
from .data_operations import (
    add_wishlist_item, update_wishlist_item, delete_wishlist_item,
    validate_item_data, prepare_item_data
)


def render_view_tab(df, sheet):
    """Отображение вкладки просмотра"""
    st.subheader("Текущий вишлист")
    
    if df.empty:
        st.info("Вишлист пуст. Добавьте первый элемент во вкладке 'Добавить/Редактировать'")
        return
    
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


def render_add_form(sheet):
    """Отображение формы добавления"""
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
            is_valid, error_msg = validate_item_data(gift_name)
            if not is_valid:
                st.error(error_msg)
                return
            
            item_data = prepare_item_data(gift_name, category, description, link)
            
            if add_wishlist_item(sheet, item_data):
                st.success("Элемент добавлен в вишлист!")
                st.rerun()


def render_edit_form(df, sheet):
    """Отображение формы редактирования"""
    if df.empty:
        return
    
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
                is_valid, error_msg = validate_item_data(edit_gift_name)
                if not is_valid:
                    st.error(error_msg)
                    return
                
                item_data = prepare_item_data(
                    edit_gift_name, edit_category, edit_description, edit_link,
                    selected=selected_row.get('Выбрано', False)
                )
                
                if update_wishlist_item(sheet, edit_item + 2, item_data):
                    st.success("Элемент обновлен!")
                    st.rerun()


def render_add_edit_tab(df, sheet):
    """Отображение вкладки добавления/редактирования"""
    render_add_form(sheet)
    render_edit_form(df, sheet)