FROM python:3.12-slim AS builder
RUN python -m venv /opt/venv
COPY requirements.txt .
RUN /opt/venv/bin/pip install -r requirements.txt

FROM builder AS test
COPY requirements-dev.txt .
RUN /opt/venv/bin/pip install -r requirements-dev.txt
ENV PATH="/opt/venv/bin:$PATH"
WORKDIR /code
COPY . .
CMD ["pytest"]

FROM python:3.12-slim
ENV PATH="/opt/venv/bin:$PATH"
RUN useradd app
WORKDIR /code
COPY --from=builder /opt/venv /opt/venv
COPY alembic.ini .
COPY migrations ./migrations
COPY app ./app
USER app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
