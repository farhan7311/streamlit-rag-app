import streamlit as st
import os
import requests
from google import genai
from google.genai import types

# Set your Gemini API key (move to st.secrets for production use)
os.environ["GOOGLE_API_KEY"] = "AIzaSyDozUi50Nlq2YHmruVo9nmp0pybzfKPNpI"

# Chat/file session state
if "history" not in st.session_state:
    st.session_state.history = []
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []
if "recent_uploads" not in st.session_state:
    st.session_state.recent_uploads = set()

client = genai.Client()
st.title("Gemini File Search with Streamlit")

# --- REST upload helper ---
def upload_to_gemini(file, store_name, api_key):
    file.seek(0)
    bytes_data = file.read()
    mime_type = "text/plain" if file.name.endswith(".txt") else "application/pdf"
    file_size = len(bytes_data)

    # Step 1: Start upload session
    start_url = f"https://generativelanguage.googleapis.com/upload/v1beta/{store_name}:uploadToFileSearchStore?key={api_key}"
    headers = {
        "X-Goog-Upload-Protocol": "resumable",
        "X-Goog-Upload-Command": "start",
        "X-Goog-Upload-Header-Content-Length": str(file_size),
        "X-Goog-Upload-Header-Content-Type": mime_type,
        "Content-Type": "application/json"
    }
    data = {"display_name": file.name}
    start_response = requests.post(start_url, headers=headers, json=data)
    upload_url = start_response.headers.get("X-Goog-Upload-URL")
    if not upload_url:
        return False, f"Step 1 failed: {start_response.text}"
    # Step 2: Upload file bytes
    upload_headers = {
        "Content-Length": str(file_size),
        "X-Goog-Upload-Offset": "0",
        "X-Goog-Upload-Command": "upload, finalize"
    }
    upload_response = requests.post(upload_url, headers=upload_headers, data=bytes_data)
    if upload_response.status_code != 200:
        return False, f"Step 2 failed: {upload_response.text}"
    return True, "Upload successful!"

# --- SIDEBAR: Store/upload controls ---
with st.sidebar:
    st.title("Settings & Controls")
    if st.button("Create File Search Store"):
        store = client.file_search_stores.create(config={"display_name": "File Search Store Streamlit"})
        st.session_state['store_name'] = store.name
        st.success(f"🌟 Store Created: {store.name}")

    uploaded_files = st.file_uploader(
        "Upload PDF/Text",
        type=['pdf', 'txt'],
        accept_multiple_files=True
    )

    if uploaded_files and 'store_name' in st.session_state:
        for file in uploaded_files:
            if file.name not in st.session_state.recent_uploads:
                with st.spinner(f"Uploading {file.name} to Gemini..."):
                    success, msg = upload_to_gemini(file, st.session_state['store_name'], os.environ["GOOGLE_API_KEY"])
                if success:
                    st.success(f"{file.name} uploaded to Gemini store! Wait a moment for indexing before querying.")
                    st.session_state.recent_uploads.add(file.name)
                else:
                    st.error(msg)
        st.session_state.uploaded_files = uploaded_files

    if 'store_name' in st.session_state:
        st.info(f"Active Store:\n{st.session_state['store_name']}")

# Uploaded file list for user info
if st.session_state.uploaded_files:
    st.markdown("#### Uploaded files:")
    for f in st.session_state.uploaded_files:
        st.write(f.name)
if 'store_name' in st.session_state:
    st.info(f"Gemini File Search Store in use: {st.session_state['store_name']}")

# --- GeminI query/response ---
if 'store_name' in st.session_state and st.session_state.uploaded_files:
    st.warning("After uploading, wait 20-60 seconds before querying to allow Gemini to index your files.")
    user_query = st.text_input("Ask a question about your files:")
    if user_query:
        try:
            prompt = (
                "Only answer using the content of the uploaded files, "
                "and mention the file name you used in the answer. "
                f"{user_query}"
            )
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[
                        types.Tool(
                            file_search=types.FileSearch(
                                file_search_store_names=[st.session_state['store_name']]
                            )
                        )
                    ]
                )
            )
            st.markdown("**Gemini Response:**")
            st.write(response.text)
            st.session_state.history.append({"question": user_query, "answer": response.text})
        except Exception as e:
            st.error(f"Query failed: {e}")

# --- Chat History ---
if st.session_state.history:
    st.markdown("### Previous Interactions")
    for pair in reversed(st.session_state.history):
        st.markdown(f"**Q:** {pair['question']}\n\n**A:** {pair['answer']}\n---")
