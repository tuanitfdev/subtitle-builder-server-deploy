from r2_manager import R2Manager
# load dotenv
from dotenv import load_dotenv
import asyncio
load_dotenv()

def main():
    asyncio.run(test())

async def test():
    r2_manager = R2Manager.get_instance()
    # print _bucket_name, _endpoint_url, _access_key_id, _secret_access_key
    print("Bucket Name:", r2_manager._bucket_name)
    print("Endpoint URL:", r2_manager._endpoint_url)
    print("Access Key ID:", r2_manager._access_key_id)
    print("Secret Access Key:", r2_manager._secret_access_key)
    
    # client = await r2_manager.get_client()
    await r2_manager.download_file("GoIn100Seconds_1mf.mp3", "data/stor/test.mp3")

if __name__ == "__main__":
    main()