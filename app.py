import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Аналитика без аналитика", layout="wide")

st.title("📊 Автоматический отчёт: Продажи")

# Загрузчик файлов
uploaded_file = st.file_uploader("Выберите CSV файл клиента", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df['Дата'] = pd.to_datetime(df['Дата'])
    
    # Перевод дней недели
    days_map = {
        'Monday': 'Понедельник', 'Tuesday': 'Вторник', 'Wednesday': 'Среда',
        'Thursday': 'Четверг', 'Friday': 'Пятница', 'Saturday': 'Суббота', 'Sunday': 'Воскресенье'
    }
    df['День_недели'] = df['Дата'].dt.day_name().map(days_map)
    
    st.success("Данные загружены!")

    # --- ВОТ ЭТОТ ПРОПУЩЕННЫЙ БЛОК РАСЧЕТОВ ---
    total_revenue = df['Сумма_чека'].sum()
    avg_check = df['Сумма_чека'].mean()
    total_margin = df['Маржа'].sum()

    # Отображение метрик в интерфейсе
    col1, col2, col3 = st.columns(3)
    col1.metric("Общая выручка", f"{total_revenue:,.0f} ₽")
    col2.metric("Средний чек", f"{avg_check:,.0f} ₽")
    col3.metric("Общая маржа", f"{total_margin:,.0f} ₽")

    # График
    st.subheader("Средние продажи по дням недели")
    weekly_sales = df.groupby('День_недели')['Сумма_чека'].mean().reindex(
        ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
    )
    st.bar_chart(weekly_sales)

    # Проверка аномалий
    anomaly_status = "Норма"
    if weekly_sales['Воскресенье'] < weekly_sales.mean() * 0.5:
        anomaly_status = "🚨 АНОМАЛИЯ В ВОСКРЕСЕНЬЕ"
        st.error("Внимание! Выявлена аномалия: продажи в воскресенье критически ниже среднего.")

    st.divider()

    # --- БЛОК СВЯЗИ С N8N ---
    st.subheader("Уведомления")
    N8N_WEBHOOK_URL = "https://ksu55.app.n8n.cloud/webhook/8936abb5-3ffd-4ca3-86dd-cf57c1c56e4b"

    if st.button('🚀 Отправить отчет в Telegram через n8n'):
        # Теперь переменные существуют и подставятся сюда:
        payload = {
            "revenue": f"{total_revenue:,.0f}",
            "avg_check": f"{avg_check:,.0f}",
            "margin": f"{total_margin:,.0f}",
            "anomaly": anomaly_status,
            "file_name": uploaded_file.name
        }
        
        try:
            response = requests.post(N8N_WEBHOOK_URL, json=payload)
            if response.status_code == 200:
                st.success("✅ Отчет успешно отправлен в n8n!")
            else:
                st.error(f"❌ Ошибка n8n: Код {response.status_code}")
        except Exception as e:
            st.error(f"🆘 Ошибка соединения: {e}")

else:
    st.info("Пожалуйста, загрузите CSV файл для начала анализа.")

