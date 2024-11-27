from email.header import decode_header
from email.utils import parseaddr
from email import utils
from datetime import datetime
import smtplib, imaplib, re, email
from email.mime.text import MIMEText
import os, json, shutil
import requests
from pdf2image import convert_from_path
import pandas as pd
import matplotlib.pyplot as plt
import pymupdf


class EmailCore():
    def __init__(self):
        self.detach_dir = os.getcwd()
        
        if 'attachments' not in os.listdir(self.detach_dir):
            os.mkdir('attachments')
        
        if 'NotYet' not in os.listdir(os.path.join(self.detach_dir , 'attachments')):
            os.mkdir(os.path.join(self.detach_dir , 'attachments','NotYet'))

        if 'Org' not in os.listdir(os.path.join(self.detach_dir , 'attachments')):
            os.mkdir(os.path.join(self.detach_dir , 'attachments','Org'))            

        if 'Done' not in os.listdir(os.path.join(self.detach_dir , 'attachments')):
            os.mkdir(os.path.join(self.detach_dir , 'attachments','Done'))

        if 'Fail' not in os.listdir(os.path.join(self.detach_dir , 'attachments')):
            os.mkdir(os.path.join(self.detach_dir , 'attachments','Fail'))

        super().__init__()

        self.imapSession = None
        self.smtpSession = None

        self.doneDir = os.path.join(self.detach_dir , 'attachments','Done')
        self.notYetDir = os.path.join(self.detach_dir , 'attachments','NotYet')
        self.orgDir = os.path.join(self.detach_dir , 'attachments','Org')

        self.ID = None


    def connectSession(self, URL, ID, PW):
        print(1)
        self.imapSession = imaplib.IMAP4_SSL(URL)
        print(2)
        self.smtpSession = smtplib.SMTP(URL)

        print(3)
        self.smtpSession.ehlo()
        print(4)
        self.smtpSession.starttls()
        
        print(5)
        self.ID = ID
        print(6)
        id = ID
        print(7)
        pw = PW
        
        print(8)
        self.imapSession.login(id, pw)
        print(9)
        self.smtpSession.login(id, pw)

    def disconnectSession(self):
        self.imapSession.close()
        self.imapSession.logout()
        self.smtpSession.quit()

    def sendEmail(self, receiver, subject, content):
        msg = MIMEText(content)
        msg['Subject'] = subject

        self.smtpSession.sendmail(self.ID, receiver, msg.as_string())
    
    def replyEmail(self, email_message, content):
        msg = MIMEText(content)

        msg["To"] = email_message["From"]
        msg["Subject"] = "Re: " + email_message["Subject"]
        msg["In_Reply-To"] = email_message["Message-Id"]
        msg["References"] = (email_message["References"] or "") + " " + email_message["Message-Id"]
        
        print("[S]Reply EMAIL TO : " + msg["To"])
        self.smtpSession.sendmail(self.ID, parseaddr(email_message.get('From'))[1], msg.as_string())
        print("[E]Reply EMAIL TO : " + msg["To"])


    def searchEmail(self):
        self.imapSession.select("INBOX")
        status, messages = self.imapSession.search(None, 'ALL')
        messages = messages[0].split()

        # 각 메일에 대하여 실행
        for n, message in enumerate(messages):
            
            res, msg = self.imapSession.fetch(message, "(RFC822)")

            raw_readable = msg[0][1]
            email_message = email.message_from_bytes(raw_readable)

            # 보낸사람
            senderEmail = parseaddr(email_message.get('From'))[1] # [0]=NickName
            # 메일제목
            # subject = email_message.get('Subject')

            subject, encoding = decode_header(email_message["Subject"])[0]
            
            if encoding :
                subject = subject.decode(encoding)

            print("SENDER  : " + senderEmail)
            print("SUBJECT : " + subject)

            #todo email 로 회원인지 아닌지 확인하는 과정 필요
            #senderEmail 이 고객인지 확인
            # if senderEmail != 'radiata03@naver.com':
            if not self.is_user(senderEmail):
                print(f'is not our user : {senderEmail}')
                self.replyEmail(email_message, 'YOU ARE NOT REGISTERED YET.\nPLEASE JOIN CCME SERVICE FIRST. http://www.ccme.co.kr/')
                
                self.imapSession.store(message, '+FLAGS', '\\Deleted')
                
                continue

            body = ''
            fileNm = ''
            
            # 메일 내용
            # if email_message.is_multipart():
            for part in email_message.walk():
                fileNm = part.get_filename()
                print(f'filename : {fileNm}')
                # if not bool(fileNm) : continue

                

                # ctype = part.get_content_type()
                
                # if ctype == 'text/plain':
                #     body += part.get_payload(decode=True).decode(part.get_content_charset)  # decode
                

                if bool(fileNm):
                    
                    if decode_header(fileNm)[0][1] is not None:
                        fileNm = decode_header(fileNm)[0][0].decode(decode_header(fileNm)[0][1])
                        print(f'decode filename : {fileNm}')

                    # if fileNm.split(".")[-1] in ['jpg', 'jpeg', 'png', 'pdf', 'xlsx'] :
                    if fileNm.split(".")[-1] in ['jpg', 'jpeg', 'png', 'pdf'] : # xlsx 뺌

                        dateStr = utils.parsedate_to_datetime(email_message.get('date')).strftime("%y%m%d")
                        newFileNm = dateStr + "_" + senderEmail + "_" + '.'.join(fileNm.split(".")[0:-1]) + "." + fileNm.split(".")[-1]

                        # orgDir 에 다운로드
                        self.download(self.orgDir, newFileNm, part)

                        # pdf
                        if fileNm.split(".")[-1] in ['pdf'] :
                            print("isPDF")
                            print(os.path.join(self.notYetDir, newFileNm))

                            self.download(self.notYetDir, newFileNm, part)

                            # self.pdf_to_png(
                            #     os.path.join(self.orgDir, newFileNm),
                            #     newFileNm
                            #     )

                            self.replyEmail(email_message, 'Invoice is saved successfully. Please check with https://www.ccme.co.kr')


                        #excel
                        # elif fileNm.split(".")[-1] in ['xlsx'] :
                        #     print("isXlsx")
                        #     # self.excel_sheet_to_png(
                        #     #     os.path.join(self.orgDir, newFileNm), 
                        #     #     os.path.join(self.notYetDir, '.'.join(newFileNm.split(".")[0:-1]) + ".png")
                        #     #     )
                        #     self.excel_to_pdf(
                        #         os.path.join(self.orgDir, newFileNm), 
                        #         os.path.join(self.notYetDir, '.'.join(newFileNm.split(".")[0:-1]) + ".pdf")
                        #     )

                        else :
                            self.download(self.notYetDir, newFileNm, part)
                            self.replyEmail(email_message, 'Invoice is saved successfully. Please check with https://www.ccme.co.kr')

                            # todo pdf 파일이 1장 이상인경우
                            # if len(images) == 1 :
                                # images[0].save(f'{self.notYetDir + os.sep + dateStr + "_" + senderEmail + "_" + '.'.join(fileNm.split(".")[0:-1]) + ".png"}','PNG')

                            # 현재는 1장 이상일 경우에는 파일을 삭제
                            # aos.remove(self.notYetDir + os.sep + newFileNm)
            # else:
            #     body = email_message.get_payload(decode=True).decode('utf-8')
            

            # 읽은 메일 삭제
            self.imapSession.store(message, '+FLAGS', '\\Deleted')
        
        # 읽은 메일 삭제
        self.imapSession.expunge()

                        

    def is_user(self, email):
        response = requests.get("http://34.105.111.197:8080/api/v1/members/status?email="+email)
        result = json.loads(response.content)
        
        return result["data"]["isMember"]

    def download(self, filePath, fileNm, part):
        if not os.path.isfile(os.path.join(filePath, fileNm)) :
            print("FILE DOWNLOAD START")
            fp = open(os.path.join(filePath, fileNm), 'wb')
            fp.write(part.get_payload(decode=True))
            fp.close()

    def excel_sheet_to_png(self, excel_file, output_png):
        # 첫 번째 시트 읽기
        df = pd.read_excel(excel_file, sheet_name=0)  # sheet_name=0은 첫 번째 시트를 읽습니다.
        
        # 데이터 크기에 따라 그림 크기 설정
        rows, cols = df.shape
        fig_width = max(10, cols * 2)  # 열 수에 따라 폭을 조정
        fig_height = max(5, rows * 0.4)  # 행 수에 따라 높이를 조정
        
        # Matplotlib 설정
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        ax.axis('tight')
        ax.axis('off')
        
        # 데이터프레임을 테이블로 변환
        table = ax.table(cellText=df.values, colLabels=df.columns, loc='center', cellLoc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.auto_set_column_width(col=list(range(len(df.columns))))  # 열 너비 자동 조정
        
        # PNG로 저장
        plt.savefig(output_png, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"PNG 파일이 저장되었습니다: {output_png}")


    # def excel_to_pdf(self, input_file, output_file):
    #     # Excel을 HTML로 변환
    #     temp_html = os.path.join(self.notYetDir, "temp.html")
    #     with open(temp_html, "w", encoding="utf-8") as f:
    #         xlsx2html(input_file, f)

    #     # HTML을 PDF로 변환
    #     pdfkit.from_file(temp_html, output_file)
    #     print(f"PDF 저장 완료: {output_file}")

        

    def pdf_to_png(self, pdfFilePath, newFileNm):
        pdfFile = pymupdf.open(os.path.join(self.orgDir, pdfFilePath))

        for page in pdfFile:
            
            pix = page.get_pixmap()
            pix.save(f'{self.notYetDir + os.sep + ".".join(newFileNm.split(".")[0:-1]) + ".png"}','PNG')
            
            break
        
        pdfFile.close()