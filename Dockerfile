FROM python:3.12-alpine AS development_build

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_ENV=${DJANGO_ENV} \
  # python:
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  # pip:
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  # poetry:
  POETRY_VERSION=1.7.0 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry'


RUN apk add tiff-dev jpeg-dev zlib-dev freetype-dev lcms2-dev libwebp-dev tcl-dev tk-dev libffi-dev
RUN apk update  \
    && apk add --no-cache bash curl git libpq wget gcc musl-dev make  \
    && apk del --purge apk-tools && pip install "poetry==1.7.0" && poetry --version


RUN mkdir /api
RUN mkdir /static

WORKDIR /api

WORKDIR /api
COPY ./pyproject.toml  /api/
COPY ./poetry.lock  /api/


RUN poetry install --no-root
COPY . /api/