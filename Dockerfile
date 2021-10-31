FROM python:3.10
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY localhigh /srv/
WORKDIR /srv
CMD python -m localhigh