FROM python:3.12-slim

WORKDIR /app

COPY shared /app/shared
COPY database /app/database
COPY services/notification-service /app/services/notification-service

RUN pip install --no-cache-dir fastapi uvicorn sqlalchemy psycopg2-binary pydantic pyjwt httpx redis

EXPOSE 8000

CMD ["uvicorn", "services.notification-service.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
