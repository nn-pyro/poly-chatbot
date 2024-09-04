import streamlit as st
from utils.chatbot import get_response, get_recommend_questions

st.set_page_config(page_title="PĐT Fpoly HCM")

def main():

    st.markdown('<h1 style="font-size: 25px;">Phòng Đào Tạo FPT Polytechnic Cơ Sở THCM</h1>', unsafe_allow_html=True)
    st.write("---")

    if "messages" not in st.session_state:
        
        
        sys_message = "Hãy đặt câu hỏi để tìm kiếm các thông tin\n"
        recommend_question = get_recommend_questions()
        recommend_response = ""
        
        for _, item in enumerate(recommend_question["output_text"]):
            recommend_response += item
        
        st.session_state.messages = [
            {"role": "assistant", "content": sys_message + "\n" + "Gợi ý câu hỏi:" + "\n" + recommend_response}
        ]
        

    for messages in st.session_state.messages:
        with st.chat_message(messages["role"]):
            st.write(messages["content"])

    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        
        if st.session_state.messages[-1]["role"] != "assistant":
            with st.chat_message("assistant"):
                with st.spinner("Đang tìm câu trả lời..."):
                    response = get_response(prompt)
                    placeholder = st.empty()
                    full_response = ''
                    for _, item in enumerate(response):
                        full_response += item
                    placeholder.markdown(full_response)

                if response is not None:
                    messages = {"role": "assistant", "content": full_response}
                    st.session_state.messages.append(messages)


if __name__ == "__main__":

    main()