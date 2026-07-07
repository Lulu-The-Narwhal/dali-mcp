FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir "fastmcp>=0.1.0" "httpx>=0.27.0" "google-genai>=0.8.0" hatchling

# Copy source
COPY dali/ ./dali/

# Hosted mode: enables usage tracking + my_story DB queries
ENV DALI_HOSTED=true

EXPOSE 8080

CMD ["python", "-m", "dali.server"]
