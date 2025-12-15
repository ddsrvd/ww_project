import streamlit as st
import requests

FASTAPI_URL = "http://localhost:8000"

st.set_page_config(page_title="СЫН РЗТ", layout="centered")
st.title("Рецензии на музыку")

# Главная страница
st.header("Welcome")
action = st.selectbox("What would you like to do?", 
                     ["Search songs", "Add review", "View song reviews", "Add new song"])

if action == "Search songs":
    # Изменяем поиск по ID на выбор типа поиска
    search_type = st.radio("Search by:", ["Name", "ID", "Author"], horizontal=True, key="search_type")
    
    if search_type == "Name":
        query = st.text_input("Search song by name")
        if query:
            resp = requests.get(f"{FASTAPI_URL}/search", params={"q": query})
            if resp.status_code == 200:
                songs = resp.json()
                if songs:
                    for song in songs:
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"**{song['name_song']}** - {song.get('author', 'Unknown')}")
                            st.caption(f"ID: {song['song_id']}")
                        with col2:
                            if st.button("Add review", key=f"add_{song['song_id']}"):
                                st.session_state.review_song = song['song_id']
                                st.rerun()
                else:
                    st.info("No songs found")
    
    elif search_type == "ID":  # Поиск по ID
        song_id = st.text_input("Search song by ID")
        if song_id:
            resp = requests.get(f"{FASTAPI_URL}/songs/{song_id}")
            if resp.status_code == 200:
                song = resp.json()
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{song['name_song']}** - {song.get('author', 'Unknown')}")
                    st.caption(f"ID: {song['song_id']}")
                with col2:
                    if st.button("Add review", key=f"add_id_{song['song_id']}"):
                        st.session_state.review_song = song['song_id']
                        st.rerun()
            else:
                st.error("Song not found")
    
    else:  
        author_query = st.text_input("Search songs by author")
        if author_query:
            resp = requests.get(f"{FASTAPI_URL}/search", params={"q": author_query, "type_search": "author"})
            if resp.status_code == 200:
                songs = resp.json()
                if songs:
                    for song in songs:
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"**{song['name_song']}** - {song.get('author', 'Unknown')}")
                            st.caption(f"ID: {song['song_id']}")
                        with col2:
                            if st.button("Add review", key=f"add_author_{song['song_id']}"):
                                st.session_state.review_song = song['song_id']
                                st.rerun()
                else:
                    st.info("No songs found by this author")

elif action == "Add review":
    song_id = st.text_input("Song ID", 
                           value=st.session_state.get('review_song', ''),
                           key="review_song_id")
    author_name = st.text_input("Your name", 
                               value=st.session_state.get('reviewer_name', ''),
                               key="author_name",
                               placeholder="Enter your name")
    review = st.text_area("Your review", key="review_text")
    
    # Добавляем кнопку для поиска по ID
    if st.button("Search by ID", key="search_by_id"):
        if song_id:
            resp = requests.get(f"{FASTAPI_URL}/songs/{song_id}")
            if resp.status_code == 200:
                song = resp.json()
                st.info(f"Found: {song['name_song']} by {song.get('author', 'Unknown')}")
    
    if st.button("Submit", key="submit_review"):
        if not song_id:
            st.error("Please enter Song ID")
        elif not author_name:
            st.error("Please enter your name")
        elif not review:
            st.error("Please enter your review")
        else:
            # Сохраняем имя пользователя
            st.session_state.reviewer_name = author_name
            
            # Отправляем отзыв
            resp = requests.post(
                f"{FASTAPI_URL}/songs/{song_id}/reviews", 
                params={
                    "review": review, 
                    "author_name": author_name
                }
            )
            if resp.status_code == 200:
                st.success("Review added!")
                if 'review_song' in st.session_state:
                    del st.session_state.review_song
            else:
                st.error(f"Failed to add review. Status: {resp.status_code}")

elif action == "View song reviews":
    song_id = st.text_input("Enter song ID")
    
    if song_id:
        resp = requests.get(f"{FASTAPI_URL}/songs/{song_id}")
        if resp.status_code == 200:
            song = resp.json()
            st.subheader(f"{song['name_song']} by {song.get('author', 'Unknown')}")
            
            # Отображаем отзывы
            reviews = song.get('review', [])
            if reviews:
                st.write("---")
                for review in reviews:
                    if isinstance(review, str):
                        if ": " in review:
                            parts = review.split(": ", 1)
                            if len(parts) == 2:
                                author, text = parts
                                st.markdown(f"**{author}**: {text}")
                            else:
                                st.markdown(f"**Anonymous**: {review}")
                        else:
                            st.markdown(f"**Anonymous**: {review}")
                    else:
                        st.markdown(f"**Review**: {review}")
                    st.write("---")
            else:
                st.info("No reviews yet")
        elif resp.status_code == 404:
            st.error("Song not found")

elif action == "Add new song":
    st.subheader("Add New Song")
    
    song_name = st.text_input("Song Name", key="new_song_name")
    song_author = st.text_input("Artist/Author", key="new_song_author", 
                               value="нет автора")
    
    if st.button("Add Song", key="add_song_button"):
        if not song_name:
            st.error("Please enter song name")
        else:
            # Отправляем запрос на создание песни
            resp = requests.post(
                f"{FASTAPI_URL}/songs", 
                params={
                    "name": song_name,
                    "author": song_author
                }
            )
            
            if resp.status_code == 200:
                result = resp.json()
                st.success("Song added successfully!")
                st.info(f"Song Name: **{song_name}**")
                st.info(f"Artist: **{song_author}**")
                
                # Показываем ID из response если есть
                if 'song_id' in result:
                    st.info(f"Song ID: **{result['song_id']}**")
                else:
                    # Или показываем сообщение из response
                    st.info(result.get('message', 'Song created'))
                
                # Кнопка для добавления рецензии
                if st.button("Add review for this song", key="add_review_for_new"):
                    # Сохраняем имя песни для поиска
                    st.session_state.search_song_name = song_name
                    st.rerun()
            else:
                try:
                    error_detail = resp.json()
                    st.error(f"Error: {error_detail.get('detail', 'Unknown error')}")
                except:
                    st.error(f"Failed to add song. Status: {resp.status_code}")