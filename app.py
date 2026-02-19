import streamlit as st
import pandas as pd

st.set_page_config(page_title="Аналитика без аналитика", layout="wide")

st.title("📊 Автоматический отчёт: Продажи")

# Загрузчик файлов
uploaded_file = st.file_uploader("Выберите CSV файл клиента", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df['Дата'] = pd.to_datetime(df['Дата'])
    df['День_недели'] = df['Дата'].dt.day_name()
    
    st.success("Данные загружены!")

    # Метрики
    col1, col2, col3 = st.columns(3)
    col1.metric("Общая выручка", f"{df['Сумма_чека'].sum():,.0f} ₽")
    col2.metric("Средний чек", f"{df['Сумма_чека'].mean():,.0f} ₽")
    col3.metric("Общая маржа", f"{df['Маржа'].sum():,.0f} ₽")

    # График аномалий
    st.subheader("Средние продажи по дням недели")
    weekly_sales = df.groupby('День_недели')['Сумма_чека'].mean().reindex(
        ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    )
    st.bar_chart(weekly_sales)

    if weekly_sales['Sunday'] < weekly_sales.mean() * 0.5:
        st.error("🚨 Внимание! Выявлена аномалия: продажи в воскресенье критически ниже среднего.")
else:
    st.info("Пожалуйста, загрузите CSV файл для начала анализа.")
