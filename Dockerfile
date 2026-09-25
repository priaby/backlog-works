FROM python:3.12-slim

WORKDIR /app
COPY app/ /app/app/

# No third-party dependencies: stdlib http.server only.
CMD ["python3", "app/main.py"]
