FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONIOENCODING utf-8

COPY requirements.txt /tmp/requirements.txt

RUN pip install --upgrade pip && pip install wheel &&\
    pip install --no-cache-dir -r /tmp/requirements.txt


COPY . /proj
RUN useradd -m -d /proj -s /bin/bash app \
    && chown -R app:app /proj/*
WORKDIR /proj
USER app