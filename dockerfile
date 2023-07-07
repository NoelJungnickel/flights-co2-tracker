FROM python:3.11

WORKDIR /server
COPY server /server

RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y redis-server
RUN chmod +x /server/start.sh
RUN chmod +x /server/main.py

EXPOSE 8000

CMD ["./start.sh"]