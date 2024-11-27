FROM python:3.9

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN playwright install-deps 
RUN playwright install
COPY . .

EXPOSE 3000

CMD ["pytest"]