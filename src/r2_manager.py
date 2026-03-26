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
        # Avoid multiple initializations when using get_instance
        self._session = aioboto3.Session()
        self._bucket_name = os.getenv("R2_BUCKET_NAME")
        self._endpoint_url = os.getenv("R2_ENDPOINT_URL")
        self._access_key_id = os.getenv("R2_ACCESS_KEY_ID")
        self._secret_access_key = os.getenv("R2_SECRET_ACCESS_KEY")
        
        # Dedicated R2 configuration
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
        """Create context manager for client"""
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
            print(f"File does not exist: {file_path}")
            return False

        file_key = object_key or path.name
        
        # Use 'async with' to automatically close client when done
        async with self._get_client() as r2:
            try:
                # Read file in a non-blocking way (for very large files consider using aiofiles)
                with open(file_path, "rb") as f:
                    await r2.put_object(
                        Bucket=self._bucket_name, 
                        Key=file_key, 
                        Body=f
                    )
                print(f"Uploaded: {file_key}")
                return True
            except Exception as e:
                print(f"Upload error: {e}")
                return False

    async def check_file_exists(self, file_key: str) -> bool:
        """
        Check if a file exists on R2 using head_object.
        Returns True if it exists, False otherwise.
        """
        async with self._get_client() as r2:
            try:
                # head_object only fetches metadata, does not download data
                await r2.head_object(Bucket=self._bucket_name, Key=file_key)
                return True
            except r2.exceptions.ClientError as e:
                # If error code is 404, the file definitely does not exist
                if e.response['Error']['Code'] == "NoSuchKey":
                    print(f"File '{file_key}' not found on R2.")
                else:
                    print(f"Error checking file: {e}")
                return False
            except Exception as e:
                print(f"Unknown error checking file: {e}")
                return False

    async def download_file(self, file_key: str, destination_path: Optional[str] = None):
        dest_path = Path(destination_path) if destination_path else Path("data/stor") / file_key
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        async with self._get_client() as r2:
            try:
                response = await r2.get_object(Bucket=self._bucket_name, Key=file_key)
                
                # Open file for binary writing
                with open(dest_path, "wb") as f:
                    stream = response["Body"]
                    # Download and write in 1MB chunks
                    while chunk := await stream.read(1024 * 1024):
                        f.write(chunk)
                        
                print(f"Download complete: {dest_path}")
                return str(dest_path)
            except r2.exceptions.ClientError as e:
                # If error code is 404, the file definitely does not exist
                if e.response['Error']['Code'] == "NoSuchKey":
                    print(f"File '{file_key}' not found on R2.")
                else:
                    print(f"Error checking file: {e}")
                    print(f"pprint(e.response):")
                    pprint(e.response)
                    # print(f"pprint(e.__dict__):")
                    # pprint(e.__dict__)
                return None
            except Exception as e:
                print(f"Download error: {e}")
                return None

    async def delete_file(self, file_key: str) -> bool:
        async with self._get_client() as r2:
            try:
                await r2.delete_object(Bucket=self._bucket_name, Key=file_key)
                print(f"Deleted: {file_key}")
                return True
            except Exception as e:
                print(f"Delete error: {e}")
                return False

    async def list_files(self) -> List[dict]:
        async with self._get_client() as r2:
            try:
                response = await r2.list_objects_v2(Bucket=self._bucket_name)
                return response.get('Contents', [])
            except Exception as e:
                print(f"List files error: {e}")
                return []