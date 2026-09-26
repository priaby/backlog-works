FROM python:3.12-slim

WORKDIR /app
COPY src/ /app/src/
COPY docs/product/backlog.md /app/docs/product/backlog.md
ENV PYTHONPATH=/app/src

# No third-party dependencies: stdlib http.server only.
CMD ["python3", "-m", "backlogworks"]
