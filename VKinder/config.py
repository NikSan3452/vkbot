class Settings:
    GROUP_TOKEN = ""
    USER_TOKEN = ""
    VERSION = "5.131"

    DRIVER = ""
    USERNAME = ""
    PASSWORD = ""
    HOST = ""
    PORT = ""
    DATABASE = ""
    DATABASE_URL = f"{DRIVER}://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
