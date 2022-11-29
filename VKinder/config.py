import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    V = '5.131'
    VK_GROUP_TOKEN = os.getenv('VK_GROUP_TOKEN')
    VK_TOKEN = os.getenv('VK_TOKEN')
    OWNER = os.getenv("OWNER") 

    DRIVER = "postgresql"
    USERNAME = "postgres"
    PASSWORD = "64381261"
    HOST = "localhost"
    PORT = "5432"
    DATABASE = "vkinder"

    DATABASE_URL = (
        f"{DRIVER}://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
    )

settings = Settings()