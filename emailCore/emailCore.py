from email.header import decode_header, make_header
from email.utils import parseaddr
from datetime import datetime
import smtplib, imaplib, re, csv, email
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

class EmailCore():
    def __init__(self):
        self.detach_dir = os.getcwd()
        print(self.detach_dir)
        if 'attachments' not in os.listdir(self.detach_dir):
            os.mkdir('attachments')
        super().__init__()

        self.imapSession = None
        self.smtpSession = None

        self.ID = None


    def connectSession(self, URL, ID, PW):
        self.imapSession = imaplib.IMAP4_SSL(URL)
        self.smtpSession = smtplib.SMTP(URL)

        self.smtpSession.ehlo()
        self.smtpSession.starttls()
        
        self.ID = ID
        id = ID
        pw = PW
        
        self.imapSession.login(id, pw)
        self.smtpSession.login(id, pw)

    def disconnectSession(self):
        self.imapSession.close()
        self.imapSession.logout()
        self.smtpSession.quit()

    def sendEmail(self, receiver, subject, content):
        msg = MIMEText('내용 : 본문 내용')
        msg['Subject'] = subject

        self.smtpSession.send(self.ID, receiver, msg.as_string())

    def searchEmail(self):
        self.imapSession.select("INBOX")
        status, messages = self.imapSession.search(None, 'ALL')
        messages = messages[0].split()

        print(messages)

        # 각 메일에 대하여 실행
        for n, message in enumerate(messages):
            
            res, msg = self.imapSession.uid('fetch', message, "(RFC822)")  
            print(res)
            print(msg)
            raw_readable = msg[0][1].decode('utf-8')
            email_message = email.message_from_string(raw_readable)
            # 보낸사람
            
            senderEmail = parseaddr(email_message.get('From'))[1] # [0]=NickName

            #senderEmail 이 고객인지 확인
            if senderEmail != 'radiata03@naver.com':
                self.sendEmail(senderEmail, 'YOU ARE NOT REGISTERED YET', 'PLEASE JOIN CCME SERVICE FIRST. http://www.ccme.co.kr/')
                continue

            subject = email_message.get('Subject')
            
            print("SENDER  : " + senderEmail)
            print("SUBJECT : " + subject)
            
            body = ''
            fileNm = ''
            
            # 메일 내용
            if email_message.is_multipart():
                for part in email_message.walk():
                    fileNm = part.get_filename()
                    ctype = part.get_content_type()
                    if ctype == 'text/plain':
                        body += part.get_payload(decode=True).decode('utf-8')  # decode
                    # if fileNm is not None:
                    #     body += fileNm
                    if bool(fileNm):
                        self.download(fileNm, part)

            else:
                body = email_message.get_payload(decode=True).decode('utf-8')
            # body = body.decode('utf-8')
            print("CONTENT :\n" + body)
            print("FILENAME :\n" + str(fileNm))

                        


    def download(self, fileNm, part):
        filePath = os.path.join(self.detach_dir, 'attachments', fileNm)
        if not os.path.isfile(filePath) :
            print("FILE DOWNLOAD STARTA")
            fp = open(filePath, 'wb')
            fp.write(part.get_payload(decode=True))
            fp.close()

                        