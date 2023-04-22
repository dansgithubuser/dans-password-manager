FROM node:lts-buster-slim
COPY frontend .
RUN npm ci
RUN npm run build


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
COPY --from=0 dist ./frontend/dist
RUN DANS_PASSWORD_MANAGER_SECRET_KEY=x python3 manage.py collectstatic --no-input

EXPOSE 8001

ENTRYPOINT gunicorn\
	-w 1\
	-b 0.0.0.0:8001\
	proj_dans_password_manager.wsgi:application
