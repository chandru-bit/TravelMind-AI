FROM python:3.12-slim

WORKDIR /app

COPY shared /app/shared
COPY database /app/database
COPY services/ai-service /app/services/ai-service

RUN pip install --no-cache-dir fastapi uvicorn httpx pydantic pyjwt

EXPOSE 8000

CMD ["uvicorn", "services.ai-service.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
