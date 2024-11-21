

import os
import requests
import json

class InvoiceCore():

    invoiceObj = {
        "invoiceDate": "1992-05-03",
        "dueDate": "1992-05-03",
        "senderName": "None",
        "senderAddress": "None",
        "senderContact": "None",
        "senderEmail": "None",
        "recipientName": "None",
        "recipientAddress": "None",
        "recipientContact": "None",
        "recipientEmail": "None",
        "items": [
            {
            "itemName": "None",
            "itemDescription": "None",
            "quantity": 0,
            "unitPrice": 0,
            "totalPrice": 0
            }
        ],
        "subTotal": 0,
        "taxRate": 0,
        "taxAmount": 0,
        "discount": 0,
        "totalAmount": 0,
        "paymentTerms": "None",
        "paymentMethod": "None",
        "bankDetails": "None",
        "paymentStatus": "None",
        "notes": "None",
        "termsAndConditions": "None",
        "currency": "None",
        "referenceNumber": "None"
    }

    loginObj = {
        "email": "email",
        "authCode": "authCode"
    }

    token = ""

    headerObj = {
        "Authorization" : ""
    }

    def __init__(self):
        
        super().__init__()

    
    def create_invoice(self):
        print("create_invoice Start")
        response = requests.post("http://34.105.111.197:8080/api/v1/invoices", headers=self.headerObj, json=self.invoiceObj)
        return json.loads(response.content)
        

    # def create_invoice(self, invoice):
    #     print("create_invoice Start")
    #     requests.post("http://34.105.111.197:8080/api/v1/invoices", headers=self.headerObj, json=self.invoiceObj)
    #     print("create_invoice Done")


    def login(self, email, authCode):
        self.loginObj["email"] = email
        self.loginObj["authCode"] = authCode
        response = requests.post("http://34.105.111.197:8080/api/v1/verify", json=self.loginObj)

        result = json.loads(response.content)

        if(result["code"] == "00"):
            self.token = result["data"]["accessToken"]
            self.headerObj["Authorization"] = "Bearer " + self.token
        
        return result
    