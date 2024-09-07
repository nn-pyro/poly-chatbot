import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
import tempfile
import os
import uuid
import yaml
import psycopg2

from yaml.loader import SafeLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader, Docx2txtLoader
from utils.custom_loader import CustomDocumentLoader
from database.db_connection import get_vector_db

st.set_page_config(page_title="PĐT Fpoly HCM")
vector_db = get_vector_db()

with open('./config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config["credentials"],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("USER"),
        password=os.getenv("PASSWORD"),
        host=os.getenv("HOST"),
        port=os.getenv("PORT")
    )
cur = conn.cursor()

upload_dir = 'uploads'
if not os.path.exists(upload_dir):
    os.makedirs(upload_dir)


def process_uploadfile(uploaded_file):
    documents = []

    for file in uploaded_file:
        
        file_extension = file.name.split('.')[-1]
        file_path = os.path.join(upload_dir, file.name)

        with open(file_path, 'wb') as f:
            f.write(file.getbuffer())

        if file_extension in ['doc', 'docx']:
            document = Docx2txtLoader(file_path).load()
        elif file_extension == 'pdf':
            document = PyPDFLoader(file_path).load()
        elif file_extension == "txt":
            document = CustomDocumentLoader(file_path).load()
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")

        documents.extend(document)

    return documents


def get_chunks(documents):

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=500)
    chunks = text_splitter.split_documents(documents)
    
    return chunks

# Hàm chính của ứng dụng
def main():
    vector_db = get_vector_db()
    uploaded_file = st.file_uploader("Chọn file để tải lên", accept_multiple_files=True)

    try:
        if st.button("Tải lên"):
            with st.spinner("Đang xử lý..."):
                docs = process_uploadfile(uploaded_file)
                chunks = get_chunks(docs)

                ids = [str(uuid.uuid4()) for _ in chunks]
                vector_db.add_documents(chunks, ids=ids)

                st.success("Tải lên thành công!")
    except Exception as e:
        st.error(f"Lỗi: {str(e)}")

    st.write("---")
    st.write("Danh sách các file đã tải lên")
    list_source = os.listdir('./uploads')
    path_name = pd.DataFrame({"Tên file - đường dẫn": list_source})
    st.table(path_name)

    st.write("---")
    selected_files = st.multiselect("Chọn các file để xóa", list_source)

    if st.button("Xóa tài liệu"):
        if selected_files:
            delete_documents(selected_files)
            
            st.success("Đã xóa các tài liệu được chọn.")
        else:
            st.warning("Vui lòng chọn ít nhất một tài liệu để xóa.")



def delete_documents(files_to_delete):

    for file in files_to_delete:
        try:
            conn.rollback()
            cur.execute("""
                SELECT id 
                FROM langchain_pg_embedding 
                WHERE cmetadata->>'source' = %s
            """, (f"uploads/{file}",))

            ids = [row[0] for row in cur.fetchall()]
            print(ids)

            vector_db.delete(ids)
            st.write(f"Đã xóa tài liệu: {file}")
            file_path = os.path.join(upload_dir, file)
            os.remove(file_path)

        except psycopg2.Error as e:
            conn.rollback()



if __name__ == "__main__":
    st.markdown('<h1 style="font-size: 25px;">Phòng Đào Tạo FPT Polytechnic Cơ Sở TP.HCM</h1>', unsafe_allow_html=True)
    st.write("---")

    name, authentication_status, username = authenticator.login('main')

    if st.session_state["authentication_status"]:
        authenticator.logout('Đăng xuất', 'main')
        st.write("---")
        main()
    elif st.session_state["authentication_status"] == False:
        st.error('Tài khoản hoặc mật khẩu không chính xác')
    elif st.session_state["authentication_status"] == None:
        st.warning('Vui lòng nhập tài khoản và mật khẩu để đăng nhập')
