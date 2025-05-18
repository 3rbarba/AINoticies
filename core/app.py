import os
import time
import warnings
import traceback
from datetime import date

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template
from flask_cors import CORS
import google.generativeai as genai
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.genai import errors as genai_errors
from google.genai import types
from pytrends.request import TrendReq
warnings.filterwarnings("ignore")

# Configuração Inicial do Flask e CORS
app = Flask(__name__)
CORS(app)

# Configurações de Retentativa
MAX_RETRIES = 3
INITIAL_BACKOFF = 2  # segundos

# Carregamento das Variáveis de Ambiente
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Inicialização do Modelo Gemini
gemini_model = None
if GOOGLE_API_KEY:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        gemini_model = genai.GenerativeModel('models/gemini-2.0-flash-001')
        print("Modelo Gemini inicializado com sucesso.")
        app.config['GEMINI_MODEL'] = gemini_model  # Armazena o modelo na configuração do app
    except Exception as e:
        print(f"Erro ao inicializar o modelo Gemini: {e}")
else:
    print("Chave da API do Google Generative AI não encontrada no arquivo .env")

# Inicialização do Pytrends
pytrends = TrendReq(hl='pt-BR', tz=-180)

# Importe as rotas
if __name__ == '__main__':
    from routes import *  # Import routes here to avoid circular imports
    app.run(debug=True)