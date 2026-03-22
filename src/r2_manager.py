import os
from pathlib import Path
from typing import Optional, List, Any
import aioboto3
from botocore.config import Config
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class R2Manager:
    """
    Manager class for Cloudflare R2 operations.
    Follows Singleton pattern to cache the client connection.
    """
    _instance: Optional['R2Manager'] = None

    def __init__(self):
        if R2Manager._instance is not None:
            raise Exception("This class is a singleton!")
        self._session: Optional[aioboto3.Session] = None
        self._client_context: Any = None
        self._client: Any = None
        self._bucket_name = os.getenv("R2_BUCKET_NAME")

    @classmethod
    def get_instance(cls) -> 'R2Manager':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def get_client(self):
        """
        Returns the R2 client, initializing it if necessary.
        """
        if self._client is not None:
            return self._client

        endpoint_url = os.getenv("R2_ENDPOINT_URL")
        access_key_id = os.getenv("R2_ACCESS_KEY_ID")
        secret_access_key = os.getenv("R2_SECRET_ACCESS_KEY")

        if not all([endpoint_url, access_key_id, secret_access_key]):
            raise ValueError("Missing R2 configuration in environment variables.")

        if self._session is None:
            self._session = aioboto3.Session()

        config = Config(s3={'addressing_style': 'virtual'})
        
        self._client_context = self._session.client(
            service_name="s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name="auto",
            config=config
        )
        
        # Enter context manager and cache the client
        self._client = await self._client_context.__aenter__()
        return self._client

    async def close(self):
        """
        Closes the R2 client connection.
        """
        if self._client_context:
            await self._client_context.__aexit__(None, None, None)
            self._client = None
            self._client_context = None

    async def upload_file(self, file_path: str, object_key: Optional[str] = None):
        """
        Uploads a file to the R2 bucket.
        """
        r2 = await self.get_client()
        path = Path(file_path)
        
        if not path.exists():
            print(f"File not found: {file_path}")
            return
        
        file_key = object_key if object_key else path.name
        try:
            with open(file_path, "rb") as f:
                await r2.put_object(Bucket=self._bucket_name, Key=file_key, Body=f)
            print(f"Uploaded {file_path} to {self._bucket_name}/{file_key}")
        except Exception as e:
            print(f"Upload failed: {e}")

    async def download_file(self, file_key: str, destination_path: Optional[str] = None) -> str:
        """
        Downloads a file from the R2 bucket.
        Returns the path to the downloaded file.
        """
        r2 = await self.get_client()
        if destination_path:
            dest_path = Path(destination_path)
        else:
            dest_path = Path("data/stor") / file_key
        
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            await r2.download_file(self._bucket_name, file_key, str(dest_path))
            print(f"Downloaded {file_key} to {dest_path}")
            return str(dest_path)
        except Exception as e:
            print(f"Download failed: {e}")
            raise e

    async def delete_file(self, file_key: str) -> bool:
        """
        Deletes a file from the R2 bucket.
        """
        r2 = await self.get_client()
        try:
            await r2.delete_object(Bucket=self._bucket_name, Key=file_key)
            print(f"Deleted {file_key} from {self._bucket_name}")
            return True
        except Exception as e:
            print(f"Delete failed for {file_key}: {e}")
            return False

    async def list_files(self) -> List[dict]:
        """
        Lists files in the R2 bucket.
        """
        r2 = await self.get_client()
        try:
            response = await r2.list_objects_v2(Bucket=self._bucket_name)
            return response.get('Contents', [])
        except Exception as e:
            print(f"Failed to list files in bucket '{self._bucket_name}': {e}")
            return []
