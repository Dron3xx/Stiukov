FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN apt-get update && \ 
    apt-get install -y openjdk-17-jre

RUN pip install -r requirements-dev.txt

CMD ["python", "run_tests.py"]