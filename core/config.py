from pydantic_settings import BaseSettings

class Setting(BaseSettings):

    DATABASE_URL : str
    ACCESS_TOKEN_EXPIRE_MINUTES :int = 15
    REFRESH_TOKEN_EXPIRE_DAYS : int = 7
    ALGORITHM : str ="HS256"
    SECRET_KEY : str = "thisismynewsecretkeyandiscurrentlyusedinthisproject"
    REDIS_URL : str


    class Config :
        env_file = ".env"
        case_sensitive = None

settings = Setting()