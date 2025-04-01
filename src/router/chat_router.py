from fastapi import FastAPI, File, UploadFile,WebSocket,WebSocketDisconnect,File,UploadFile
from langchain.chat_models import ChatOpenAI
from fastapi import APIRouter
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from fastapi.responses import StreamingResponse
import asyncio
import os
import re
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException,BackgroundTasks,Depends
from fastapi.responses import FileResponse
from urllib.parse import urlparse
import uuid
from loguru import logger
from model.request_model import EmailSchema
from service.chat_service import extract_text_from_txt,process_text_for_vectorstore,vector_store,openai_api_key,ConnectionState,get_agent_request,STATE_WAITING_FOR_EMAIL,STATE_WAITING_FOR_PHONE,STATE_COLLECTED,generator,text_to_speech,fake_db,send_email,send_mail_via_bot,save_email
from service.fallback import random_valid_name,get_random_fallback_response
from prompts.prompts import voice_prompt_template,prompt_template


chat_routers = APIRouter()

DATA_FOLDER = "crawl_data"
os.makedirs(DATA_FOLDER, exist_ok=True)
db_directory = "./chroma_db"
os.makedirs(db_directory, exist_ok=True)



@chat_routers.get("/crawlapi")
async def extract_and_save(url: str):
    try:
        # Fetch the webpage
        response = requests.get(url)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail=f"Failed to fetch the URL. Status code: {response.status_code}")

        # Parse the webpage
        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove script and style tags
        for script in soup(["script", "style", "noscript"]):
            script.decompose()

        # Extract visible text
        site_text = soup.get_text(separator="\n")

        # Extract <a> tags with href attributes
        links = []
        for a_tag in soup.find_all("a", href=True):
            link_text = a_tag.text.strip() or "No Text"
            links.append(f"Link Text: {link_text} | URL: {a_tag['href']}")

        # Extract metadata
        metadata = []
        for meta_tag in soup.find_all("meta"):
            if meta_tag.get("name"):
                meta_name = meta_tag.get("name")
                meta_content = meta_tag.get("content", "No Content")
                metadata.append(f"Meta Name: {meta_name} | Content: {meta_content}")
            elif meta_tag.get("property"):
                meta_property = meta_tag.get("property")
                meta_content = meta_tag.get("content", "No Content")
                metadata.append(f"Meta Property: {meta_property} | Content: {meta_content}")

        # Clean up and combine the data
        cleaned_text = "\n".join(line.strip() for line in site_text.splitlines() if line.strip())
        combined_data = f"### Text Content ###\n{cleaned_text}\n\n"

        combined_data += "### Links ###\n"
        combined_data += "\n".join(links) + "\n\n"

        combined_data += "### Metadata ###\n"
        combined_data += "\n".join(metadata)

        # Append the Source URL at the end of the content
        combined_data += f"\n\n### Source URL ###\n{url}"

        # Generate a unique filename based on the URL
        parsed_url = urlparse(url)
        base_name = parsed_url.netloc.replace(".", "_")  # Use the domain name as the base
        unique_id = uuid.uuid4().hex[:8]  # Generate a short random unique identifier
        file_name = f"{base_name}_{unique_id}.txt"
        file_path = os.path.join(DATA_FOLDER, file_name)

        # Save the combined data to a .txt file
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(combined_data)

        # Return the .txt file
        return FileResponse(path=file_path, filename=file_name, media_type="text/plain")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# FastAPI endpoint to upload text file
@chat_routers.post("/train/model")
async def upload_txt(file: UploadFile = File(...)):
    # Check file extension
    if not file.filename.endswith('.txt'):
        return {"error": "Only .txt files are supported."}
    
    # Check file size (example: limit to 10MB)
    file_size_limit = 10 * 1024 * 1024  # 10 MB
    file_size = len(await file.read())
    await file.seek(0)  # Reset file pointer
    if file_size > file_size_limit:
        return {"error": "File size exceeds the 10MB limit."}
    
    try:
        # Extract and process text
        text = extract_text_from_txt(file)
        documents = process_text_for_vectorstore(text)

        # Add documents to vector store
        vector_store.add_documents(documents)
        vector_store.persist()  # Persist changes to disk
        logger.info(f"Successfully processed and stored vectors for file: {file.filename}")
        return {"message": f"File '{file.filename}' processed and vectors stored in ChromaDB."}
    except ValueError as ve:
        return {"error": str(ve)}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"error": "An unexpected error occurred while processing the file."}
    
#saved conversation
# def save_query(query, file_path="chat_history.txt"):
#     """Save the user query to a text file."""
#     if not os.path.exists(file_path):
#         with open(file_path, "w", encoding="utf-8") as file:
#             file.write("Chat History\n\n")
#     with open(file_path, "a", encoding="utf-8") as file:
#         file.write(f"Query: {query}\n")


import aiofiles

# def save_query(query, file_path="chat_history.txt"):
#     """Asynchronously save the user query to a text file."""
#     try:
#         if not os.path.exists(file_path):
#             with aiofiles.open(file_path, "w", encoding="utf-8") as file:
#                 file.write("Chat History\n\n")
#         with aiofiles.open(file_path, "a", encoding="utf-8") as file:
#             file.write(f"Query: {query}\n")
#     except Exception as e:
#         print(f"Error saving query: {e}")  # Log the error



# def save_answer(answer, file_path="chat_history.txt"):
#     """Save the AI answer to a text file."""
#     with open(file_path, "a", encoding="utf-8") as file:
#         file.write(f"Answer: {answer}\n\n")

# stored_queries = [""]  # Initialize list with an empty string


# def fun(query):
#     stored_queries[0] += query + "\n"  # Append new query to the existing string with a newline
#     return stored_queries[0]  # Return the updated string

# async def main():
#     await save_query()  # Ensure `save_query` is awaited properly

# # 🔹 If inside a script (not in Jupyter Notebook or FastAPI), use this:
# if __name__ == "__main__":
#     asyncio.run(main())  # ✅ Works in standalone scripts

# async def save_query():
#     """Asynchronously save all stored queries to a text file."""
#     file_path = "chat_history.txt"
#     try:
#         async with aiofiles.open(file_path, "a", encoding="utf-8") as file:
#             await file.write(stored_queries[0])  # Save all queries from stored_queries
#         print("Queries saved successfully!")  # Print success message

#     except Exception as e:
#         print(f"Error saving query: {e}")  # Log any errors





async def log_chat_history(user_input, response):
    # Append the user input and response to chat_history.txt
    with open("chat_history.txt", "a") as f:
        f.write(f"User: {user_input}\nResponse: {response}\n\n")

@chat_routers.websocket("/ws/query")
async def websocket_query_rag(websocket: WebSocket):
    await websocket.accept()  # Accept the WebSocket connection
    connection_state = ConnectionState()
    user_name = random_valid_name()
    
    # Prepare the personalized prompt
    personalized_prompt = prompt_template.replace("{user_name}", user_name)
    prompt = PromptTemplate(
        template=personalized_prompt,
        input_variables=["context", "question"]
    )
    
    # Initialize the LLM and retriever once per connection
    llm = ChatOpenAI(model="gpt-4", openai_api_key=openai_api_key)
    retriever = vector_store.as_retriever()
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=False,
        chain_type_kwargs={"prompt": prompt}
    )
    
    try:
        while True:
            # Wait to receive a message from the client
            data = await websocket.receive_text()
            user_input = data.strip()
            # mail_response = await send_mail_via_bot(user_input)
            # if mail_response != "No mail-related query detected.":
            #     await websocket.send_json({"type": "response", "answer": mail_response})  # Send response
            #     continue
            save_emails=await save_email(user_input)
            if save_emails != "That doesn't seem to be a valid email address. Could you please provide a valid email?":
                await websocket.send_json({"type": "response", "answer": save_emails}) 
                continue
            
            # Handle exit commands
            if user_input.lower() in ["exit", "quit"]:
                await websocket.send_json({"type": "response", "answer": "Goodbye! Have a great day! 😊"})
                break
            
            # Check if the user is requesting an agent
            if get_agent_request(user_input):
                # Check if user information is already in the fake database
                if fake_db["email"] and fake_db["phone_number"]:
                    response = "Thank you! I already have your information. Our agent will contact you soon. Is there anything else you would like to know about?😊"
                elif not fake_db["email"]:
                    connection_state.state = STATE_WAITING_FOR_EMAIL
                    response = "I’d be happy to connect you with an agent! Could you please provide your email address first?"
                elif not fake_db["phone_number"]:
                    connection_state.state = STATE_WAITING_FOR_PHONE
                    response = "Thank you for sharing your email! Could you also provide your phone number so we can reach out to you quickly if needed?"
            elif connection_state.state == STATE_WAITING_FOR_EMAIL:
                # Validate and store the email
                email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", user_input)
                if email_match:
                    fake_db["email"] = email_match.group()
                    connection_state.state = STATE_WAITING_FOR_PHONE
                    response = f"Thank you for providing your email: {fake_db['email']}. Could you also provide your phone number?"
                else:
                    response = "That doesn't seem to be a valid email address. Could you please provide a valid email?"
            elif connection_state.state == STATE_WAITING_FOR_PHONE:
                # Validate and store the phone number
                phone_match = re.search(r"\+?\d{10,15}", user_input)
                if phone_match:
                    fake_db["phone_number"] = phone_match.group()
                    connection_state.state = STATE_COLLECTED
                    response = f"Thank you for providing your phone number: {fake_db['phone_number']}. Our agent will contact you as soon as possible.Let me know if you need help!😊"
                else:
                    response = "That doesn't seem to be a valid phone number. Could you please provide a valid phone number?😊"
            elif connection_state.state == STATE_COLLECTED:
                # If all information is already collected, handle repeated requests for agent assistance
                if get_agent_request(user_input):
                    response = "Thank you! I already have your information. Our agent will contact you soon. Is there anything else you would like to know about? 😊 👋 ."
                else:
                    # Handle general queries
                    try:
                        answer = qa_chain.run(user_input)
                        if not answer.strip() or "I'm sorry" in answer:
                            answer = get_random_fallback_response(user_name)
                        response = answer
                    except Exception as e:
                        response = f"An error occurred: {str(e)}"
            else:
                # Process general queries or reset the state
                try:
                    answer = qa_chain.run(user_input)
                    if not answer.strip() or "I'm sorry" in answer:
                        answer = get_random_fallback_response(user_name)
                    response = answer
                except Exception as e:
                    response = f"An error occurred: {str(e)}"
                    
            # await log_chat_history(user_input, response)
            # Send the response back to the client
            await websocket.send_json({"type": "response", "answer": response})
    
    except WebSocketDisconnect:
        print(f"WebSocket connection with {user_name} closed.")




# WebSocket route for SpeechTTS
@chat_routers.websocket("/SpeechTTS")
async def process_query(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            lecture = "This is the lecture content."

            # Generate response using generator
            captured_text = await generator(data, lecture)

            # Perform TTS conversion and streaming
            voice = "en-GB-SoniaNeural"
            await text_to_speech(captured_text, voice, websocket)

            # Notify client of end of stream
            await websocket.send_text("[END]")
    except WebSocketDisconnect:
        print("WebSocket connection closed")
    finally:
        await websocket.close()


@chat_routers.post("/query")
async def query_rag(query: str):
    try:
        # Generate a random user name and fallback response
        user_name = random_valid_name()
        fallback_responses = get_random_fallback_response(user_name)

        # Update the prompt dynamically with the username
        personalized_prompt = prompt_template.replace("{user_name}", user_name)
        prompt = PromptTemplate(
            template=personalized_prompt,
            input_variables=["context", "question"]
        )

        # Initialize LLM and retriever
        llm = ChatOpenAI(model="gpt-4", openai_api_key=openai_api_key)
        retriever = vector_store.as_retriever()
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            return_source_documents=False,
            chain_type_kwargs={"prompt": prompt}
        )

        async def event_stream():
            # Get the complete answer (blocking call)
            full_answer = qa_chain.run(query)

            # Split the answer into words
            words = full_answer.split()  # Splitting by whitespace to get words
            
            for word in words:
                yield f"data: {word.strip()}\n\n"  # Yield each word
                print(word.strip())  # Print each word to console
                await asyncio.sleep(0.1)  # Simulate delay for streaming effect

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    except Exception as e:
        # Handle errors and return an appropriate HTTP response
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")



@chat_routers.post("/send-email/")
async def send_email_endpoint(email_data: EmailSchema, background_tasks: BackgroundTasks):
    background_tasks.add_task(send_email, email_data.recipient, email_data.subject, email_data.body)
    return {"message": "Email is being sent please wait 3 to 5 second only!"}



