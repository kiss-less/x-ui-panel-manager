# syntax=docker/dockerfile:1

FROM python:3.10.12-slim
WORKDIR /app
COPY requirements.txt requirements.txt
COPY api.py api.py
COPY inbound.py inbound.py
COPY script.py script.py
COPY user_expiry_dates.py user_expiry_dates.py
COPY utils.py utils.py
COPY cred.json cred.json
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
CMD [ "python3", "script.py"]
