from typing import Union
from fastapi import FastAPI
from dotenv import load_dotenv
import os
from emailCore import emailCore
from aiCore import aiCore



load_dotenv()

user = os.getenv("EMAIL")
password = os.getenv("PASSWORD")
key = os.getenv("OPEN-AI_KEY")


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.get("/email/test")
def email_test():
    
    eCore = emailCore.EmailCore()
    eCore.connectSession("imap.gmail.com", user, password)
    eCore.searchEmail()
    eCore.disconnectSession()

    return {"Hello": "World"}


@app.get("/ai/question")
def ai_question(q: Union[str, None] = None):
    
    aCore = aiCore.AiCore(key)
    # aCore.makeQ(q)[0].message.content


    return {
        "q" : q,
        "a": aCore.makeQ(q)
        }

@app.get("/ai/filename")
def ai_question(filename: Union[str, None] = None):
    
    print("START /ai/question/filename")

    filename = os.getcwd() + "/attachments/" + filename 

    print(filename)

    aCore = aiCore.AiCore(key)
    # aCore.makeQ(q)[0].message.content


    return aCore.extractSB(filename)