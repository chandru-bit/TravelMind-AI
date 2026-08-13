FROM python:3.12-slim

WORKDIR /app

COPY shared /app/shared
COPY database /app/database
COPY services/user-service /app/services/user-service

RUN pip install --no-cache-dir fastapi uvicorn sqlalchemy pydantic pyjwt httpx redis

EXPOSE 8000

CMD ["uvicorn", "services.user-service.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
