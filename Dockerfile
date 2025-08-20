FROM python:3.12-slim

WORKDIR /app

# Keep Python output unbuffered and pip clean
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install Node (for Vite dev server), bash (for entrypoint), and tini (PID 1 / signal handling)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl gnupg bash nodejs npm tini \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy source
COPY backend ./backend
COPY frontend ./frontend

# Install frontend dependencies (dev deps needed for 'npm run dev')
RUN cd frontend && npm ci || npm install

# Entry script to run both backend and frontend dev server
# - Reads /app/.env if present (recommended: pass with `--env-file` or mount it)
RUN bash -lc 'cat > /usr/local/bin/start-insight << "EOF"\n#!/usr/bin/env bash\nset -euo pipefail\n\nterm_handler() {\n  kill -TERM \"${BACK_PID:-0}\" 2>/dev/null || true\n  kill -TERM \"${FE_PID:-0}\" 2>/dev/null || true\n  wait || true\n}\ntrap term_handler SIGTERM SIGINT\n\nif [ -f \"/app/.env\" ]; then\n  set -a\n  . /app/.env\n  set +a\nfi\n\npython backend/start_api.py &\nBACK_PID=$!\n\n( cd /app/frontend && npm run dev -- --host ) &\nFE_PID=$!\n\n# Wait for either to exit, then propagate status\nwait -n || true\nexit $?\nEOF\nchmod +x /usr/local/bin/start-insight'

# Expose frontend (Vite dev) and backend ports
EXPOSE 5173 8000

# Use tini as PID 1 for clean signal handling
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/usr/local/bin/start-insight"]