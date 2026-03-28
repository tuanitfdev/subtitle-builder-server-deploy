from transformers.utils import is_flash_attn_2_available

if is_flash_attn_2_available():
    print("Flash Attention 2 is available")
else:
    print("Flash Attention 2 is not available")