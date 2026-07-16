FROM python:3.12-slim


WORKDIR /app


COPY pyproject.toml uv.lock ./

# --frozen uses when installaion fails don't reinstall deps
RUN pip install uv && uv sync --frozen --no-dev 


COPY . .


EXPOSE 8000

CMD uv run alembic upgrade head && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000


