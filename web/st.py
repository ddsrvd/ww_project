import streamlit as st
import requests

FASTAPI_URL = "http://localhost:8000"  # имя сервиса в docker-compose

st.set_page_config(page_title="Song Catalog", layout="wide")
st.title("Song Catalog")

menu = ["All Songs", "Search", "Add Song", "Add Review"]
choice = st.sidebar.selectbox("Navigation", menu)

if choice == "All Songs":
    st.header("All Songs")
    try:
        resp = requests.get(f"{FASTAPI_URL}/songs", timeout=3)
        if resp.status_code == 200:
            songs = resp.json()
            for s in songs:
                with st.container():
                    st.subheader(f"{s['name_song']} {f'— {s.get('author', 'Unknown')}' if s.get('author') else ''}")
                    st.caption(f"ID: {s['song_id']}")
                    reviews = s.get('review', [])
                    if reviews:
                        st.markdown("**Reviews:**")
                        for r in reviews:
                            st.markdown(f"- {r}")
                    else:
                        st.info("No reviews yet.")
                    st.divider()
        else:
            st.error("Failed to load songs")
    except Exception as e:
        st.error("Could not connect to backend")

elif choice == "Search":
    st.header("🔍 Search Songs")
    query = st.text_input("Enter song name")
    if query:
        try:
            resp = requests.get(f"{FASTAPI_URL}/search", params={"q": query}, timeout=3)
            if resp.status_code == 200:
                results = resp.json()
                if results:
                    for s in results:
                        st.write(f"**{s['name_song']}** (dist: {s['distance']}) — {s.get('author', 'Unknown')}")
                else:
                    st.info("No matches found")
            else:
                st.warning("Search failed")
        except Exception:
            st.error("Search service unavailable")

elif choice == "Add Song":
    st.header("➕ Add New Song")
    name = st.text_input("Song Name")
    author = st.text_input("Author (optional)")
    if st.button("Add Song") and name:
        try:
            resp = requests.post(f"{FASTAPI_URL}/songs", params={"name": name, "author": author}, timeout=3)
            if resp.status_code == 200:
                st.success("✅ Song added!")
            else:
                st.error("Failed to add song")
        except Exception:
            st.error("Backend unavailable")

elif choice == "Add Review":
    st.header("Add Review")
    song_id = st.text_input("Song ID")
    review = st.text_area("Your review")
    if st.button("Submit") and song_id and review:
        try:
            resp = requests.post(f"{FASTAPI_URL}/songs/{song_id}/reviews", params={"review": review}, timeout=3)
            if resp.status_code == 200:
                st.success("Review added!")
            elif resp.status_code == 404:
                st.error("Song not found")
            else:
                st.error("Failed to add review")
        except Exception:
            st.error("Backend unavailable")