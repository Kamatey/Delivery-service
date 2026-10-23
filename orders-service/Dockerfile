# 1. Start from a small official Python image
FROM python:3.12-slim

# 2. Bring in uv (the fast Python package manager) from its official image
COPY --from=ghcr.io/astral-sh/uv:0.9.26 /uv /bin/uv

WORKDIR /app

# 3. Install dependencies first (without dev tools like pytest).
#    Docker caches this layer, so rebuilding after a code change is fast.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# 4. Copy the application code
COPY app ./app

# 5. Run as a normal user, not root. /data holds the SQLite database file.
RUN useradd --create-home appuser && mkdir /data && chown appuser /data
USER appuser

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000

# 6. Start the FastAPI app with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
