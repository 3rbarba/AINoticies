import os
import warnings
from dotenv import load_dotenv
import google.generativeai as genai
from pytrends.request import TrendReq

# Ignorar avisos
warnings.filterwarnings("ignore")

# Carregamento das Variáveis de Ambiente
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Configurações de Retentativa
MAX_RETRIES = 3
INITIAL_BACKOFF = 2  # segundos

# Inicialização do Modelo Gemini
gemini_model = None
if GOOGLE_API_KEY:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        gemini_model = genai.GenerativeModel('models/gemini-2.0-flash-001')
        print("Modelo Gemini inicializado com sucesso.")
    except Exception as e:
        print(f"Erro ao inicializar o modelo Gemini: {e}")
else:
    print("Chave da API do Google Generative AI não encontrada no arquivo .env")

# Inicialização do Pytrends
pytrends = TrendReq(hl='pt-BR', tz=-180)
