from pydantic_settings import BaseSettings

class Setting(BaseSettings):

    DATABASE_URL : str
    ACCESS_TOKEN_EXPIRE_MINUTES :int = 15
    REFRESH_TOKEN_EXPIRE_DAYS : int = 7
    ALGORITHM : str ="HS256"
    SECRET_KEY : str = "thisismynewsecretkeyandiscurrentlyusedinthisproject"
    REDIS_URL : str

    FRONTEND_URL: str                   
    FROM_EMAIL: str
    SMTP_HOST: str                      
    SMTP_PORT: int = 587                
    SMTP_USER: str                       
    SMTP_PASSWORD: str   

    MODEL_NAME : str
    CHUNK_SIZE :int
    CHUNK_OVERLAP : int

    CHROMA_DB_DIR :str
    EMBEDDING_DIMENSION : str                



    class Config :
        env_file = ".env"
        case_sensitive = None

settings = Setting()