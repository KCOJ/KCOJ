FROM python:3.6

ADD . /app/

WORKDIR /app

RUN pip3 install -r requirements.txt

RUN pip3 install gunicorn

CMD gunicorn -w 1 -k gthread --thread=8 -b 0.0.0.0:8000 run:app

EXPOSE 8000