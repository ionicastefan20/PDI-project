FROM bitnami/spark:3.5.1

USER root

COPY requirements.txt /requirements.txt

RUN apt update
RUN apt install libgl1 libglib2.0-0 -y

RUN pip install --upgrade pip
RUN pip install -r /requirements.txt
