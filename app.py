import os
import json
import re
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Load API key from .env
load_dotenv()

# Create model instance
model = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro",
    temperature=0.5,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

def get_model_result(query, doc_text=None):
    # Append document content to the query if provided
    context_text = f"\nUse the following document as reference:\n{doc_text}" if doc_text else ""
    
    final_prompt = f"""
    You are a legal assistant. Answer in JSON format with keys: query, response, citations, status.
    Question: {query}
    {context_text}
    """

    answer = model.invoke(final_prompt)

    # Extract JSON from output
    match = re.search(r"\{[\s\S]*\}", answer.content)
    if match:
        return json.loads(match.group(0))
    else:
        raise ValueError("No JSON found in model output")

# Streamlit UI
st.title("AI Legal Assistant")
query = st.text_input("Enter your legal query:")

uploaded_file = st.file_uploader("Upload a reference document", type=["txt", "pdf", "docx"])

doc_text = None
if uploaded_file is not None:
    # For .txt
    if uploaded_file.type == "text/plain":
        doc_text = uploaded_file.read().decode("utf-8")
    # For PDF
    elif uploaded_file.type == "application/pdf":
        import PyPDF2
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        doc_text = "\n".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())
    # For DOCX
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        import docx
        doc = docx.Document(uploaded_file)
        doc_text = "\n".join([para.text for para in doc.paragraphs])

if st.button("Ask AI"):
    result_json = get_model_result(query, doc_text)
    st.subheader("Response")
    st.write(result_json["response"])

    st.subheader("Citations")
    for citation in result_json["citations"]:
        st.markdown(f"> {citation['source_text']}")
