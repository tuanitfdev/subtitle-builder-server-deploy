import torch
from transformers import pipeline
from transformers.utils import is_flash_attn_2_available

model_kwargs = {"attn_implementation": "flash_attention_2"} if is_flash_attn_2_available() else {"attn_implementation": "sdpa"}
print(f"Using model_kwargs: {model_kwargs}")

pipe = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-large-v3", # select checkpoint from https://huggingface.co/openai/whisper-large-v3#model-details
    torch_dtype=torch.float16,
    device="cuda:0", # or mps for Mac devices
    model_kwargs=model_kwargs,
)

outputs = pipe(
    "GoIn100Seconds_1mf.mp3",
    chunk_length_s=30,
    batch_size=24,
    return_timestamps=True,
)

import json

with open("output.json", "w", encoding="utf-8") as f:
    json.dump(outputs, f, ensure_ascii=False, indent=2)

print(outputs)