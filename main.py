from typing import Union
from fastapi import FastAPI
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import datetime
import os
from emailCore import emailCore
from aiCore import aiCore
from invoiceCore import invoiceCore
import shutil

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

@app.get("/email/check")
def email_check():
    print('@app.get("/email/check") START')
    eCore = emailCore.EmailCore()
    print(f"eCore.connectSession('imap.gmail.com', {user}, {password}) START")
    eCore.connectSession("imap.gmail.com", user, password)
    print('eCore.searchEmail() START')
    eCore.searchEmail()
    print('eCore.disconnectSession() START')
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

    filename = os.getcwd() + "/attachments" + os.sep + filename 

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


@app.get("/invoice/all/save")
def save_invoices():
    print('Start /invoice/save')
    # 이부분은 Done 으로 수정해야함
    notYetDir = os.path.join(os.getcwd() ,"attachments","NotYet")
    doneDir = os.path.join(os.getcwd() ,"attachments","Done")
    failDir = os.path.join(os.getcwd() ,"attachments","Fail")
    
    aCore = aiCore.AiCore(key)

    for fileNm in os.listdir(notYetDir):
        try:
            print(f'{os.path.join(notYetDir,fileNm)} Start')
            iCore = invoiceCore.InvoiceCore()
            iCore.login(fileNm.split("_")[1], 44121)

            print("AI PROCESS START")
            result = aCore.extractSB(os.path.join(notYetDir,fileNm))
            print(f"AI RESULT\n{result}")
            print("AI PROCESS END")

            if  result["sellerName"] & result["buyerName"] & result["currency"] & result["totalPrice"] :
                iCore.invoiceObj["invoiceDate"] = datetime.datetime.strptime(fileNm.split("_")[0], "%y%m%d").strftime("%Y-%m-%d")
                iCore.invoiceObj["senderName"] = result["sellerName"]
                iCore.invoiceObj["recipientName"] = result["buyerName"]
                iCore.invoiceObj["currency"] = result["currency"]
                iCore.invoiceObj["totalAmount"] = result["totalPrice"]

                result = iCore.create_invoice()

                if(result["code"] == "00"):
                    shutil.move(os.path.join(notYetDir,fileNm), os.path.join(doneDir,result["data"] +"."+ fileNm.split(".")[-1]))
                else:
                    print("createInvoice Fail")
            else:
                shutil.move(os.path.join(notYetDir,fileNm), os.path.join(failDir,fileNm))
                print("invalid invoice")
        except Exception as e:
            print(f'error during invoice saving {e}')
            continue

    return "YAHO"

#TEMP
@app.get("/invoice/save/test/{fileNm}")
def save_invoices_fileNm(fileNm:str):

    # 이부분은 Done 으로 수정해야함
    notYetDir = os.path.join(os.getcwd() ,"attachments","NotYet")
    doneDir = os.path.join(os.getcwd() ,"attachments","Done")

    
    print(fileNm)
    print(notYetDir)
    print(os.path.join(notYetDir,fileNm))
    
    aCore = aiCore.AiCore(key)

    iCore = invoiceCore.InvoiceCore()
    iCore.login(fileNm.split("_")[1], 44121)

    print("AI PROCESS START")
    result = aCore.extractSB(os.path.join(notYetDir,fileNm))
    print(f"AI RESULT\n{result}")
    print("AI PROCESS END")
    iCore.invoiceObj["invoiceDate"] = datetime.datetime.strptime(fileNm.split("_")[0], "%y%m%d").strftime("%Y-%m-%d")
    iCore.invoiceObj["senderName"] = result["sellerName"]
    iCore.invoiceObj["recipientName"] = result["buyerName"]
    iCore.invoiceObj["currency"] = result["currency"]
    iCore.invoiceObj["totalAmount"] = result["totalPrice"]

    result = iCore.create_invoice()

    if(result["code"] == "00"):
        shutil.move(os.path.join(notYetDir,fileNm), os.path.join(doneDir,result["data"] +"."+ fileNm.split(".")[-1]))
    else:
        print("createInvoice Fail")

    return result

@app.get("/invoice/{invoice_id}")
def download(invoice_id: str):

    # 이부분은 Done 으로 수정해야함
    filename = os.path.join(os.getcwd() ,"attachments","Done", invoice_id )
    
    print(filename)

    return FileResponse(filename)