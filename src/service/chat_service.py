from fastapi import FastAPI, File, UploadFile,WebSocket,WebSocketDisconnect,File,UploadFile
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain.schema import Document
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from fuzzywuzzy import fuzz
from langchain.memory import ConversationBufferMemory
import os
import tempfile
from dotenv import load_dotenv
import re
from edge_tts import Communicate
from loguru import logger
from fastapi import FastAPI, HTTPException
import aiosmtplib
from email.mime.text import MIMEText
from prompts.prompts import voice_prompt_template
from service.fallback import random_valid_name_for_voice,get_random_fallback_response_for_voice
from typing import Optional
from starlette.websockets import WebSocketState


connection_state = {"state": None}
conversation_memory = ConversationBufferMemory()
fake_db = {"email": None, "phone_number": None}  # Simple fake database to store user information

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OpenAI API key not found. Please set it in your .env file.")

TARGET_PHRASES = [
    "i want to talk to an agent",
    "i need help",
    "connect me with an agent",
    "talk to an agent",
    "i want to buy this service",
    "i want to talk to your expert",
    "i need agent"
]
SIMILARITY_THRESHOLD = 85 # Adjust as needed

SMTP_USERNAME = os.getenv('SMTP_USERNAMES')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORDS')
SMTP_HOST = "smtp.gmail.com"            
SMTP_PORT = 587  
# Define conversation states
STATE_INITIAL = "initial"
STATE_WAITING_FOR_EMAIL = "waiting_for_email"
STATE_WAITING_FOR_PHONE = "waiting_for_phone"
STATE_COLLECTED = "collected"
# ChromaDB Setup
embedding_model = OpenAIEmbeddings(openai_api_key=openai_api_key)
db_directory = "./chroma_db"
vector_store = Chroma(persist_directory=db_directory, embedding_function=embedding_model)

class ConnectionState:
    """
    Class to manage the state of a single WebSocket connection.
    """
    def __init__(self):
        self.state = STATE_INITIAL
        self.email: Optional[str] = None
        self.phone_number: Optional[str] = None

def get_agent_request(user_input: str) -> bool:
    """
    Determines if the user wants to talk to an agent based on similarity.
    
    Args:
        user_input (str): The input string from the user.
    
    Returns:
        bool: True if the user wants to talk to an agent, False otherwise.
    """
    user_input_lower = user_input.lower()
    for phrase in TARGET_PHRASES:
        similarity = fuzz.token_set_ratio(user_input_lower, phrase.lower())
        if similarity >= SIMILARITY_THRESHOLD:
            return True
    return False


# Function to process text for vector store
def process_text_for_vectorstore(text: str):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
    chunks = text_splitter.split_text(text)
    documents = [Document(page_content=chunk) for chunk in chunks]
    return documents

# Function to extract text from a text file
def extract_text_from_txt(file: UploadFile):
    try:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(file.file.read())
            temp_file.close()
            with open(temp_file.name, 'r', encoding='utf-8') as txt_file:
                text = txt_file.read()
        os.remove(temp_file.name)
        return text
    except Exception as e:
        logger.error(f"Error reading text file: {e}")
        raise ValueError("Failed to extract text from file.")


# Generator function for handling the query and generating an answer

def preprocess_query(query: str) -> str:
    """
    Replace spoken variations of '@' (like 'at the rate', 'at rate', 'at') with '@'
    """
    # Replace "at the rate", "at rate" with "@", ensuring no extra spaces
    query = re.sub(r"\s*\bat\s+the\s+rate\b\s*", "@", query, flags=re.IGNORECASE)
    query = re.sub(r"\s*\bat\s+rate\b\s*", "@", query, flags=re.IGNORECASE)
    query = re.sub(r"\s*\bat\b(?=\s+\w)\s*", "@", query, flags=re.IGNORECASE)  # Only replace "at" when followed by a word

    return query.strip()

async def send_mail_via_bot(query):
    if re.search(r'(send the mail|send mail|plz drop mail|can you send a mail on given email address|send the mail please|send the mail plz|plz send a mail|please drop a mail|plz send an email|send an email|drop an email|can you email me|please email me|shoot an email|mail me|could you send an email|would you mind sending an email|fire off an email|dispatch an email|forward an email|email this|email that|please send the mail|can you please send the mail|could you please send the email|would you please send the mail|send the email now|send over an email|do send an email|email it to me|drop me an email|send across the email|would you mind emailing me|please send me an email|can you send me an email|shoot me an email|ping me an email|forward me the email|kindly send the email|may I request you to send an email|please ensure the mail is sent|could you send over the email)', 
                query, re.IGNORECASE):
        
        recipient = fake_db.get('email')
        if recipient and isinstance(recipient, str) and "@" in recipient:
            subject = "Currently you are chatting with bot"
            body = "Please share your review"
            return await send_email(recipient, subject, body)
        else:
            return "Please provide your email address before sending a mail."
    
    return "No mail-related query detected."




async def send_mail_via_voice_bot(query):
    recipient = fake_db.get('email')
    if recipient and isinstance(recipient, str) and "@" in recipient:
        subject = "Currently you are chatting with bot"
        body = "Please share your review"
        return await send_email(recipient, subject, body)


async def save_email(query):
    if not query:
        return "Please provide your email address before sending a mail."
    
    mail_process=preprocess_query(query)
    email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", mail_process)
    if email_match:
        fake_db["email"] = email_match.group()
        return await send_mail_via_voice_bot(query)
    else:
        return "That doesn't seem to be a valid email address. Could you please provide a valid email?"

# 📩 Async function to send an email
async def send_email(recipient: str, subject: str, body: str):
    message = MIMEText(body, "html")  # Use "html" for HTML content, "plain" for plain text
    message["From"] = SMTP_USERNAME
    message["To"] = recipient
    message["Subject"] = subject

    try:
        await aiosmtplib.send(
            message,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            username=SMTP_USERNAME,
            password=SMTP_PASSWORD,
            start_tls=True,  # Use True for TLS (587), False for SSL (465)
        )
        return "Email sent successfully please check your email.Is there anything else you would like to know?!"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending email: {str(e)}")

# Test case

async def generator(query: str, lecture: str) -> str:
    try:
        mail_response = await send_mail_via_bot(query)
        print(mail_response)
        if mail_response != "No mail-related query detected.":
            return mail_response  # Send email and exit early if mail was sent
        
        save_emails=await save_email(query)
        if save_emails != "That doesn't seem to be a valid email address. Could you please provide a valid email?":
            return save_emails

        user_name = random_valid_name_for_voice()
        fallback_response = get_random_fallback_response_for_voice(user_name)

        # Prepare the personalized prompt
        personalized_prompt = voice_prompt_template.replace("{user_name}", user_name)
        prompt = PromptTemplate(
            template=personalized_prompt,
            input_variables=["context", "question"]
        )

        # Initialize the LLM and retriever
        llm = ChatOpenAI(model="gpt-4", openai_api_key=openai_api_key)
        retriever = vector_store.as_retriever() if vector_store else None
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            return_source_documents=False,
            chain_type_kwargs={"prompt": prompt}
        )

        queryy = preprocess_query(query)

        # Handle agent request
        if get_agent_request(queryy):
            if fake_db.get("email") and fake_db.get("phone_number"):
                return "Thank you! I already have your information. Our agent will contact you soon. Is there anything else you would like to know?"
            elif not fake_db.get("email"):
                connection_state["state"] = STATE_WAITING_FOR_EMAIL
                return "I’d be happy to connect you with an agent! Could you please provide your email address first?"
            elif not fake_db.get("phone_number"):
                connection_state["state"] = STATE_WAITING_FOR_PHONE
                return "Thank you for sharing your email! Could you also provide your phone number so we can reach out to you quickly if needed?"

        # Handle email/phone collection
        elif connection_state["state"] == STATE_WAITING_FOR_EMAIL:
            email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", queryy)
            if email_match:
                fake_db["email"] = email_match.group()
                connection_state["state"] = STATE_WAITING_FOR_PHONE
                return f"Thank you for providing your email: Could you also provide your phone number please?"
            else:
                return "That doesn't seem to be a valid email address. Could you please provide a valid email?"
        
        elif connection_state["state"] == STATE_WAITING_FOR_PHONE:
            phone_match = re.search(r"\+?\d[\d\s]{9,14}", query)
            if phone_match:
                fake_db["phone_number"] = phone_match.group()
                connection_state["state"] = STATE_COLLECTED
                return f"Thank you for providing your phone number: Our agent will contact you as soon as possible. Let me know if you need help!"
            else:
                return "That doesn't seem to be a valid phone number. Could you please provide a valid phone number?"
        
        elif connection_state["state"] == STATE_COLLECTED:
            connection_state["state"] = None  # Reset state
            if get_agent_request(query):
                return "Thank you! I already have your information. Our agent will contact you soon. Is there anything else you would like to know?"

        # Process user question
        try:
            answer = qa_chain.run(query) if qa_chain else "QA system not initialized."
            captured_text = answer.strip() if answer and answer.strip() else fallback_response
            return captured_text
        except Exception as e:
            return f"An error occurred: {str(e)}"
    
    except Exception as e:
        return f"Unexpected error: {str(e)}"



async def text_to_speech(text: str, voice: str, websocket: WebSocket):
    """Convert text to speech and stream it to the WebSocket client."""
    # print(f"Debug: text before TTS = {repr(text)}")  # Debugging step

    if not isinstance(text, str):
        text = str(text) if text is not None else "Sorry, I didn't understand that."

    communicate = Communicate(text, voice)
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            await websocket.send_bytes(chunk["data"])
