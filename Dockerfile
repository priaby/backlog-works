FROM python:3.12-slim

WORKDIR /app
COPY src/ /app/src/
ENV PYTHONPATH=/app/src

# No third-party dependencies: stdlib http.server only.
CMD ["python3", "-m", "backlogworks"]
