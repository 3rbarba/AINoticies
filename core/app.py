from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime
import json
import re
import threading
import time
from typing import Optional
from dataclasses import dataclass
import os
import io
import mimetypes
import struct
import google.generativeai as genai

# --- ADIÇÃO NECESSÁRIA: Importar a chave da API do config.py ---
from config import GOOGLE_API_KEY as GEMINI_API_KEY_FROM_CONFIG

try:
    from google.adk.agents import Agent
    from google.adk.tools import google_search
    from utils import call_agent
except ImportError:
    print("AVISO: 'google.adk' ou 'utils' não encontradas. A geração de notícias pode falhar.")
    Agent = None
    google_search = None
    def call_agent(agent, prompt): return "{}"

from utils_cache_sqlite import * # Importa as funções atualizadas

# --- Configuração do Flask ---
app = Flask(__name__)
CORS(app)

# --- Configuração da API Gemini para TTS ---
try:
    if not GEMINI_API_KEY_FROM_CONFIG:
        print("AVISO: GEMINI_API_KEY não definida em config.py. A funcionalidade TTS falhará.")
    else:
        genai.configure(api_key=GEMINI_API_KEY_FROM_CONFIG)
except Exception as e:
    print(f"Erro ao configurar Gemini TTS: {e}")

# --- Tuas Classes e Sistema de Notícias Existentes ---
@dataclass
class NewsArticle:
    titulo: str = ""
    fonte: str = ""
    resumo: str = ""
    data: str = ""
    categoria: str = ""
    noticia_completa: str = ""

class NewsSystemOptimized:
    def __init__(self, model: str = "gemini-2.0-flash"):
        self.model = model
        self._setup_agents()

    def _setup_agents(self):
        if Agent:
            self.unified_agent = Agent(
                name="agente_unificado_noticias",
                model=self.model,
                instruction="""
                Você é um jornalista especializado em pesquisa e produção de conteúdo.
                Suas funções incluem:
                1. Identificar tópicos em alta
                2. Pesquisar notícias relevantes
                3. Gerar conteúdo completo e bem estruturado
                """,
                tools=[google_search]
            )
        else:
            self.unified_agent = None

    def get_trending_topics(self, limit: int = 20):
        if not self.unified_agent: return []

        hoje = datetime.today().strftime("%Y-%m-%d")
        prompt = f"""
        Use Google Search para identificar os {limit} tópicos mais relevantes e comentados da semana.
        Data: {hoje}
        Retorne:
        {{
            "topicos": [
                {{"topico": "...", "categoria": "..."}}
            ]
        }}
        """
        try:
            response = call_agent(self.unified_agent, prompt)
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return data.get("topicos", [])
        except Exception as e:
            print(f"Erro ao buscar tópicos: {e}")
        return []

    def search_and_process_news(self, topico: str, categoria: str) -> Optional[dict]:
        if not self.unified_agent: return None

        prompt = f"""
        Gere uma notícia detalhada para o tópico: {topico} (categoria: {categoria})
        Formato:
        {{
            "noticia": {{
                "titulo": "...",
                "data": "...",
                "fonte": "...",
                "categoria": "{categoria}",
                "noticia_completa": "..."
            }},
            "status": "Notícia completa gerada com sucesso!"
        }}
        """
        try:
            response = call_agent(self.unified_agent, prompt)
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            print(f"Erro ao processar notícia: {e}")
        return None

# --- Funções Auxiliares para TTS ---
def convert_to_wav(audio_data: bytes, mime_type: str) -> bytes:
    """Gera um cabeçalho WAV para os dados de áudio."""
    parameters = parse_audio_mime_type(mime_type)
    bits_per_sample = parameters["bits_per_sample"]
    sample_rate = parameters["rate"]
    num_channels = 1
    data_size = len(audio_data)
    bytes_per_sample = bits_per_sample // 8
    block_align = num_channels * bytes_per_sample
    byte_rate = sample_rate * block_align
    chunk_size = 36 + data_size

    print(f"Convertendo para WAV: bits_per_sample={bits_per_sample}, sample_rate={sample_rate}, num_channels={num_channels}, data_size={data_size}")
    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF", chunk_size, b"WAVE", b"fmt ",
        16, 1, num_channels, sample_rate,
        byte_rate, block_align, bits_per_sample,
        b"data", data_size
    )
    return header + audio_data

def parse_audio_mime_type(mime_type: str) -> dict[str, int | None]:
    """Extrai bits_per_sample e rate do MIME type."""
    bits_per_sample = 16
    rate = 24000
    print(f"Analisando MIME type: {mime_type}")
    parts = mime_type.split(";")
    for param in parts:
        param = param.strip()
        if param.lower().startswith("rate="):
            try:
                rate = int(param.split("=", 1)[1])
            except (ValueError, IndexError):
                pass
        elif param.startswith("audio/L"):
            try:
                bits_per_sample = int(param.split("L", 1)[1])
            except (ValueError, IndexError):
                pass
    print(f"Analisado: bits_per_sample={bits_per_sample}, rate={rate}")
    return {"bits_per_sample": bits_per_sample, "rate": rate}


# --- Inicialização ---
news_system = NewsSystemOptimized()
init_cache_db()
processing_status = {}

# --- Tuas Rotas Existentes ---
@app.route('/api/topics', methods=['GET'])
def get_trending():
    try:
        limit = min(max(request.args.get('limit', 20, type=int), 1), 50)
        topicos = news_system.get_trending_topics(limit)
        return jsonify({
            "success": True,
            "topics": topicos,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Rota /api/news/<topic> (GET) - Agora vai buscar as notícias mais recentes pelo título
@app.route('/api/news/<topic>', methods=['GET'])
def get_news_by_title_or_generate(topic): # Renomeado para maior clareza
    try:
        categoria = request.args.get("categoria", "Geral")

        # Prioriza buscar as últimas notícias do banco de dados pelo título
        # Isso vai buscar o 'topico' do HTML que na verdade é o 'titulo' da notícia
        # Vamos buscar por notícias onde o título contenha o 'topic' fornecido
        latest_news_list = get_latest_news_by_title(topic, limit=1) # Busca a mais recente
        
        if latest_news_list:
            cached_data = latest_news_list[0]
            # O tópico no cache é o tópico original da busca.
            # O "título" da notícia no JSON é o que o usuário vê.
            return jsonify({
                "noticia": cached_data["noticia"],
                "from_cache": True,
                "audio_data_available": cached_data["audio_data"] is not None,
                "timestamp": datetime.now().isoformat(),
                "topico_original_do_cache": cached_data["topico"], # Retorna para o frontend
                "categoria_original_do_cache": cached_data["categoria"] # Retorna para o frontend
            })

        # Se não encontrar no cache, tenta gerar uma nova notícia
        result = news_system.search_and_process_news(topic, categoria)
        if result and result.get("noticia"):
            news_data = result["noticia"]
            # Salva no cache com o 'topic' original da busca e a categoria
            save_news_to_cache(topic, categoria, news_data) 
            result["from_cache"] = False
            result["audio_data_available"] = False # Áudio não disponível ainda
            result["timestamp"] = datetime.now().isoformat()
            result["topico_original_do_cache"] = topic
            result["categoria_original_do_cache"] = categoria
            return jsonify(result)

        return jsonify({"success": False, "error": "Notícia não encontrada ou gerada"}), 404
    except Exception as e:
        print(f"Erro na rota /api/news/<topic>: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/news', methods=['POST'])
def post_news():
    try:
        data = request.get_json()
        topico = data.get("topico")
        categoria = data.get("categoria", "Geral")
        if not topico:
            return jsonify({"success": False, "error": "topico obrigatório"}), 400

        # Para POST, ainda vamos tentar buscar a mais recente que corresponde
        latest_news_list = get_latest_news_by_title(topico, limit=1)
        if latest_news_list:
            cached_data = latest_news_list[0]
            return jsonify({
                "noticia": cached_data["noticia"],
                "from_cache": True,
                "audio_data_available": cached_data["audio_data"] is not None,
                "timestamp": datetime.now().isoformat(),
                "topico_original_do_cache": cached_data["topico"],
                "categoria_original_do_cache": cached_data["categoria"]
            })

        result = news_system.search_and_process_news(topico, categoria)
        if result and result.get("noticia"):
            news_data = result["noticia"]
            save_news_to_cache(topico, categoria, news_data)
            result["from_cache"] = False
            result["audio_data_available"] = False
            result["timestamp"] = datetime.now().isoformat()
            result["topico_original_do_cache"] = topico
            result["categoria_original_do_cache"] = categoria
            return jsonify(result)

        return jsonify({"success": False, "error": "Notícia não encontrada"}), 404
    except Exception as e:
        print(f"Erro na rota /api/news (POST): {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

# Rota /api/news/history (NOVA ROTA)
@app.route('/api/news/history', methods=['GET'])
def news_history():
    try:
        limit = request.args.get("limit", 10, type=int)
        # Garante que o limite não é irrealista (e.g., muito grande ou negativo)
        limit = max(1, min(limit, 100)) 
        
        history = get_news_history(limit)
        
        # Prepara os dados para o frontend
        formatted_history = []
        for item in history:
            formatted_history.append({
                "topico": item["topico"], # O tópico original da busca
                "categoria": item["categoria"], # A categoria original
                "noticia": item["noticia"], # O dicionário completo da notícia
                "audio_data_available": item["audio_data"] is not None,
                "created_at": item["created_at"]
            })

        return jsonify({
            "success": True,
            "count": len(formatted_history),
            "history": formatted_history
        })
    except Exception as e:
        print(f"Erro na rota /api/news/history: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


# Rota para servir o áudio diretamente do cache
@app.route('/api/news/audio/<topico_encoded>/<categoria_encoded>', methods=['GET'])
def get_news_audio(topico_encoded, categoria_encoded):
    # Decodifica os parâmetros da URL, pois o frontend os enviará encodidos
    topico = topico_encoded # Já vem decodificado pelo Flask para o @app.route
    categoria = categoria_encoded # Já vem decodificado pelo Flask para o @app.route

    print(f"Tentando buscar áudio para tópico: {topico}, categoria: {categoria}")

    cached_data = get_cached_news(topico, categoria)
    if cached_data and cached_data["audio_data"]:
        print(f"Áudio encontrado no cache para {topico}")
        audio_data = cached_data["audio_data"]
        mime_type = cached_data["audio_mime_type"] or "audio/wav" # Default para wav

        return send_file(
            io.BytesIO(audio_data),
            mimetype=mime_type,
            as_attachment=False,
            download_name='noticia_cached.wav'
        )
    print(f"Áudio não encontrado no cache para {topico}")
    return jsonify({"error": "Áudio não encontrado para esta notícia no cache."}), 404

# Rota para Gemini TTS - AGORA SALVA O ÁUDIO NO CACHE TAMBÉM
@app.route('/api/gemini-tts', methods=['POST'])
def generate_tts_endpoint():
    """
    Endpoint para gerar áudio TTS usando Gemini e salvar no cache.
    Recebe texto, voz, tópico e categoria via JSON.
    Gera o áudio, converte se necessário, salva no cache e retorna o arquivo de áudio.
    """
    if not GEMINI_API_KEY_FROM_CONFIG:
        print("ERRO: GEMINI_API_KEY não está configurada em config.py.")
        return jsonify({"error": "Configuração da API Key em falta no servidor (verifique config.py)."}), 500

    data = request.json
    text_to_speak = data.get('text')
    voice = data.get('voice', 'Zephyr')
    topico = data.get('topico', 'desconhecido')
    categoria = data.get('categoria', 'Geral')

    if not text_to_speak:
        return jsonify({"error": "Texto não fornecido."}), 400

    try:
        model_name = "gemini-2.5-flash-preview-tts"
        contents = [
            {"parts": [{"text": text_to_speak}]}
        ]
        generate_content_config = {
            "response_modalities": ["AUDIO"],
            "speech_config": {
                "voice_config": {
                    "prebuilt_voice_config": {"voice_name": voice}
                }
            },
        }

        print(f"Gerando áudio para: '{text_to_speak[:60]}...' com voz '{voice}'")

        audio_chunks = []
        output_mime_type = "audio/wav"

        model = genai.GenerativeModel(model_name)

        response_stream = model.generate_content(
            contents=contents,
            generation_config=generate_content_config,
            stream=True
        )

        # Processa os chunks de áudio recebidos do Gemini
        for chunk in response_stream:
            if chunk.candidates and chunk.candidates[0].content and chunk.candidates[0].content.parts:
                part = chunk.candidates[0].content.parts[0]
                if part.inline_data and part.inline_data.data:
                    inline_data = part.inline_data
                    data_buffer = inline_data.data
                    mime_type = inline_data.mime_type

                    file_extension = mimetypes.guess_extension(mime_type)

                    # Se for áudio cru (ex: L16), converte para WAV
                    if file_extension is None and "L16" in mime_type:
                        print("Formato L16 detectado, convertendo para WAV...")
                        data_buffer = convert_to_wav(data_buffer, mime_type)
                        output_mime_type = "audio/wav"
                    else:
                        output_mime_type = mime_type

                    audio_chunks.append(data_buffer)

        if not audio_chunks:
            print("Nenhum dado de áudio recebido da Gemini.")
            return jsonify({"error": "Falha ao gerar áudio."}), 500

        full_audio_data = b"".join(audio_chunks)
        print(f"Áudio gerado: {len(full_audio_data)} bytes, Tipo: {output_mime_type}")

        # Salva o áudio no cache após gerar
        # Usa o 'topico' e 'categoria' fornecidos para atualizar a notícia correspondente
        cached_news_data = get_cached_news(topico, categoria)
        if cached_news_data and cached_news_data["noticia"]:
            save_news_to_cache(topico, categoria, cached_news_data["noticia"], full_audio_data, output_mime_type)
            print(f"Áudio salvo no cache para tópico '{topico}', categoria '{categoria}'.")
        else:
            print(f"AVISO: Notícia para tópico '{topico}', categoria '{categoria}' não encontrada no cache para salvar áudio. Isso pode ocorrer se a notícia for nova e o áudio for gerado antes da notícia ser persistida.")

        return send_file(
            io.BytesIO(full_audio_data),
            mimetype=output_mime_type,
            as_attachment=False,
            download_name='noticia.wav'
        )

    except Exception as e:
        print(f"Erro crítico na API /api/gemini-tts: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Erro interno do servidor: {str(e)}"}), 500

# --- Executar o Servidor ---
if __name__ == "__main__":
    print("Iniciando o servidor Flask na porta 5000...")
    app.run(port=5000, debug=True)