import streamlit as st
import requests
import time

FASTAPI_URL = "http://db_api:8001"
WORKER_URL = "http://worker:8002"  

# Инициализация состояния аутентификации
if 'auth_token' not in st.session_state:
    st.session_state.auth_token = None
if 'user' not in st.session_state:
    st.session_state.user = None

def check_profanity(text: str) -> bool:
    """Проверяет текст на нецензурную лексику"""
    try:
        response = requests.post(
            f"{WORKER_URL}/check",
            json={"text": text},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return False
    except Exception:
        return False

st.set_page_config(page_title="СЫН РЗТ", layout="centered")
def auth_page():
    st.title("СЫН РЗТ - Авторизация")
    
    tab1, tab2 = st.tabs(["🔑 Войти по коду", "Как получить код?"])
    
    with tab1:
        code = st.text_input("Введите код из Telegram бота", 
                           max_chars=4,
                           placeholder="ABCD")
        
        if st.button("Войти", type="primary"):
            if code and len(code) == 4:
                with st.spinner("Проверка кода..."):
                        response = requests.post(
                            f"{FASTAPI_URL}/auth/code",
                            json={"code": code.upper()},
                            timeout=10
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            if data["success"]:
                                st.session_state.auth_token = data["token"]
                                st.session_state.user = data["user"]
                                st.success(f"Добро пожаловать, {data['user']['username']}!")
                                st.rerun()
                            else:
                                st.error(f"Ошибка: {data.get('error', 'Неверный код')}")
        else:
            st.warning("Введите 4-значный код")
    
    with tab2:
        st.markdown("""
        ### Инструкция по получению кода:
        
        1. **Откройте Telegram бота** (ваш музыкальный бот)
        2. **Нажмите кнопку** "Получить код для сайта" в ТГ боте
        3. **Скопируйте 4-значный код** который вам отправит бот
        
        ⚠️ После использования код станет недействительным
        """)
        
        st.info("""
        **Нет доступа к боту?** Зарегистрируйтесь:
        1. Найдите вашего музыкального бота в Telegram
        2. Напишите /start
        3. Получить код для сайта
        """)
    
    st.stop()  

# Проверка авторизации в начале файла
if not st.session_state.auth_token:
    auth_page()

st.title(f"СЫН РЗТ - Добро пожаловать, {st.session_state.user['username']}!")

with st.sidebar:
    st.write(f"👤 **{st.session_state.user['username']}**")
    st.write(f"TG ID: `{st.session_state.user['id']}`")
    
    if st.button("Выйти", type="secondary"):
        st.session_state.auth_token = None
        st.session_state.user = None
        st.rerun()
    
    st.divider()

# Главная страница
st.header("Выберите действие")
action = st.selectbox("Что вы хотите сделать?", 
                     ["Найти треки", "Добавить рецензию", "Посмотреть рецензии", "Добавить новый трек"])

if action == "Найти треки":
    search_type = st.radio("Искать по:", ["Названию", "ID", "Исполнителем"], horizontal=True, key="search_type")
    
    if search_type == "Названию":
        query = st.text_input("Введите название трека")
        if query:
            resp = requests.get(f"{FASTAPI_URL}/find_song", params={"query": query, "type_search": "name"})
            if resp.status_code == 200:
                songs = resp.json()
                if songs:
                    for song in songs:
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"**{song[1]}** - {song[2] or 'Неизвестно'}")
                            st.caption(f"ID: {song[0]}")
                        with col2:
                            if st.button("Добавить рецензию", key=f"add_{song[0]}"):
                                st.session_state.review_song = song[0]
                                st.rerun()
                else:
                    st.info("Треки не найдены")
    
    elif search_type == "ID":
        song_id = st.text_input("Введите ID трека")
        if song_id:
            resp = requests.get(f"{FASTAPI_URL}/get_song/{song_id}")
            if resp.status_code == 200:
                song = resp.json()
                if song:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**{song[1]}** - {song[2] or 'Неизвестно'}")
                        st.caption(f"ID: {song[0]}")
                    with col2:
                        if st.button("Добавить рецензию", key=f"add_id_{song[0]}"):
                            st.session_state.review_song = song[0]
                            st.rerun()
                else:
                    st.error("Трек не найден")
    
    else:
        author_query = st.text_input("Введите исполнителя")
        if author_query:
            resp = requests.get(f"{FASTAPI_URL}/find_song", params={"query": author_query, "type_search": "author"})
            if resp.status_code == 200:
                songs = resp.json()
                if songs:
                    for song in songs:
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"**{song[1]}** - {song[2] or 'Неизвестно'}")
                            st.caption(f"ID: {song[0]}")
                        with col2:
                            if st.button("Добавить рецензию", key=f"add_author_{song[0]}"):
                                st.session_state.review_song = song[0]
                                st.rerun()
                else:
                    st.info("Треки не найдены")

elif action == "Добавить рецензию":
    song_id = st.text_input("ID трека", 
                           value=st.session_state.get('review_song', ''),
                           key="review_song_id")
    
    # Показываем имя пользователя из Telegram
    st.info(f"Рецензия будет добавлена от имени: **{st.session_state.user['username']}**")
    
    review = st.text_area("Ваша рецензия", key="review_text")
    
    # Кнопка для поиска по ID
    if st.button("Найти по ID", key="search_by_id"):
        if song_id:
            resp = requests.get(f"{FASTAPI_URL}/get_song/{song_id}")
            if resp.status_code == 200:
                song = resp.json()
                if song:
                    st.success(f"Найден: **{song[1]}** - {song[2] or 'Неизвестно'}")
    
    if st.button("Отправить", key="submit_review"):
        if not song_id:
            st.error("Введите ID трека")
        elif not review:
            st.error("Введите текст рецензии")
        else:
            # Проверяем на нецензурную лексику
            if check_profanity(review):
                st.error("❌ Рецензия содержит нецензурную лексику. Пожалуйста, измените текст.")
            else:
                # Отправляем отзыв С user_tg_id
                resp = requests.post(
                    f"{FASTAPI_URL}/create_web_review", 
                    json={
                        "song_id": song_id,
                        "comment": review,
                        "user_tg_id": st.session_state.user["id"]  # Telegram ID из сессии!
                    }
                )
                
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("success"):
                        st.success("✅ Рецензия добавлена под вашим Telegram аккаунтом!")
                        st.info(f"Автор: {data.get('user_name', st.session_state.user['username'])}")
                        if 'review_song' in st.session_state:
                            del st.session_state.review_song
                    else:
                        st.error(f"❌ Ошибка: {data.get('error', 'Неизвестная ошибка')}")
                elif resp.status_code == 400:
                    st.error(f"❌ {resp.json().get('detail', 'Ошибка при добавлении')}")
                else:
                    st.error(f"❌ Ошибка сервера: {resp.status_code}")

elif action == "Посмотреть рецензии":
    song_id = st.text_input("Введите ID трека")
    
    if song_id:
        resp = requests.get(f"{FASTAPI_URL}/get_song/{song_id}")
        if resp.status_code == 200:
            song = resp.json()
            if song:
                st.subheader(f"{song[1]} - {song[2] or 'Неизвестно'}")
                
                # Получаем рецензии
                reviews_resp = requests.get(f"{FASTAPI_URL}/get_song_review/{song_id}")
                if reviews_resp.status_code == 200:
                    reviews = reviews_resp.json()
                    if reviews:
                        st.write("---")
                        for review in reviews:
                            if len(review) >= 3:
                                author, text = review[1], review[2]
                                # Подсвечиваем рецензии текущего пользователя
                                if author == st.session_state.user['username']:
                                    st.markdown(f"**👤 Вы:** {text}")
                                else:
                                    st.markdown(f"**{author}:** {text}")
                                st.write("---")
                    else:
                        st.info("Рецензий пока нет")
                else:
                    st.error("Ошибка при получении рецензий")
        else:
            st.error("Трек не найден")

elif action == "Добавить новый трек":
    st.subheader("Добавить новый трек")
    
    song_name = st.text_input("Название трека", key="new_song_name")
    song_author = st.text_input("Исполнитель", key="new_song_author", 
                               value="нет автора")
    
    if st.button("Добавить трек", key="add_song_button"):
        if not song_name:
            st.error("Введите название трека")
        else:
            # Отправляем запрос на создание песни
            resp = requests.post(
            f"{FASTAPI_URL}/create_web_song", 
            json={  
            "name_song": song_name,  
            "author": song_author if song_author != "нет автора" else None
            }
        )
            
            if resp.status_code == 200:
                result = resp.json()
                st.success("✅ Трек успешно добавлен!")
                st.info(f"Название: **{song_name}**")
                st.info(f"Исполнитель: **{song_author}**")
            else:
                st.error(f"❌ Ошибка при добавлении: {resp.status_code}")