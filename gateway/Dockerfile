FROM python:3.12-slim

WORKDIR /app

# Copy root requirements & shared package
COPY shared /app/shared
COPY database /app/database
COPY gateway /app/gateway

RUN pip install --no-cache-dir fastapi uvicorn httpx redis pydantic pyjwt sqlalchemy

EXPOSE 8000

CMD ["uvicorn", "gateway.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
