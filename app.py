import streamlit as st
from script import restore_spaces

# Настройка страницы
st.set_page_config(
    page_title="Восстановление пробелов в тексте",
    page_icon="👋",
    layout="wide"
)

st.title("💬 Восстановим же пробелы в тексте")
st.write("Напишите любой текст без пробелов и я восстановлю их для вас")

text = st.text_input("Ваш текст:", placeholder="Мамамылараму")

if st.button("Восставноить пробелы"):
    if text:
        with st.spinner("Думаю..."):
            try:
                answer = restore_spaces(text)
                st.success(f"Ответ: {answer}")
            except Exception as e:
                st.error(f"Произошла ошибка: {e}")
    else:
        st.warning("Пожалуйста, введите текст.")