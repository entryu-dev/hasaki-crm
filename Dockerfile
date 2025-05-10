FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9-slim

WORKDIR /app

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONPATH /app

# Install Poetry
RUN pip install --upgrade pip && pip install poetry && poetry config virtualenvs.create false

COPY ./ /app

RUN bash -c "poetry install --no-root"
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8082"]
