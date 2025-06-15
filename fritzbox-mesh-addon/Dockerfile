FROM python:3.11-slim

RUN pip install flask fritzconnection schedule

WORKDIR /app

COPY fritzmesh.py /app/fritzmesh.py
COPY run.sh /app/run.sh

RUN chmod +x /app/run.sh

CMD [ "/app/run.sh" ]
