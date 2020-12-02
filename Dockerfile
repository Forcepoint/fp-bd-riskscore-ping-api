FROM python:3.6.10-alpine3.11

WORKDIR /app

ARG _HOME_DIR_NAME=fp-riskexporter-api
ENV _HOME_DIR_NAME=${_HOME_DIR_NAME}

COPY container-files container-files/

RUN apk update && apk add --no-cache bash \
    wget \
    gcc musl-dev python3-dev \
    && tar -zxvf container-files/${_HOME_DIR_NAME}-v*.tar.gz \
    && rm -f container-files/${_HOME_DIR_NAME}-v*.tar.gz \
    && pip install pipenv cython \
    && cd ${_HOME_DIR_NAME} \
    && pipenv install --skip-lock \
    && pipenv run pip freeze > requirements.txt \
    && pipenv --rm \
    && pip uninstall -y pipenv \
    && pip install --no-cache-dir -r requirements.txt \
    && cd .. \
    && mkdir ${_HOME_DIR_NAME}/certs \
    && chmod 700 ${_HOME_DIR_NAME}/src/modules/main_run.py \
    container-files/entrypoint.sh

EXPOSE 5000/tcp

ENTRYPOINT ["./container-files/entrypoint.sh"]
