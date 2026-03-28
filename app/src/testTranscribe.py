import torch
import stable_whisper
from transformers.utils import is_flash_attn_2_available

# Cấu hình model_kwargs để sử dụng Flash Attention 2 nếu có
model_kwargs = {"attn_implementation": "flash_attention_2"} if is_flash_attn_2_available() else {"attn_implementation": "sdpa"}
print(f"Using model_kwargs: {model_kwargs}")

# Load model whisper-large-v3-turbo bằng stable-ts
# Sử dụng faster-whisper làm backend để hỗ trợ batch_size và chạy cực nhanh trên L4
# compute_type='float16' giúp kích hoạt Flash Attention 2 và Tensor Cores trên GPU L4
model = stable_whisper.load_faster_whisper(
    'large-v3-turbo', 
    device='cuda', 
    compute_type='float16'
)

# Tiến hành transcribe với các tùy chọn để tối ưu timestamp và độ tự nhiên
results = model.transcribe(
    "data/stor/GoIn100Seconds_full.mp3",
    language=None, # Tự động nhận diện ngôn ngữ hoặc điền 'vi'
    word_timestamps=True,
    batch_size=24, # Tối ưu cho GPU L4 (24GB VRAM) - Yêu cầu load_faster_whisper
)

# Xuất kết quả ra file SRT với timestamp câu tự nhiên (không highlight từ đang phát âm)
results.to_srt_vtt('output.srt', segment_level=True, word_level=False)

# Xuất kết quả text thuần ra file outputPlainText.txt
with open('outputPlainText.txt', 'w', encoding='utf-8') as f:
    f.write(results.text)

# In thông báo hoàn tất
print("Transcription completed. Outputs saved to output.srt and outputPlainText.txt")
