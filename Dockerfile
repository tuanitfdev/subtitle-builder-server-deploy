# syntax=docker/dockerfile:1
# Single Stage Dockerfile for debugging runtime issues

# lightning.ai studio installed image
FROM pytorch/pytorch:2.8.0-cuda12.8-cudnn9-devel

# Thiết lập biến môi trường để tránh các câu hỏi tương tác
ENV DEBIAN_FRONTEND=noninteractive
# Ép uv sử dụng system python và không tạo venv
ENV UV_SYSTEM_PYTHON=1
# Chỉ định thư mục cache cho uv
ENV UV_CACHE_DIR=/root/.cache/uv
# Sử dụng chế độ copy thay vì hardlink để tương thích tốt nhất với Docker mount cache
ENV UV_LINK_MODE=copy

WORKDIR /app

# Cài đặt uv từ image chính thức
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Cài đặt các công cụ cần thiết để biên dịch và chạy
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Cài đặt flash-attn với mount cache và --no-build-isolation
# RUN --mount=type=cache,target=/root/.cache/uv \
#     uv pip install flash-attn --no-build-isolation --no-cache-dir

RUN apt-get update && apt-get install -y curl vim-gtk3 tmux xsel htop net-tools iputils-ping

RUN curl -fLo /root/.vim/autoload/plug.vim --create-dirs https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim && \
    git clone https://github.com/tmux-plugins/tpm /root/.tmux/plugins/tpm && \
    curl -sSfL https://raw.githubusercontent.com/ajeetdsouza/zoxide/main/install.sh | sh && \
    git clone https://github.com/lincheney/fzf-tab-completion.git ~/fzf-tab-completion && \
    cp /root/.bashrc /root/.bashrc.bk

COPY .vimrc .tmux.conf .bashrc /root/

RUN vim +PlugInstall +qall && \
    /root/.tmux/plugins/tpm/bin/install_plugins

# Cài đặt các dependencies từ pyproject.toml với mount cache
COPY pyproject.toml .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install .

# Copy toàn bộ code vào sau cùng
COPY . .

# CMD ["python", "src/mainServer.py"]

