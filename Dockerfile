FROM python:3-alpine

RUN \
    apk add --update git \
    && rm -rf /var/cache/apk/*

COPY src requirements.txt /opt/

RUN pip install -r /opt/requirements.txt

EXPOSE 8000

CMD ["python", "/opt/src/main.py"]
