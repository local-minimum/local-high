FROM python:3.10
COPY requirements.txt .
RUN pip install gunicorn
RUN pip install -r requirements.txt
COPY launcher.sh /srv/
COPY localhigh /srv/localhigh
WORKDIR /srv
