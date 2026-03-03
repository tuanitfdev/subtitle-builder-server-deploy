# Sử dụng image PyTorch chính thức với CUDA 12.1 và cuDNN 8 bản devel
# Bản devel (development) cần thiết để có trình biên dịch nvcc cài flash-attn
FROM pytorch/pytorch:2.2.1-cuda12.1-cudnn8-devel

# Thiết lập biến môi trường để tránh các câu hỏi tương tác trong quá trình cài đặt
ENV DEBIAN_FRONTEND=noninteractive

# Cài đặt các thư viện hệ thống cần thiết cho xử lý âm thanh (ffmpeg)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Cài đặt các thư viện bổ trợ cho quá trình build flash-attn
# (Image pytorch thường đã có sẵn torch, nhưng cần thêm packaging/ninja để build nhanh hơn)
RUN pip install --no-cache-dir packaging ninja

# Cài đặt flash-attn với flag --no-build-isolation
# Quá trình này sẽ diễn ra mượt mà vì image devel đã có sẵn nvcc và torch
RUN pip install --no-cache-dir flash-attn --no-build-isolation

# Cài đặt các dependencies còn lại từ file requirements
COPY requirement.txt .
RUN pip install --no-cache-dir -r requirement.txt

# Copy toàn bộ code vào sau cùng
COPY . .

CMD ["python3"]
