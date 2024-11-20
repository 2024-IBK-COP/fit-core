from openai import OpenAI
from dotenv import load_dotenv
import os, platform
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import io



class AiCore():
    def __init__(self, key):
        self.client = OpenAI(
            # This is the default and can be omitted
            api_key=key,
        )        

        # assistant = self.client.beta.assistants.create(
        #     name="Financial Analyst Assistant",
        #     instructions="You are an expert financial analyst. Use you knowledge base to answer questions about audited financial statements.",
        #     model="gpt-4o",
        #     tools=[{"type": "file_search"}],
        # )

    def extractSB(self, filePath):
        text = ''
        if os.path.splitext(filePath)[-1] in ".pdf" :
            text = extract_text_from_pdf(filePath)
        if os.path.splitext(filePath)[-1] in ".png.jpg.jpeg" :
            text = extract_text_from_image(filePath)

        print("EXTRACT TEXT : \n" + text)
        # seller, buyer = extract_seller_and_buyer(self.client, text)

        # return {
        #     "seller" : seller,
        #     "buyer": buyer
        # }

        return extract_seller_and_buyer(self.client, text)


        # response = self.client.chat.completions.create(
        #     model="gpt-4o-mini",
        #     messages=[
        #         {
        #             "role": "user",
        #             "content": [
        #                 {"type": "text", "text": question},
        #                 {
        #                     "type": "image_url",
        #                     "image_url": {"url": f"{img_url}"},
        #                 },
        #             ],
        #         }
        #     ],
        # )

    def makeQ(self, question):

        chat_completion = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Let me know lama ai",
                }
            ],
            model="gpt-3.5-turbo",
        )

        print("CHOICE LEN : " + str(len(chat_completion.choices)))

        for choice in chat_completion.choices:
            print(choice.index)
            print(choice.message.content)

        print(chat_completion)
        return chat_completion.choices[0].message.content
    
def extract_text_from_pdf(pdf_path):
    print("START extract_text_from_pdf")
    # PDF 파일을 이미지로 변환
    images = convert_from_path(pdf_path)
    text = ""
    for image in images:
        # 이미지에서 텍스트 추출
        text += pytesseract.image_to_string(image)
    return text

def extract_text_from_image(image_path):

    if 'Window' in platform.system():
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    print("START extract_text_from_image")
    # 이미지 파일에서 텍스트 추출
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text

def extract_seller_and_buyer(openai, text):
    print("START extract_seller_and_buyer")
    # GPT 모델을 사용하여 판매자와 구매자 정보 추출
    # prompt = f"Extract the seller name and buyer name from the following invoice text:\n\n{text}\n\n If there is seller and buyer data in text, answer should be the following format:\n\nSeller Name:\nBuyer Name:\n\n"
    
    prompt = f"Is there seller name, buyer name, total price, currency from the following invoice text:\n\n{text}\n\n Say yes or no. And if answer is yes then Extract the seller name, buyer name, total price(only number without currency), currency . Answer should be the following format:\n\nSeller Name:\nBuyer Name:\n\nTotal Price:\n\nCurrency:\n\n"

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        max_tokens=150,
        temperature=0.2,
        n=1,
        stop=None
    )
    print("ANSWER S")
    print(response.choices[0].message.content)
    print("ANSWER E")
    result_text = response.choices[0].message.content.strip()

    # Assuming the response text will have something like "Seller: <seller_name>" and "Buyer: <buyer_name>"
    seller = None
    buyer = None
    currency = None
    totalPrice = None

    for line in result_text.split("\n"):
        if "Seller Name:" in line:
            seller = line.split("Seller Name:")[-1].strip()
        elif "Buyer Name:" in line:
            buyer = line.split("Buyer Name:")[-1].strip()
        elif "Currency:" in line:
            currency = line.split("Currency:")[-1].strip()
        elif "Total Price:" in line:
            totalPrice = line.split("Total Price:")[-1].strip()

    return {
        "sellerName": seller if seller else "",
        "buyerName": buyer if buyer else "",
        "currency" : currency if currency else "",
        "totalPrice" : totalPrice if totalPrice else ""
        }
