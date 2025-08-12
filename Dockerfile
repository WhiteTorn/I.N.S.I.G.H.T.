FROM python:3.12-slim

WORKDIR /app

COPY backend ./backend/

RUN pip install --upgrade pip && pip install -r backend/requirements.txt

COPY frontend ./frontend/
RUN apt-get update && apt-get install -y nodejs npm
RUN cd frontend && npm install && npm run dev

RUN cp -r frontend/dist backend/static

EXPOSE 8083

CMD ["python", "backend/start_api.py"]