import json

import httpx
import streamlit as st

BASE_URL = "http://127.0.0.1:8001"

# Le funzioni che leggono (GET) vogliono la cache. Le funzioni che scrivono (POST) non la vogliono.


def delete_chat(selected_chat_id):
    headers = get_auth_headers()
    response = httpx.delete(f"{BASE_URL}/chats/{selected_chat_id}", headers=headers)
    if response.status_code == 200:
        del st.session_state.selected_chat_id
        st.cache_data.clear()  # la svuoto solo se creo una nuova chat perche si deve aggiornare list_all_chat
        st.rerun()
    else:
        st.error(
            f"Errore nella cancellazione: {response.status_code} - {response.text}"
        )


@st.cache_data
def list_all_chats():
    headers = get_auth_headers()
    response = httpx.get(f"{BASE_URL}/chats", headers=headers)
    list_of_sessions_data = response.json()
    chat_titles = []
    chat_ids = []
    for element in list_of_sessions_data:
        chat_titles.append(element.get("title"))
        chat_ids.append(element.get("id"))
    return chat_titles, chat_ids


@st.cache_data
def get_messages(selected_chat_id):
    headers = get_auth_headers()
    response = httpx.get(f"{BASE_URL}/chats/{selected_chat_id}", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return []


def create_chat():
    headers = get_auth_headers()

    response = httpx.post(f"{BASE_URL}/chats", headers=headers)
    if response.status_code == 200:
        new_item_chat = response.json()
        return new_item_chat
    else:
        st.error(f"Errore nella creazione: {response.status_code} - {response.text}")


def compute_cronologia(chat_titles, chat_ids):
    # SIDEBAR WITH CHATS
    st.sidebar.header("Cronologia Chat")
    for i in range(0, len(chat_titles)):
        if st.sidebar.button(chat_titles[i], key=chat_ids[i]):
            st.session_state.selected_chat_id = chat_ids[
                i
            ]  


def get_auth_headers():
    if "token" in st.session_state:
        return {"Authorization": f"Bearer {st.session_state['token']}"}
    return {}  # Restituisce header vuoto se non sei loggato


if "token" in st.session_state:
    headers = get_auth_headers()
    if "loaded_chat_id" not in st.session_state:
        st.session_state.loaded_chat_id = None

    st.sidebar.header("Create New chat")

    temp_chat_titles, temp_chat_ids = list_all_chats()
    compute_cronologia(temp_chat_titles, temp_chat_ids)
    if st.sidebar.button("New Chat"):
        new_item_chat = create_chat()
        st.session_state.selected_chat_id = new_item_chat.get("id")
        st.cache_data.clear()  # la svuoto solo se creo una nuova chat perche si deve aggiornare list_all_chat
        st.rerun()

    if "selected_chat_id" in st.session_state:
        # LOAD CHAT
        if (
            st.session_state.selected_chat_id != st.session_state.loaded_chat_id
        ):  # carico i messaggi solo se cambio chat
            st.title(f"{st.session_state.selected_chat_id}")
            st.session_state.messages = get_messages(st.session_state.selected_chat_id)
            st.session_state.loaded_chat_id = (
                st.session_state.selected_chat_id
            )  # aggiorno i due stati della chat

    else:
        st.session_state.messages = []

    # deve stare fuori da tutto cosi disegno sempre quello che c'è in messages!
    if "messages" in st.session_state and len(st.session_state.messages) > 0:
        for msg in st.session_state.messages:
            if msg.get("role") == "user":
                st.chat_message("user").markdown(msg.get("content"))
            elif msg.get("role") == "ai":
                st.chat_message("assistant").markdown(msg.get("content"))

    if "selected_chat_id" in st.session_state:
        # DELETE CHAT
        if st.button("Delete chat"):
            delete_chat(st.session_state.selected_chat_id)

        if prompt := st.chat_input("What is up?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            response = httpx.post(
                f"{BASE_URL}/chats/{st.session_state.selected_chat_id}",
                json={"input_data": prompt},
                headers=headers,
            )
            if response.status_code == 200:
                respose_text = response.json()
                st.session_state.messages.append(
                    {"role": "ai", "content": respose_text["content"]}
                )
                st.session_state.loaded_chat_id = None
                st.cache_data.clear()
                st.rerun()

        if st.button("Random Stream"):
            with httpx.stream("GET", f"{BASE_URL}/stream", headers=headers) as response:
                response.raise_for_status()  # non ritorna un codice ma è un tracker per lo status e basta
                st.write_stream(response.iter_text())

    if st.button("Logout"):
        del st.session_state.token
        st.rerun()
else:
    st.header("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Log in"):
        data = {"username": username, "password": password}

        response = httpx.post(f"{BASE_URL}/token", data=data)
        if response.status_code == 200:
            response = response.json()
            st.session_state.token = response.get("token")
            st.rerun()
        else:
            st.error(
                f"Errore nella creazione: {response.status_code} - {response.text}"
            )
