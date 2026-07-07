FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir "fastmcp>=0.1.0" "httpx>=0.27.0" hatchling

COPY dali/ ./dali/

# DALI_TOKEN required — get yours at dali.getlulu.dev (free GitHub OAuth login)
ENV DALI_TRANSPORT=http

EXPOSE 8080

CMD ["python", "-m", "dali.server"]
