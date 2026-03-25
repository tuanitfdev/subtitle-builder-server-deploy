import os
from pathlib import Path
from typing import Optional, List, Any
import aioboto3
from botocore.config import Config
from dotenv import load_dotenv
from pprint import pprint

load_dotenv()

class R2Manager:
    _instance: Optional['R2Manager'] = None

    def __init__(self):
        # Tránh khởi tạo nhiều lần nếu dùng get_instance
        self._session = aioboto3.Session()
        self._bucket_name = os.getenv("R2_BUCKET_NAME")
        self._endpoint_url = os.getenv("R2_ENDPOINT_URL")
        self._access_key_id = os.getenv("R2_ACCESS_KEY_ID")
        self._secret_access_key = os.getenv("R2_SECRET_ACCESS_KEY")
        
        # Cấu hình R2 chuyên dụng
        self._config = Config(
            s3={'addressing_style': 'virtual'},
            retries={'max_attempts': 3, 'mode': 'standard'}
        )

    @classmethod
    def get_instance(cls) -> 'R2Manager':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _get_client(self):
        """Tạo context manager cho client"""
        return self._session.client(
            service_name="s3",
            endpoint_url=self._endpoint_url,
            aws_access_key_id=self._access_key_id,
            aws_secret_access_key=self._secret_access_key,
            region_name="auto",
            config=self._config
        )

    async def upload_file(self, file_path: str, object_key: Optional[str] = None):
        path = Path(file_path)
        if not path.exists():
            print(f"File không tồn tại: {file_path}")
            return False

        file_key = object_key or path.name
        
        # Dùng 'async with' để tự động đóng client sau khi xong
        async with self._get_client() as r2:
            try:
                # Đọc file một cách non-blocking (nếu file cực lớn nên dùng aiofiles)
                with open(file_path, "rb") as f:
                    await r2.put_object(
                        Bucket=self._bucket_name, 
                        Key=file_key, 
                        Body=f
                    )
                print(f"Đã upload: {file_key}")
                return True
            except Exception as e:
                print(f"Upload lỗi: {e}")
                return False

    async def check_file_exists(self, file_key: str) -> bool:
        """
        Kiểm tra file có tồn tại trên R2 hay không bằng head_object.
        Trả về True nếu tồn tại, False nếu không.
        """
        async with self._get_client() as r2:
            try:
                # head_object chỉ lấy thông tin đầu ngữ, không tải data
                await r2.head_object(Bucket=self._bucket_name, Key=file_key)
                return True
            except r2.exceptions.ClientError as e:
                # Nếu mã lỗi là 404, chắc chắn file không tồn tại
                if e.response['Error']['Code'] == "NoSuchKey":
                    print(f"File '{file_key}' không tìm thấy trên R2.")
                else:
                    print(f"Lỗi khi check file: {e}")
                return False
            except Exception as e:
                print(f"Lỗi không xác định khi check file: {e}")
                return False

    async def download_file(self, file_key: str, destination_path: Optional[str] = None):
        dest_path = Path(destination_path) if destination_path else Path("data/stor") / file_key
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        async with self._get_client() as r2:
            try:
                response = await r2.get_object(Bucket=self._bucket_name, Key=file_key)
                
                # Mở file để ghi binary
                with open(dest_path, "wb") as f:
                    stream = response["Body"]
                    # Tải và ghi từng block 1MB một
                    while chunk := await stream.read(1024 * 1024):
                        f.write(chunk)
                        
                print(f"Đã tải xong: {dest_path}")
                return str(dest_path)
            except r2.exceptions.ClientError as e:
                # Nếu mã lỗi là 404, chắc chắn file không tồn tại
                if e.response['Error']['Code'] == "NoSuchKey":
                    print(f"File '{file_key}' không tìm thấy trên R2.")
                else:
                    print(f"Lỗi khi check file: {e}")
                    print(f"pprint(e.response):")
                    pprint(e.response)
                    # print(f"pprint(e.__dict__):")
                    # pprint(e.__dict__)
                return None
            except Exception as e:
                print(f"Download lỗi: {e}")
                return None

    async def delete_file(self, file_key: str) -> bool:
        async with self._get_client() as r2:
            try:
                await r2.delete_object(Bucket=self._bucket_name, Key=file_key)
                print(f"Đã xóa: {file_key}")
                return True
            except Exception as e:
                print(f"Xóa lỗi: {e}")
                return False

    async def list_files(self) -> List[dict]:
        async with self._get_client() as r2:
            try:
                response = await r2.list_objects_v2(Bucket=self._bucket_name)
                return response.get('Contents', [])
            except Exception as e:
                print(f"Lỗi list file: {e}")
                return []