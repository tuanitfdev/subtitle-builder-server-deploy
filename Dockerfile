# STAGE 1: Builder
# Sử dụng image devel để có trình biên dịch nvcc cài flash-attn
FROM pytorch/pytorch:2.4.0-cuda12.1-cudnn9-devel AS builder

# Thiết lập biến môi trường để tránh các câu hỏi tương tác
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /build

# Cài đặt các công cụ cần thiết để biên dịch (build-essential chứa gcc, g++, v.v.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Cài đặt các thư viện bổ trợ cho quá trình build
RUN pip install --no-cache-dir packaging ninja

# Tạo thư mục chứa các file .whl đã build xong
RUN mkdir -p /build/wheels

# Build flash-attn và insanely-fast-whisper thành file wheel (.whl)
# Cách này giúp chúng ta mang "thành phẩm" sang stage sau cực kỳ sạch sẽ
RUN pip wheel --no-cache-dir --wheel-dir=/build/wheels flash-attn --no-build-isolation
RUN pip wheel --no-cache-dir --wheel-dir=/build/wheels insanely-fast-whisper --ignore-requires-python


# STAGE 2: Final
# Sử dụng image runtime nhẹ hơn nhiều để chạy ứng dụng
FROM pytorch/pytorch:2.4.0-cuda12.1-cudnn9-devel

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# Cài đặt ffmpeg (cần thiết để xử lý âm thanh khi chạy)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy các file .whl đã build từ stage builder sang
COPY --from=builder /build/wheels /app/wheels

# SỬA LỖI: Gỡ bỏ torch/torchvision có sẵn và cài đặt lại ĐỒNG BỘ để nhận diện đúng CUDA
# Lỗi "operator torchvision::nms does not exist" thường do torchvision không tìm thấy CUDA 
# khi được cài đặt riêng lẻ hoặc bị lệch phiên bản với torch có sẵn trong image.
# RUN pip uninstall -y torch torchvision && \
#     pip install --no-cache-dir torch==2.4.0 torchvision==0.19.0 --index-url https://download.pytorch.org/whl/cu121 && \
RUN pip install --no-cache-dir /app/wheels/*.whl && \
    rm -rf /app/wheels

# Kiểm tra lại kỹ hơn: load torchvision.ops và thử gọi một hàm ops
RUN python3 -c "import torch; import torchvision; print(f'Torch version: {torch.__version__}'); print(f'Is CUDA available: {torch.cuda.is_available()}'); import torchvision.ops; print('Torchvision Ops loaded successfully')"

# Cài đặt các dependencies từ file requirements (tập trung logic app ở stage cuối)
COPY requirements.txt .
RUN if [ -s requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Copy toàn bộ code vào sau cùng
COPY . .

# CMD ["python3"]
