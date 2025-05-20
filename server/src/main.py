import os
import uvicorn
import dotenv

dotenv.load_dotenv()

SERVER_HOST = os.getenv("SERVER_HOST")
SERVER_PORT = os.getenv("SERVER_PORT")
CLIENT_IP = os.getenv("CLIENT_IP")

if __name__ == "__main__":
    uvicorn.run("src.server:app", host=SERVER_HOST, port=int(SERVER_PORT), reload=True)