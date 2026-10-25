FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY . .
RUN python3 db.py
EXPOSE 3000
CMD ["python3", "server.py"]
