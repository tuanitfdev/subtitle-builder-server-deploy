import torch
import stable_whisper
from transformers.utils import is_flash_attn_2_available

# Cấu hình model_kwargs để sử dụng Flash Attention 2 nếu có
model_kwargs = {"attn_implementation": "flash_attention_2"} if is_flash_attn_2_available() else {"attn_implementation": "sdpa"}
print(f"Using model_kwargs: {model_kwargs}")

# Load model whisper-large-v3-turbo bằng stable-ts
# stable-ts giúp lấy timestamp chính xác ở mức độ từ (word-level) và câu (sentence-level)
model = stable_whisper.load_model('large-v3-turbo', device='cuda:0')

# Tiến hành transcribe với các tùy chọn để tối ưu timestamp và độ tự nhiên
# - language: có thể chỉ định 'vi' nếu là tiếng Việt
# - word_timestamps: True để lấy timestamp chính xác từng từ
results = model.transcribe(
    "GoIn100Seconds_1mf.mp3",
    language=None, # Tự động nhận diện ngôn ngữ hoặc điền 'vi'
    word_timestamps=True,
    # stable-ts có các thuật toán giúp timestamp khớp với âm thanh hơn
)

# Xuất kết quả ra file SRT với timestamp câu tự nhiên
results.to_srt_vtt('output.srt')

# Xuất kết quả text thuần ra file outputPlainText.txt
with open('outputPlainText.txt', 'w', encoding='utf-8') as f:
    f.write(results.text)

# In thông báo hoàn tất
print("Transcription completed. Outputs saved to output.srt and outputPlainText.txt")
