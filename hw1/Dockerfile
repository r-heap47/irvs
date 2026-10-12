FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /srv

# Сначала только зависимости: этот слой кэшируется, пока не меняется requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN useradd --system --no-create-home --uid 10001 appuser
COPY app/ ./app/

USER appuser
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
