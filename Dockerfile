FROM python:3.12-slim AS builder

WORKDIR /app
COPY . /app
RUN pip install --upgrade pip setuptools wheel
RUN pip3 install -r requirements.txt
EXPOSE 5000
ENTRYPOINT ["python3"]
CMD ["main.py"]