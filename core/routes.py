from app import app
from flask import jsonify, render_template, request
import traceback

from agents.content_collector import agente_coletor_detalhado
from agents.topic_finder import identificar_topicos_em_alta
from agents.news_searcher import pesquisar_noticias
from agents.content_editor import editar_conteudo
from agents.content_reviewer import revisar_geral
from agents.publisher import publicar_noticia
from utils import call_agent
from google.adk.agents import Agent
from google.adk.tools import google_search

# -------------------- Endpoints Flask --------------------
def index():
    return render_template('index.html')

@app.route('/gerar_noticia', methods=['GET'])
def gerar_noticia():
    # ... (seu código para gerar uma notícia resumida)
    pass

@app.route('/noticia_completa', methods=['POST'])
def noticia_completa():
    # ... (seu código para exibir a notícia completa)
    pass

@app.route('/gerar_noticia_completa', methods=['GET'])
def gerar_noticia_completa_route():
    print("Iniciando o fluxo de geração de notícia completa...")
    try:
        topicos_em_alta = identificar_topicos_em_alta()
        if topicos_em_alta:
            primeiro_topico_info = topicos_em_alta[0]
            primeiro_topico = primeiro_topico_info['tópico']
            categoria = primeiro_topico_info['categoria']
            noticias_pesquisadas = pesquisar_noticias(primeiro_topico, categoria)
            if noticias_pesquisadas:
                detalhes_noticia = agente_coletor_detalhado(
                    primeiro_topico,
                    True,
                    noticias_pesquisadas,
                    categoria
                )
                return jsonify({"status": "Notícia completa gerada com sucesso!", "noticia": detalhes_noticia})
            else:
                return jsonify({"erro": "Nenhuma notícia encontrada para o tópico em alta."})
        else:
            return jsonify({"erro": "Nenhum tópico em alta encontrado."})
    except Exception as e:
        error_traceback = traceback.format_exc()
        print(f"ERRO: {str(e)}")
        print(error_traceback)
        return jsonify({"erro": f"Erro ao gerar notícia completa: {str(e)}", "detalhes": error_traceback})