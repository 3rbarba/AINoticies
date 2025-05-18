import os
import time
import warnings
import traceback
from datetime import date
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
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

# Importar os Agentes
from agents.topic_finder import identificar_topicos_em_alta
from agents.news_searcher import pesquisar_noticias
from agents.content_editor import editar_conteudo
from agents.content_collector import agente_coletor_detalhado
from agents.content_reviewer import revisar_geral
from agents.publisher import publicar_noticia

# Rota para a página inicial
@app.route('/')
def index():
    return render_template('index.html')

# Rota para gerar notícias
@app.route('/gerar_noticias', methods=['GET'])
def gerar_noticias():
    try:
        # 1. Identificar Tópicos em Alta
        topicos_com_categoria = identificar_topicos_em_alta()
        if not topicos_com_categoria:
            return jsonify({"erro": "Nenhum tópico em alta encontrado."}), 404

        todas_as_noticias = []
        # 2. Pesquisar Notícias para cada Tópico
        for topico_info in topicos_com_categoria:
            topico = topico_info['tópico']
            categoria = topico_info['categoria']
            noticias = pesquisar_noticias(topico, categoria)
            if noticias:
                todas_as_noticias.extend(noticias)

        if not todas_as_noticias:
            return jsonify({"erro": "Nenhuma notícia encontrada para os tópicos em alta."}), 404

        # 3. Coletar Notícias Detalhadas
        noticias_detalhadas = []
        for noticia in todas_as_noticias:
            noticia_detalhada = agente_coletor_detalhado(noticia['título'], noticia['categoria'], noticia, noticia['categoria'])
            if noticia_detalhada:
                noticias_detalhadas.append(noticia_detalhada)

        if not noticias_detalhadas:
            return jsonify({"erro": "Falha ao coletar detalhes das notícias."}), 500

        # 4. Editar Conteúdo
        conteudo_editado = editar_conteudo(noticias_detalhadas)
        if not conteudo_editado:
            return jsonify({"erro": "Falha ao editar o conteúdo das notícias."}), 500

        # 5. Revisar Conteúdo
        conteudo_revisado = revisar_geral(conteudo_editado)
        if not conteudo_revisado:
            return jsonify({"erro": "Falha ao revisar o conteúdo das notícias."}), 500

        # 6. Publicar Notícia
        publicar_noticia(conteudo_revisado)

        return jsonify({"mensagem": "Notícias geradas e publicadas com sucesso."}), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"erro": str(e)}), 500
 
if __name__ == '__main__':
    from routes import *
    # Inicializa o Flask e executa o servidor
    app.run(debug=True, port=5000)
 