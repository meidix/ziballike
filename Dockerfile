FROM python:3.10

RUN mkdir /app

WORKDIR /app

COPY . .

RUN python -m pip install --upgrade pip

RUN pip install -r reqs.txt
