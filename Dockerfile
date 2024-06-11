FROM python:3.11

RUN pip install --upgrade pip

RUN useradd -rms /bin/bash dev && chmod 777 /opt /run

WORKDIR /mechanics_bot

RUN chown -R dev:dev /mechanics_bot && chmod 755 /mechanics_bot

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY --chown=dev:dev . .