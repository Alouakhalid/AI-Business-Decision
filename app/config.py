import os
from dotenv import load_dotenv

load_dotenv(override=True)

class Config:
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    COHERE_API_KEY: str = os.getenv("COHERE_API_KEY", "")
    
    GROQ_MODEL_PRIMARY: str = os.getenv("GROQ_MODEL_PRIMARY", "llama-3.3-70b-versatile")
    GROQ_MODEL_FAST: str = os.getenv("GROQ_MODEL_FAST", "llama-3.1-8b-instant")
    
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")

    @classmethod
    def update_keys(cls, groq_key: str = None, cohere_key: str = None, primary_model: str = None, fast_model: str = None):
        """Updates runtime configuration and persists back to .env file."""
        env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        
        if groq_key is not None:
            cls.GROQ_API_KEY = groq_key.strip()
        if cohere_key is not None:
            cls.COHERE_API_KEY = cohere_key.strip()
        if primary_model is not None:
            cls.GROQ_MODEL_PRIMARY = primary_model.strip()
        if fast_model is not None:
            cls.GROQ_MODEL_FAST = fast_model.strip()

        # Update environment variables
        os.environ["GROQ_API_KEY"] = cls.GROQ_API_KEY
        os.environ["COHERE_API_KEY"] = cls.COHERE_API_KEY
        os.environ["GROQ_MODEL_PRIMARY"] = cls.GROQ_MODEL_PRIMARY
        os.environ["GROQ_MODEL_FAST"] = cls.GROQ_MODEL_FAST

        # Save to .env file
        lines = [
            f"GROQ_API_KEY={cls.GROQ_API_KEY}\n",
            f"COHERE_API_KEY={cls.COHERE_API_KEY}\n",
            f"GROQ_MODEL_PRIMARY={cls.GROQ_MODEL_PRIMARY}\n",
            f"GROQ_MODEL_FAST={cls.GROQ_MODEL_FAST}\n",
            f"API_PORT={cls.API_PORT}\n",
            f"API_HOST={cls.API_HOST}\n"
        ]
        try:
            with open(env_file, "w") as f:
                f.writelines(lines)
        except Exception as e:
            print(f"Warning: Failed to persist .env updates: {e}")

config = Config()
