import litserve as ls
import torch
import stable_whisper as whisper
from transformers.utils import is_flash_attn_2_available
import aioboto3
import os
import uuid
from contextlib import asynccontextmanager

# Giả sử bạn config R2/S3 qua biến môi trường
R2_BUCKET = os.getenv("R2_BUCKET_NAME")
R2_ENDPOINT_URL = os.getenv("R2_ENDPOINT_URL")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")

class SubtitleBuilderAPI(ls.LitAPI):
    def setup(self, device):
        self.device = device
        print(f"Loading Whisper model on {device}...")
        # Load model stable-whisper (faster-whisper backend)
        # Tối ưu cho GPU với float16 và Flash Attention 2 nếu có
        self.model = whisper.load_faster_whisper(
            "large-v3-turbo", 
            device=self.device, 
            compute_type="float16"
        )
        # Khởi tạo session cho aioboto3
        self.session = aioboto3.Session()        

    async def decode_request(self, request):
        """
        Xử lý request async: Tải file từ R2/S3 về local tạm thời
        """
        file_key = request.get("file_key") # Key của file trên R2
        if not file_key:
            return {"error": "Missing file_key"}

        # Tạo path tạm để lưu audio
        temp_file = f"data/stor/{os.path.basename(file_key)}"
        
        print(f"Downloading {file_key} from R2 to {temp_file}...")
        
        async with self.session.client(
            's3',
            endpoint_url=R2_ENDPOINT_URL,
            aws_access_key_id=R2_ACCESS_KEY_ID,
            aws_secret_access_key=R2_SECRET_ACCESS_KEY
        ) as s3:
            await s3.download_file(R2_BUCKET, file_key, temp_file)
            
        return {
            "audio_path": temp_file,
            "language": request.get("language"),
            "task": request.get("task", "transcribe")
        }

    def predict(self, x):
        """
        Xử lý inference đồng bộ (Sync) trên GPU để tối ưu hiệu năng
        """
        if "error" in x:
            return x
            
        audio_path = x["audio_path"]
        audio_filename = os.path.basename(audio_path)
        try:
            print(f"Transcribing {audio_path}...")
            result = self.model.transcribe(
                audio_path,
                language=x.get("language"),
                task=x.get("task"),
                vad=True,
                word_timestamps=True,
                batch_size=24
            )
            return {"result": result,
              "audio_filename": audio_filename}
        except Exception as e:
            return {"error": str(e), "audio_path": audio_path}

    def encode_response(self, output):
        """
        Trả về kết quả và dọn dẹp file tạm
        """

        audio_filename = output.get("audio_filename")
        audio_filename0Ext = audio_filename.split(".")[0]
        rawResult = output.get("result")
        rawResult.to_srt_vtt(f"data/stor/{audio_filename0Ext}.srt", segment_level=True, word_level=False)
        # Dọn dẹp file tạm sau khi đã xử lý xong
        audio_path = f"data/stor/{audio_filename}"
        result = {
            "subtitleFileKey": f"{audio_filename0Ext}.srt",
            "audioFileKey": audio_filename,
            "msg": "Subtitle generated successfully"
        }
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)
            print(f"Removed temp file: {audio_path}")
            
        if "error" in output:
            return {"status": "error", "message": output["error"]}
            
        return {"status": "success", "data": output["result"]}

if __name__ == "__main__":
    api = SubtitleBuilderAPI()
    
    # Cấu hình server
    server = ls.LitServer(
        api, 
        accelerator="auto", 
        devices=1, 
        workers_per_device=1, # Quan trọng: Giới hạn 1 worker để tránh OOM GPU
        timeout=600           # Tăng timeout cho audio dài
    )
    
    server.run(port=8000)
