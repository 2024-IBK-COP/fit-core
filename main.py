from typing import Union
from fastapi import FastAPI
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import datetime
import os
from emailCore import emailCore
from aiCore import aiCore
from invoiceCore import invoiceCore


load_dotenv()

user = os.getenv("EMAIL")
password = os.getenv("PASSWORD")
key = os.getenv("OPEN-AI_KEY")


app = FastAPI()


@app.get("/")
def read_root():
    return {"Main": "Page"}


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

@app.get("/email/check")
def email_check():
    
    eCore = emailCore.EmailCore()
    eCore.connectSession("imap.gmail.com", user, password)
    eCore.searchEmail()
    eCore.disconnectSession()

    return {"emailcheck": True}


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

@app.get("/test")
def test():
    print("START /test")
    iCore = invoiceCore.InvoiceCore()
    iCore.login("radiata03@gmail.com", 44121)
    iCore.create_invoice()

@app.get("/invoice/{invoice_id}")
def download(invoice_id: str):

    # 이부분은 Done 으로 수정해야함
    filename = os.getcwd() + "/attachments/Done" + invoice_id 

    return FileResponse(filename)

@app.get("/invoice/save")
def save_invoices():

    # 이부분은 Done 으로 수정해야함
    filePath_notYet = os.path.join(os.getcwd() ,"attachments","NotYet")
    filePath_done = os.path.join(os.getcwd() ,"attachments","Done")
    
    
    aCore = aiCore.AiCore(key)

    for fileNm in os.listdir(filePath_notYet):
        
        iCore = invoiceCore.InvoiceCore()
        iCore.login(fileNm.split("_")[1], 44121)

        result = aCore.extractSB(os.path.join(filePath_notYet,fileNm))
        iCore.invoiceObj["invoiceDate"] = datetime.datetime.strptime(fileNm.split("_")[0], "%y%m%d")
        iCore.invoiceObj["senderName"] = result["sellerName"]
        iCore.invoiceObj["recipientName"] = result["buyerName"]
        iCore.invoiceObj["currency"] = result["currency"]
        iCore.invoiceObj["totalAmount"] = result["totalPrice"]

        iCore.create_invoice()

    return "YAHO"

#TEMP
@app.get("/invoice/save/{fileNm}")
def save_invoices_fileNm(fileNm:str):

    # 이부분은 Done 으로 수정해야함
    filePath_notYet = os.path.join(os.getcwd() ,"attachments","NotYet")
    filePath_done = os.path.join(os.getcwd() ,"attachments","Done")

    
    print(fileNm)
    print(filePath_notYet)
    print(os.path.join(filePath_notYet,fileNm))
    
    aCore = aiCore.AiCore(key)

    iCore = invoiceCore.InvoiceCore()
    iCore.login(fileNm.split("_")[1], 44121)

    print("AI PROCESS START")
    result = aCore.extractSB(os.path.join(filePath_notYet,fileNm))
    print(f"AI RESULT\n{result}")
    print("AI PROCESS END")
    iCore.invoiceObj["invoiceDate"] = datetime.datetime.strptime(fileNm.split("_")[0], "%y%m%d").strftime("%Y-%m-%d")
    iCore.invoiceObj["senderName"] = result["sellerName"]
    iCore.invoiceObj["recipientName"] = result["buyerName"]
    iCore.invoiceObj["currency"] = result["currency"]
    iCore.invoiceObj["totalAmount"] = result["totalPrice"]

    return iCore.create_invoice()

@app.get("/invoice/{invoice_id}")
def download(invoice_id: str):

    # 이부분은 Done 으로 수정해야함
    filename = os.getcwd() + "/attachments/Done/" + invoice_id 

    return FileResponse(filename)