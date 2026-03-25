FROM python:3.11-slim

WORKDIR /app

# نسخ requirements أولاً للاستفادة من Docker cache
COPY requirements.txt .

# تثبيت المكتبات
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# نسخ باقي الملفات
COPY . .

# منفذ التشغيل
EXPOSE $PORT

# أمر التشغيل — PORT يُعطيه Railway تلقائياً
CMD streamlit run app.py \
    --server.port=${PORT:-8501} \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false
