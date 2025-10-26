from langchain_groq import ChatGroq 
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models import BaseChatModel
from pydantic import SecretStr
from app.core.settings import get_settings

# --- Build Custom Error --- 
class LLMFactoryError(ValueError):
    """
        Custom Error for issues during LLM Client Creation
    """
# --- Build Groq LLM ---
def build_groq_llm(model: str , temperature: float = 0.7 ) -> BaseChatModel:
    """
        Build a Groq LLM Client with the given model name and temperature.
    """
    settings = get_settings()

    # --- Check API Key --- 
    if not settings.groq_api_key:
        raise LLMFactoryError("GROQ_API_KEY is missing in settings. Cannot initialize Groq LLM.")

    # --- Build LLM Client --- 
    llm = ChatGroq(
        model=model,    
        temperature=temperature,
        api_key=SecretStr(settings.groq_api_key)
    )
    return llm 
# --- Build Gemini LLM --- 
def build_gemini_llm(model: str , temperature: float = 0.7 ) -> BaseChatModel:
    """
        Build a Gemini LLM Client with the given model name and temperature.
    """
    settings = get_settings()

    # --- Check API Key --- 
    if not settings.gemini_api_key:
        raise LLMFactoryError("GEMINI_API_KEY is missing in settings. Cannot initialize Gemini LLM.")

    # --- Build LLM Client --- 
    llm = ChatGoogleGenerativeAI(
        model=model,    
        temperature=temperature,
        google_api_key=settings.gemini_api_key
    )
    return llm
