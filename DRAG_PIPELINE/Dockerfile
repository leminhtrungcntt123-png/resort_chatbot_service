FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# SỬA Ở ĐÂY: Copy toàn bộ code vào root của WORKDIR (tức là /app)
COPY . . 

EXPOSE 8080

# Chỉnh lại đường dẫn chạy uvicorn nếu cần (tùy vào main.py nằm đâu)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port","8080"]