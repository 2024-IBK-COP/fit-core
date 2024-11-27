# CCME CORE

- email 을 보내고 받고

- openAI 를 활용하고

- pdf를 저장하고 변환하고


```shell
uvicorn main:app --reload --host=0.0.0.0
```
```shell
gunicorn -k uvicorn.workers.UvicornWorker --access-logfile ./gunicorn-access.log main:app --bind 0.0.0.0:8000 --workers 2 --daemon
```

## .env

프로젝트 루트 디렉토리에 위치

```shell
pip install python-dotenv
```

```.env
EMAIL="abcd@abcd.com"
PASSWORD="abcdabcdabcd"
OPEN-AI_KEY="abcdabcdabcdabcd"
```

> /email/check  ->  /invoice/all/save

## /email/check
이메일 하나하나씩 체크한 뒤에 그 안의 인보이스 파일 저장 및 답장

## /invoice/all/save
저장된 인보이스 파일을 AI 돌려서 데이터 추출후 DB에 저장

## /invoice/{invoice_id}
인보이스 파일 다운로드

