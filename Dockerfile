FROM python:3-alpine

RUN \
    apk add --update git \
    && rm -rf /var/cache/apk/*

ADD src/* /opt/
ADD requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

EXPOSE 8000

CMD ["python", "/opt/main.py"]
