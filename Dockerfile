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

# RUN pip install --no-cache-dir packaging ninja
# Cài đặt trực tiếp các thư viện nặng (flash-attn, insanely-fast-whisper)
# Dùng 1 stage giúp dễ debug hơn khi có lỗi biên dịch hoặc runtime
# RUN pipx install insanely-fast-whisper --force --pip-args="--ignore-requires-python"
# RUN pipx runpip insanely-fast-whisper install flash-attn --no-build-isolation

RUN pip install flash-attn --no-build-isolation
RUN pip install insanely-fast-whisper --ignore-requires-python


#RUN pipx install --no-cache-dir insanely-fast-whisper --ignore-requires-python


# Xóa các bản cài đặt cũ nếu có để tránh xung đột
# RUN pip uninstall -y torch torchvision torchaudio

# Cài đặt bộ 3 Torch & Torchvision (đảm bảo hết lỗi NMS)
# RUN pip install --no-cache-dir --force-reinstall torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# Fix lỗi NMS bằng cách cài cặp đôi này cùng nhau
#RUN pip install --no-cache-dir --force-reinstall \
#    torch==2.5.1 \
#    torchvision==0.20.1 \
#    torchaudio==2.5.1 \
#    --index-url https://download.pytorch.org/whl/cu124


# Kiểm tra lại kỹ hơn: load torchvision.ops và thử gọi một hàm ops



# Kiểm tra lại kỹ hơn: load torchvision.ops và thử gọi một hàm ops
# RUN python3 -c "import torch; import torchvision; print(f'Torch version: {torch.__version__}'); print(f'Is CUDA available: {torch.cuda.is_available()}'); import torchvision.ops; print('Torchvision Ops loaded successfully')"

# Cài đặt các dependencies từ file requirements
COPY requirements.txt .
RUN if [ -s requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Copy toàn bộ code vào sau cùng
COPY . .

# CMD ["python3"]