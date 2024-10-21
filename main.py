from typing import Union
from fastapi import FastAPI
from dotenv import load_dotenv
import os
from emailCore import emailCore



load_dotenv()

user = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

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
    eCore.download()
    eCore.disconnectSession()

    return {"Hello": "World"}
