from openai import OpenAI
from dotenv import load_dotenv
import os
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

        assistant = self.client.beta.assistants.create(
            name="Financial Analyst Assistant",
            instructions="You are an expert financial analyst. Use you knowledge base to answer questions about audited financial statements.",
            model="gpt-4o",
            tools=[{"type": "file_search"}],
        )

    def extractSB(self, filePath):
        text = ''
        if os.path.splitext(filePath)[-1] in ".pdf" :
            text = extract_text_from_pdf(filePath)
        if os.path.splitext(filePath)[-1] in ".png.jpg.jpeg" :
            text = extract_text_from_image(filePath)

        print("EXTRACT TEXT : " + text)
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
    print("START extract_text_from_image")
    # 이미지 파일에서 텍스트 추출
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text

def extract_seller_and_buyer(openai, text):
    print("START extract_seller_and_buyer")
    # GPT 모델을 사용하여 판매자와 구매자 정보 추출
    prompt = f"Extract the seller and buyer information from the following invoice text:\n\n{text}\n\n"

    response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                        ],
                    }
                ],
            )

    # response = openai.chat.completions.create(
    #     engine="gpt-3.5-turbo",
    #     prompt=prompt,
    #     max_tokens=150,
    #     temperature=0.2,
    #     n=1,
    #     stop=["Buyer:"]
    # )
    
    # seller_info = response.choices[0].text.strip()
    
    # prompt_buyer = f"{seller_info}\n\nBuyer:"
    # response_buyer = openai.chat.completions.create(
    #     engine="gpt-3.5-turbo",
    #     prompt=prompt_buyer,
    #     max_tokens=150,
    #     temperature=0.2,
    #     n=1,
    #     stop=["\n"]
    # )
    
    # buyer_info = response_buyer.choices[0].text.strip()
    
    return response.choices[0].message.content
