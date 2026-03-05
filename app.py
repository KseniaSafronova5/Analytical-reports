import streamlit as st
import pandas as pd
import requests
import io

# --- 1. КОНФИГУРАЦИЯ СТРАНИЦЫ ---
st.set_page_config(page_title="Аналитика без аналитика", layout="wide")

# Инициализация истории чата в самом начале
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 2. ФУНКЦИЯ ДЛЯ ШАБЛОНА ---
def generate_template():
    template_data = {
        'Дата': ['2026-02-01', '2026-02-01', '2026-02-02'],
        'Товар': ['Пример товара А', 'Пример товара Б', 'Пример товара В'],
        'Категория': ['Категория 1', 'Категория 2', 'Категория 1'],
        'Сумма_чека': [1000, 500, 1200],
        'Маржа': [200, 100, 300]
    }
    df_temp = pd.DataFrame(template_data)
    return df_temp.to_csv(index=False, encoding='utf-8-sig')

# --- 3. САЙДБАР: ИНСТРУКЦИИ, ШАБЛОН И ЛИЦЕНЗИЯ ---
with st.sidebar:
    st.header("📁 Подготовка данных")
    st.write("Используйте этот формат для загрузки:")
    
    csv_template = generate_template()
    st.download_button(
        label="📥 Скачать шаблон CSV",
        data=csv_template,
        file_name="template_sales.csv",
        mime="text/csv"
    )
    
    st.divider()
    st.info("""
    **Требования:**
    - Колонки: Дата, Товар, Категория, Сумма_чека, Маржа.
    - Формат даты: ГГГГ-ММ-ДД.
    """)

    st.divider()
    st.subheader("🔑 Доступ к Premium")
    license_key = st.text_input("Введите ключ активации ИИ", type="password")
    
    if license_key == "BOSS2026": 
        st.success("Premium активирован! 🔓")
        is_premium = True
    else:
        is_premium = False
        if license_key:
            st.error("Неверный код")
        else:
            st.info("Введите ключ для доступа к ИИ-чату")

# --- 4. ОСНОВНОЙ ИНТЕРФЕЙС ---
st.title("📊 Автоматический отчёт: Продажи")

uploaded_file = st.file_uploader("Выберите CSV файл клиента", type="csv")

if uploaded_file is not None:
    # Загрузка данных
    df = pd.read_csv(uploaded_file)
    required_columns = ['Дата', 'Товар', 'Категория', 'Сумма_чека', 'Маржа']
    actual_columns = list(df.columns)
    missing = [col for col in required_columns if col not in actual_columns]

    if missing:
        st.error(f"⚠️ Ошибка! Не хватает столбцов: {', '.join(missing)}")
        st.stop()

    try:
        # Обработка данных
        df['Дата'] = pd.to_datetime(df['Дата'])
        days_map = {
            'Monday': 'Понедельник', 'Tuesday': 'Вторник', 'Wednesday': 'Среда',
            'Thursday': 'Четверг', 'Friday': 'Пятница', 'Saturday': 'Суббота', 'Sunday': 'Воскресенье'
        }
        df['День_недели'] = df['Дата'].dt.day_name().map(days_map)
        
        st.success("Данные успешно загружены!")

        # 5. Метрики
        total_revenue = df['Сумма_чека'].sum()
        avg_check = df['Сумма_чека'].mean()
        total_margin = df['Маржа'].sum()

        col1, col2, col3 = st.columns(3)
        col1.metric("Общая выручка", f"{total_revenue:,.0f} ₽")
        col2.metric("Средний чек", f"{avg_check:,.0f} ₽")
        col3.metric("Общая маржа", f"{total_margin:,.0f} ₽")

        # 6. График
        st.subheader("Средние продажи по дням недели")
        order = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
        weekly_sales = df.groupby('День_недели')['Сумма_чека'].mean().reindex(order)
        st.bar_chart(weekly_sales)

        # 7. Аномалии
        min_day = weekly_sales.idxmin()
        mean_val = weekly_sales.mean()
        anomaly_status = "Норма"
        if weekly_sales[min_day] < mean_val * 0.5:
            anomaly_status = f"⚠️ АНОМАЛИЯ В {min_day.upper()}"
            st.error(f"Внимание! Продажи в {min_day} критически ниже среднего.")

        st.divider()

        # 8. Отправка в Telegram
        st.subheader("📢 Уведомления")
        N8N_URL = "https://ksautomationai.com/webhook/8936abb5-3ffd-4ca3-86dd-cf57c1c56e4b"

        if st.button('🚀 Отправить отчет в Telegram'):
            payload = {
                "revenue": f"{total_revenue:,.0f}",
                "avg_check": f"{avg_check:,.0f}",
                "margin": f"{total_margin:,.0f}",
                "anomaly": anomaly_status,
                "file_name": uploaded_file.name
            }
            try:
                res = requests.post(N8N_URL, json=payload)
                if res.status_code == 200:
                    st.success("✅ Отчет отправлен!")
                else:
                    st.error("❌ Ошибка сервера n8n")
            except Exception as e:
                st.error(f"🆘 Ошибка: {e}")

        # 9. ЧАТ С ИИ (PREMIUM / FREE)
        st.divider()
        st.subheader("💬 Чат с вашим ИИ-аналитиком")

        if not is_premium:
            # Блок для бесплатных пользователей
            col_img, col_txt = st.columns([1, 2])
            with col_img:
                st.image("https://img.freepik.com/free-vector/ai-technology-concept_23-2148332158.jpg")
            with col_txt:
                st.markdown("""
                ### ✨ Усильте аналитику с Premium
                ИИ поможет вам:
                * 🧠 Понять причины падения продаж
                * 📈 Спрогнозировать выручку на месяц
                * 💡 Получить советы по закупкам
                
                [Получить доступ](https://t.me/kseniasafronova5)
                """)
            st.chat_input("Чат доступен в Premium-версии", disabled=True)
        
        else:
            # Блок для Premium пользователей
            # 1. Показываем историю
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            # 2. Поле ввода
            if prompt := st.chat_input("Задайте вопрос по вашим данным..."):
                # Добавляем вопрос в историю
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                # Отправка в n8n
                with st.chat_message("assistant"):
                    with st.spinner("ИИ анализирует..."):
                        data_json = df.head(30).to_json(orient='records')
                        chat_payload = {
                            "question": prompt,
                            "data": data_json,
                            "context": "Retail Analytics Mode"
                        }
                        try:
                            chat_res = requests.post(N8N_URL, json=chat_payload)
                            answer = chat_res.json().get("output", "Бот не вернул ответ.")
                        except:
                            answer = "Ошибка связи с ИИ. Проверьте n8n."
                        
                        st.markdown(answer)
                
                # Добавляем ответ в историю
                st.session_state.messages.append({"role": "assistant", "content": answer})

    except Exception as e:
        st.error(f"Ошибка при обработке: {e}")

else:
    st.info("Загрузите CSV файл, чтобы увидеть отчет. Шаблон — в меню слева.")