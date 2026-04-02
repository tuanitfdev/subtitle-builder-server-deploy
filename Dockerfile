FROM ghcr.io/tuanitfdev/whisper-model-hub-deploy:latest as model-hub

tuanitfdev/whisper-model-hub-deploy

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

# Cài đặt flash-attn từ pre-built wheel
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install https://github.com/Dao-AILab/flash-attention/releases/download/v2.8.3/flash_attn-2.8.3+cu12torch2.9cxx11abiTRUE-cp312-cp312-linux_x86_64.whl

RUN apt-get update && apt-get install -y curl vim-gtk3 tmux xsel htop net-tools iputils-ping

RUN git clone https://github.com/tuanitfdev/myShellEnv.git ~/myShellEnv && \
    cd ~/myShellEnv/src && \
    chmod +x setupBashTmuxFzfNo_ZoxideFromUbuntu.sh && \
    ./setupBashTmuxFzfNo_ZoxideFromUbuntu.sh && \
    rm -rf ~/myShellEnv

COPY --from=model-hub /models /models

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

ENTRYPOINT ["entrypoint.sh"]

# CMD ["supervisord", "-c", "/etc/supervisor/supervisord.conf"]
# with default config at /etc/supervisor/supervisord.conf 

