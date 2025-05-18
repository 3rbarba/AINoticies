from app import app  # Importe a instância do Flask do app.py
from flask import jsonify, render_template
import traceback

from agents.content_collector import agente_coletor_detalhado
from agents.topic_finder import identificar_topicos_em_alta
from agents.news_searcher import pesquisar_ultimas_noticias
from agents.content_editor import editar_conteudo
from agents.content_reviewer import revisar_geral
from agents.publisher import publicar_noticia
from utils import call_agent
from google.adk.agents import Agent
from google.adk.tools import google_search

# -------------------- Endpoints Flask --------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/gerar_noticia', methods=['GET'])
def gerar_noticia():
    print("Iniciando o fluxo de geração de notícia (edição e imagem)...")
    try:
        topicos_em_alta = identificar_topicos_em_alta()
        if topicos_em_alta:
            primeiro_topico_info = topicos_em_alta[0]
            primeiro_topico = primeiro_topico_info['tópico']
            noticias_pesquisadas = pesquisar_ultimas_noticias(primeiro_topico)
            if noticias_pesquisadas:
                conteudo_editado = editar_conteudo(noticias_pesquisadas[:1])
                return jsonify({"status": "Edição de conteúdo realizada", "resultado": conteudo_editado})
            else:
                return jsonify({"erro": f"Não foram encontradas notícias para o tópico '{primeiro_topico}'"})
        else:
            return jsonify({"erro": "Não foi possível identificar tópicos em alta"})
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"ERRO: {str(e)}")
        print(error_traceback)
        return jsonify({"erro": f"Erro no processamento: {str(e)}", "detalhes": error_traceback})

@app.route('/gerar_noticia_completa', methods=['GET'])
def gerar_noticia_completa_endpoint():
    print("Iniciando o fluxo de geração de notícia completa...")
    try:
        topicos_em_alta = identificar_topicos_em_alta()
        if not topicos_em_alta:
            return jsonify({"erro": "Não foi possível identificar tópicos em alta"})

        resultados_completos = []  # Lista para armazenar os resultados de cada tópico

        for topico_info in topicos_em_alta:
            topico = topico_info['tópico']
            categoria = topico_info.get('categoria', 'A DEFINIR')
            noticias = pesquisar_ultimas_noticias(topico, categoria)

            if noticias:
                detalhes_noticia = agente_coletor_detalhado(
                    topico,
                    True,
                    str(noticias),
                    categoria
                )

                conteudo_editado = editar_conteudo(noticias[:1])

                noticia_completa = {
                    **conteudo_editado,
                    'noticia_completa': detalhes_noticia.get('noticia_completa', ''),
                    'fonte': detalhes_noticia.get('fonte', noticias[0].get('fonte', '')),
                    'data': detalhes_noticia.get('data', noticias[0].get('data', '')),
                    'categoria': categoria,
                    'topico': topico,  # Adicionando o tópico para identificação
                    'noticias_originais': noticias  # Adicionando as notícias originais
                }

                noticia_revisada = revisar_geral(noticia_completa)

                # publicar_noticia(noticia_revisada)  # Comentei a publicação para retornar os resultados
                resultados_completos.append(noticia_revisada)  # Adiciona o resultado à lista
            else:
                resultados_completos.append({
                    "erro": f"Nenhuma notícia válida foi encontrada para o tópico: {topico}",
                    "topico": topico
                })

        return jsonify({"status": "Processo de geração de notícias completo", "resultados": resultados_completos})  # Retorna todos os resultados

    except Exception as e:
        error_traceback = traceback.format_exc()
        print(f"ERRO: {str(e)}")
        print(error_traceback)
        return jsonify({
            "erro": f"Erro no processamento: {str(e)}",
            "detalhes": error_traceback
        })