import litserve as ls
import torch
import stable_whisper as whisper
from transformers.utils import is_flash_attn_2_available
from fastapi import HTTPException
from my_exception import MyException
from my_logger import MyLogger
from r2_manager import R2Manager
import os
import traceback


# load dotenv
from dotenv import load_dotenv
load_dotenv()

class SubtitleBuilderAPI(ls.LitAPI):
    def setup(self, device):
        try:
            print(f"Loading Whisper model on {device}...")
            # Load model stable-whisper (faster-whisper backend)
            # Optimized for GPU with float16 and Flash Attention 2 if available
            self.model = whisper.load_faster_whisper(
                "deepdml/faster-whisper-large-v3-turbo-ct2", 
                # "large-v3", 
                device="cuda", 
                compute_type="float16",
                device_index=[0],
                download_root="/data/models",
            )
            # print("da mock load faster whisper")
            self.r2_manager = R2Manager.get_instance()
        
        except Exception as e:
            MyLogger.log_error(f"Failed to load model or initialize R2Manager: {str(e)}", payload={
                "device": device,
                "exception": traceback.format_exc()  # full stack trace as string
            })
            raise

    async def decode_request(self, request):
        """
        Handle async request: Download file from R2/S3 to local temp storage
        """
        file_key = request.get("file_key") # Key of the file on R2
        if not file_key:
            MyLogger.log_error("Missing 'file_key' in request", payload={
                "request": request
            })
            raise HTTPException(status_code=400, detail="Missing 'file_key' in request")

        # Create temp path to store audio
        audio_path = f"data/stor/{os.path.basename(file_key)}"
        
        print(f"Downloading {file_key} from R2 to {audio_path}...")
        
        try:
            res = await self.r2_manager.download_file(file_key, audio_path)
        except Exception as e:
            MyLogger.log_error(f"Failed to download file from R2: {str(e)}", payload={
                "file_key": file_key,
                "exception": traceback.format_exc()  # full stack trace as string
            })
            raise HTTPException(status_code=500, detail="Internal Server Error")
        return {
            "audio_path": audio_path,
            "audio_filename": file_key,
            "language": request.get("language", "None"),
            "task": request.get("task", "transcribe")
        }

    async def predict(self, x):
        """
        Handle synchronous inference on GPU for optimal performance
        """
        audio_path = x.get("audio_path")
        audio_filename = x.get("audio_filename")
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
            # result = "da transcribe thanh cong"
            return {
                "result": result,
                "audio_filename": audio_filename,
                "audio_path": audio_path
            }
        except Exception as e:
            MyLogger.log_error(f"Transcription failed: {str(e)}", payload={
                "audio_path": audio_path,
                "audio_filename": audio_filename,
                "exception": traceback.format_exc()  # full stack trace as string
            })
            raise HTTPException(status_code=500, detail="Transcription failed")

    async def encode_response(self, output):
        """
        Return result and clean up temp files
        """
        try:
            audio_filename = output.get("audio_filename")
            audio_filename0Ext = audio_filename.split(".")[0]
            srt_path = f"data/stor/{audio_filename0Ext}.srt"
            rawResult = output.get("result")
            try:
                rawResult.to_srt_vtt(srt_path, segment_level=True, word_level=False)

                if srt_path and os.path.exists(srt_path):
                    # Upload SRT file to R2
                    srt_key = f"{audio_filename0Ext}.srt"
                    await self.r2_manager.upload_file(srt_path, srt_key)
                    print(f"Uploaded SRT to R2 with key: {srt_key}")
                else:
                    msg = f"SRT file not found after transcription: {srt_path}"
                    payload = {
                        "audio_filename": audio_filename,
                        "srt_path": srt_path
                    }
                    MyLogger.log_error(msg, payload=payload)
                    raise MyException(msg, payload=payload)
            except Exception as e:
                MyLogger.log_error(f"Failed to save SRT file: {str(e)}", payload={
                    "audio_filename": audio_filename,
                    "srt_path": srt_path,
                    "exception": traceback.format_exc()  # full stack trace as string
                })
                raise
            
            # print("rawResult processed")
            # Clean up temp files after processing
            # create mocked srt file
            # with open(f"data/stor/{audio_filename0Ext}.srt", "w") as f:
            #     f.write("test")
            # print("mocked srt file created")
            result = {
                "subtitleFileKey": f"{audio_filename0Ext}.srt",
                "audioFileKey": audio_filename,
                "msg": f"Subtitle {audio_filename0Ext}.srt generated successfully"
            }
            audio_path = f"data/stor/{audio_filename}"
            if audio_path and os.path.exists(audio_path):
                os.remove(audio_path)
                print(f"Removed temp file: {audio_path}")
                
            return {"status": "success", "data": result}
        except Exception as e:
            MyLogger.log_error(f"Failed to encode response: {str(e)}", payload={
                "audio_filename": output.get("audio_filename"),
                "exception": traceback.format_exc()  # full stack trace as string
            })
            raise HTTPException(status_code=500, detail="Failed to encode response or clean up")

if __name__ == "__main__":
    api = SubtitleBuilderAPI(enable_async=True)
    
    # Server configuration
    server = ls.LitServer(
        api, 
        accelerator="auto", 
        devices=1, 
        workers_per_device=1, # Important: Limit to 1 worker to avoid GPU OOM
        timeout=600           # Tăng timeout cho audio dài
    )
    
    server.run(port=8000, generate_client_file=False)
