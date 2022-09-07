FROM python:3-slim-buster

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt update
RUN apt install -y libpq-dev gcc

WORKDIR /pwm
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY dans_password_manager ./dans_password_manager
COPY proj_dans_password_manager ./proj_dans_password_manager
COPY do.py .
COPY go.py .
COPY manage.py .
COPY git-state.txt .
RUN DJANGOGO_ENV=local python3 manage.py collectstatic --no-input

EXPOSE 8001

ENTRYPOINT gunicorn\
	-w 4\
	-b 0.0.0.0:8001\
	--certfile=/etc/letsencrypt/live/$DOMAIN/fullchain.pem\
	--keyfile=/etc/letsencrypt/live/$DOMAIN/privkey.pem\
	proj_dans_password_manager.wsgi:application
