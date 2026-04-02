from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SERVICE_NAME: str = "Emotion Detection CV Service"
    SERVICE_VERSION: str = "1.0.0"
    SERVICE_PORT: int = 8001
    DETECTOR_BACKEND: str = "opencv"   # opencv | retinaface | mtcnn
    MAX_IMAGE_SIZE: int = 1280

    class Config:
        env_file = ".env"


settings = Settings()
