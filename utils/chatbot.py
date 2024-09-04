import os

from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferMemory
from langchain.chains.question_answering import load_qa_chain
from langchain_core.prompts import PromptTemplate
from database.db_connection import get_vector_db
from langchain_together import ChatTogether

load_dotenv()
vector_db = get_vector_db()

chatbot = ChatTogether(
    
    api_key = os.getenv("API_KEY"),
    model = "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
    temperature=0.6
    
)

def get_conversational_chain():
    
    template = """
    You are an intelligent assistant working in the Training Department at "Cao đẳng FPT Polytechnic." Your role is to interact with students and provide answers based on the information provided. The provided content consists of institutional documents which might not offer direct answers to every question but include relevant information.
    Your goal is to use this information to craft responses that feel like a natural conversation. Even if the question is brief or challenging, strive to give thoughtful and engaging answers as if you were conversing with the student directly. Avoid responses that sound formal or dry; instead, aim for a friendly and conversational tone. 
    If the exact answer isn't clear, offer the most relevant response or a reasonable explanation based on the content you have. If the information provided is entirely unrelated, reply with: "Hiện tại chưa có thông tin trả lời cho câu hỏi này."
    You are only permitted to use the provided content for reasoning and answering. External sources are not allowed. Ensure your responses are clear, articulate, and maintain a respectful tone towards students. 
    **Hint:** Think about how the information in the document might relate to the question. Try to apply this knowledge to real-world problems, just as you would solve problems in everyday life. This will help you come up with more coherent and meaningful answers.
    Please provide answers in Vietnamese.

    Conversation History:\n{chat_history}\n
    Provided Content:\n{context}\n
    Question:\n{question}\n

    Answer:

    """
        
    prompt = PromptTemplate(
        
        template = template,
        input_variables = ["chat_history", "context", "question"]
        )


    qa_chain = RetrievalQA.from_chain_type(
        
        llm=chatbot,
        chain_type='stuff',
        retriever=vector_db.as_retriever(search_type="mmr", search_kwargs={'k': 10, 'fetch_k': 50}),
        verbose=True,
        chain_type_kwargs={
            "verbose": True,
            "prompt": prompt,
            "memory": ConversationBufferMemory(
                memory_key="chat_history",
                input_key="question"),
        }
        
    )

    return qa_chain


def get_recommend_questions():
    
    template = """
    You are an intelligent assistant currently serving as a staff member in the Training Department at "Cao đẳng FPT Polytechnic". Based on the information provided, generate exactly 5 recommended questions that students might ask. Provide only the questions without any additional text, introductions, or explanations. These questions should be related to the provided content and should be in Vietnamese.

    Provided Content:\n{context}\n

    1.
    2.
    3.
    4.
    5.
    """
    
    prompt = PromptTemplate(
        template=template,
        input_variables=["context"]
    )
    
    retriever_db = vector_db.as_retriever()
    context = retriever_db.invoke("Cho tôi một số câu hỏi có liên quan")
    
    chain = load_qa_chain(
        llm = chatbot,
        chain_type = "stuff",
        prompt = prompt
    )
    
    response = chain({"input_documents": context}, return_only_outputs=True)
    
    return response


def get_response(user_question):
    
    qa_chain = get_conversational_chain()
    
    response = qa_chain.run({
        "query": user_question,
        "chat_history":""
    })

    return response