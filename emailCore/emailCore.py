from email.header import decode_header, make_header
from email.utils import parseaddr
from datetime import datetime
import imaplib, re, csv, email
import os
from dotenv import load_dotenv

class EmailCore():
    def __init__(self):
        self.detach_dir = os.getcwd()
        print(self.detach_dir)
        if 'attachments' not in os.listdir(self.detach_dir):
            os.mkdir('attachments')
        super().__init__()

        self.session = None

    def connectSession(self, URL, ID, PW):
        
        self.session = imaplib.IMAP4_SSL(URL)

        id = ID
        pw = PW

        # 로그인
        self.session.login(id, pw)

    def disconnectSession(self):
        self.session.close()
        self.session.logout()

    def download(self):

    # 접근하고자 하는 메일함 이름
        self.session.select("INBOX")

        # status = 이메일 접근 상태
        # messages = 선택한 조건에 해당하는 메일의 id 목록
        # ('OK', [b'00001 00002 .....'])
        # status, messages = self.session.uid('search', None)
        status, messages = self.session.search(None, 'ALL')

        messages = messages[0].split()

        # 각 메일에 대하여 실행
        for n, message in enumerate(messages):

            print(f"Writing email #{n} on file...")
            
            # Standard format for fetching email message
            res, msg = self.session.uid('fetch', message, "(RFC822)")  
            print(res)
            print(msg)
            print(type(msg))
            if msg:
                print("continue" + str(n))
                continue

            raw_readable = msg[0][1].decode('utf-8')
            email_message = email.message_from_string(raw_readable)

            # 보낸사람
            fr = make_header(decode_header(email_message.get('From')))
            # print("SENDER : " + fr.encode())
            
            # print("SENDER : " + fr.encode().split()[0])
            # print("SENDER : " + fr.encode().split()[1])
            # print(parseaddr(fr.encode())[1])
            print("SENDER  : " + parseaddr(email_message.get('From'))[1])
            # print(fr.encode());

            # 메일 제목
            # subject = make_header(decode_header(email_message.get('Subject')))
            # print("SUBJECT : " + subject.encode())
            print("SUBJECT : " + email_message.get('Subject'))

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
                        filePath = os.path.join(self.detach_dir, 'attachments', fileNm)
                        if not os.path.isfile(filePath) :
                            print("FILE DOWNLOAD STARTA")
                            fp = open(filePath, 'wb')
                            fp.write(part.get_payload(decode=True))
                            fp.close()

            else:
                body = email_message.get_payload(decode=True).decode('utf-8')
                
            # body = body.decode('utf-8')
            print("CONTENT :\n" + body)
            print("FILENAME :\n" + str(fileNm))

                        