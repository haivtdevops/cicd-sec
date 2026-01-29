FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    git curl jq \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir semgrep pytest

WORKDIR /workspace

CMD ["bash"]
