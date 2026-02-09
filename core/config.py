from pydantic_settings import BaseSettings

class Setting(BaseSettings):

    DATABASE_URL : str


    class Config :
        env_file = ".env"
        case_sensitive = None

settings = Setting()