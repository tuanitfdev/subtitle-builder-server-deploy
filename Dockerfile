# Single Stage Dockerfile for debugging runtime issues
FROM nvcr.io/nvidia/pytorch:25.02-py3

# Thiết lập biến môi trường để tránh các câu hỏi tương tác
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# Cài đặt các công cụ cần thiết để biên dịch và chạy
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Cài đặt các thư viện bổ trợ cho quá trình build
RUN pip install --no-cache-dir packaging ninja

# Cài đặt trực tiếp các thư viện nặng (flash-attn, insanely-fast-whisper)
# Dùng 1 stage giúp dễ debug hơn khi có lỗi biên dịch hoặc runtime
RUN pip install --no-cache-dir flash-attn --no-build-isolation
RUN pip install --no-cache-dir insanely-fast-whisper --ignore-requires-python

# Kiểm tra lại kỹ hơn: load torchvision.ops và thử gọi một hàm ops
# RUN python3 -c "import torch; import torchvision; print(f'Torch version: {torch.__version__}'); print(f'Is CUDA available: {torch.cuda.is_available()}'); import torchvision.ops; print('Torchvision Ops loaded successfully')"

# Cài đặt các dependencies từ file requirements
COPY requirements.txt .
RUN if [ -s requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Copy toàn bộ code vào sau cùng
COPY . .

# CMD ["python3"]
