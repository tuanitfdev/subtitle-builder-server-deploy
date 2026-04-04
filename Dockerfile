FROM ghcr.io/tuanitfdev/whisper-model-hub-deploy:latest as model-hub

# FROM tuanitfdev/whisper-model-hub:latest

# FROM pytorch/pytorch:2.8.0-cuda12.8-cudnn9-devel
FROM vastai/pytorch:2.8.0-cu128-cuda-12.9-mini-py312-2026-03-26

# Thiết lập biến môi trường để tránh các câu hỏi tương tác
ENV DEBIAN_FRONTEND=noninteractive
# Ép uv sử dụng system python và không tạo venv
ENV UV_SYSTEM_PYTHON=1
# Chỉ định thư mục cache cho uv
ENV UV_CACHE_DIR=/root/.cache/uv
# Sử dụng chế độ copy thay vì hardlink để tương thích tốt nhất với Docker mount cache
ENV UV_LINK_MODE=copy

WORKDIR /opt/ws/app

# Cài đặt uv từ image chính thức
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV VIRTUAL_ENV=/venv/main
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Cài đặt các công cụ cần thiết để biên dịch và chạy
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY --from=model-hub /data/models /data/models
COPY --from=model-hub /data/cacheTorchHub /root/.cache/torch/hub
COPY --from=model-hub /data/whl /data/whl

# Cài đặt flash-attn từ pre-built wheel
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install /data/whl/flash_attn-2.8.3+cu12torch2.9cxx11abiTRUE-cp312-cp312-linux_x86_64.whl && rm -rf /data/whl

RUN mkdir -p ~/myShellEnv && curl -L https://github.com/tuanitfdev/myShellEnv/tarball/main | tar -C ~/myShellEnv -xz --strip-components=1 && cd ~/myShellEnv/src && \
    bash ./setupBash02TmuxFzfNo_ZoxideFromUbuntu.sh && \
    rm -rf ~/myShellEnv

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Cài đặt các dependencies từ pyproject.toml với mount cache
COPY app/pyproject.toml pyproject.toml
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install .

# Copy toàn bộ code vào sau cùng
COPY app .

COPY supervisor/app.conf  /etc/supervisor/conf.d/
COPY supervisor/app.sh /opt/supervisor-scripts/
RUN chmod +x /opt/supervisor-scripts/app.sh

COPY bootScript/20-my-first-boot.sh /etc/vast_boot.d/first_boot/
RUN chmod +x /etc/vast_boot.d/first_boot/20-my-first-boot.sh

ENTRYPOINT ["entrypoint.sh"]

# CMD ["supervisord", "-c", "/etc/supervisor/supervisord.conf"]
# with default config at /etc/supervisor/supervisord.conf 

