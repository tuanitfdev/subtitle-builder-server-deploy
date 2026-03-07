# Single Stage Dockerfile for debugging runtime issues

# insane-fast-whisper installed image
# FROM pytorch/pytorch:2.5.1-cuda12.1-cudnn9-devel

# lightning.ai studio installed image
FROM pytorch/pytorch:2.8.0-cuda12.8-cudnn9-devel

# Thiết lập biến môi trường để tránh các câu hỏi tương tác
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# Cài đặt các công cụ cần thiết để biên dịch và chạy
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pipx

RUN pip install flash-attn --no-build-isolation --no-cache-dir


# Cài đặt các dependencies từ file requirements
COPY requirements.txt .
RUN if [ -s requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Copy toàn bộ code vào sau cùng
COPY . .

# CMD ["python3"]