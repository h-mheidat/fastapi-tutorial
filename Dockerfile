# syntax=docker/dockerfile:1.3
FROM python:3.10-slim-buster as base 


FROM base AS build


RUN apt-get update && apt-get install git --no-install-recommends -y


ARG GITHUB_TOKEN
ARG GITHUB_AUTH_URL="https://$GITHUB_TOKEN:x-oauth-basic@github.com"
RUN git config --global url.$GITHUB_AUTH_URL.insteadOf https://github.com


ENV PIP_DISABLE_PIP_VERSION_CHECK=1
COPY requirements.txt .

RUN pip install -r requirements.txt


FROM base AS deploy

COPY --from=build /usr/local /usr/local

WORKDIR /app
COPY . /app

ENV PYTHONPATH=/app/fastapi_demo

EXPOSE 80

STOPSIGNAL SIGINT

CMD ["uvicorn", "--reload", "--workers", "1", "--host", "0.0.0.0", "--port", "80", "fastapi_demo.main:app"]
# CMD ["ddtrace-run", "gunicorn", "--config=gunicorn_conf.py", "-b", "0.0.0.0:8000", "fsp.app:app"]
