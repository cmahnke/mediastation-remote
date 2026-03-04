FROM python:3.14-alpine

WORKDIR /

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /app

CMD ["fastapi", "run", "app/api.py", "--port", "80", "--proxy-headers"]