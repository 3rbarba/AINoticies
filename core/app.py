from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from google.adk.agents import Agent
from google.adk.tools import google_search
from utils import call_agent
from datetime import date, datetime
import json
import re
import asyncio
import threading
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import time


@dataclass
class NewsArticle:
    """Estrutura padronizada para artigos de notícia"""
    titulo: str = ""
    fonte: str = ""
    resumo: str = ""
    data: str = ""
    categoria: str = ""
    noticia_completa: str = ""


class NewsSystem:

    def __init__(self, model: str = "gemini-2.0-flash"):
        self.model = model
        self._setup_agents()
    
    def _setup_agents(self):
        """Configura todos os agentes necessários"""
        self.unified_agent = Agent(
            name="agente_unificado_noticias",
            model=self.model,
            instruction="""
            Você é um jornalista especializado em pesquisa e produção de conteúdo.
            Suas funções incluem:
            1. Identificar tópicos em alta
            2. Pesquisar notícias relevantes
            3. Gerar conteúdo completo e bem estruturado
            
            Sempre retorne respostas em JSON válido conforme o formato solicitado.
            Mantenha a qualidade jornalística e verifique as informações.
            """,
            description="Agente unificado para processamento completo de notícias",
            tools=[google_search]
        )
    
    def get_trending_topics(self, limit: int = 30) -> List[Dict[str, str]]:
        """Identifica tópicos em alta de forma otimizada"""
        hoje = date.today().strftime("%Y-%m-%d")
        
        prompt = f"""
        Use google_search para identificar os {limit} tópicos mais relevantes e comentados da semana atual.
        Data de hoje: {hoje}
        
        Retorne APENAS um JSON válido no formato:
        {{
            "topicos": [
                {{"topico": "nome do tópico", "categoria": "categoria"}},
                ...
            ]
        }}
        
        Priorize atualidade e relevância.
        """
        
        try:
            response = call_agent(self.unified_agent, prompt)
            if response:
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    return data.get('topicos', [])
        except Exception as e:
            print(f"Erro ao buscar tópicos: {e}")
        
        return []
    
    def search_and_process_news(self, topico: str, categoria: str) -> Optional[Dict]:
        """Busca e processa notícias de forma unificada"""
        prompt = f"""
        Execute as seguintes etapas para o tópico "{topico}" (categoria: {categoria}):
        
        1. Use google_search para encontrar as 3 notícias mais relevantes e recentes
        2. Selecione a melhor notícia
        3. Gere um texto completo e informativo (mínimo 4 parágrafos)
        4. Compile todas as informações
        
        Retorne APENAS um JSON válido no formato:
        {{
            "noticia": {{
                "titulo": "título da notícia",
                "data": "data da notícia",
                "fonte": "fontes utilizadas",
                "categoria": "{categoria}",
                "noticia_completa": "texto completo da notícia com mínimo 4 parágrafos"
            }},
            "status": "Notícia completa gerada com sucesso!"
        }}
        
        Se não encontrar notícias válidas, retorne:
        {{
            "noticia": null,
            "status": "Nenhuma notícia relevante encontrada"
        }}
        """
        
        try:
            response = call_agent(self.unified_agent, prompt)
            if response:
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    return data
        except Exception as e:
            print(f"Erro ao processar notícia para {topico}: {e}")
        
        return {
            "noticia": None,
            "status": f"Erro ao processar notícia sobre {topico}"
        }


# Inicializar Flask
app = Flask(__name__)
CORS(app)
news_system = NewsSystem()

# Armazenamento em memória para status de processamento
processing_status = {}
news_cache = {}

def index():
    return render_template('index.html')


@app.route('/', methods=['GET'])
def home():
    """Endpoint de boas-vindas"""
    return jsonify({
        "message": "Sistema de Notícias API",
        "version": "2.0",
        "endpoints": {
            "trending_topics": "/api/topics",
            "process_news": "/api/news",
            "specific_topic": "/api/news/<topic>",
            "batch_process": "/api/batch",
            "status": "/api/status/<job_id>"
        }
    })


@app.route('/api/topics', methods=['GET'])
def get_trending_topics():
    """Endpoint para buscar tópicos em alta"""
    try:
        limit = request.args.get('limit', default=15, type=int)
        limit = min(max(limit, 1), 50)  # Limita entre 1 e 50
        
        topicos = news_system.get_trending_topics(limit)
        
        return jsonify({
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "count": len(topicos),
            "topics": topicos
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500


@app.route('/api/news/<topic>', methods=['GET'])
def process_single_news(topic):
    """Endpoint para processar uma notícia específica"""
    try:
        categoria = request.args.get('categoria', 'Geral')
        
        # Verifica cache
        cache_key = f"{topic}_{categoria}"
        if cache_key in news_cache:
            cached_result = news_cache[cache_key]
            cached_result['from_cache'] = True
            return jsonify(cached_result)
        
        resultado = news_system.search_and_process_news(topic, categoria)
        
        if resultado:
            # Adiciona metadados
            resultado['timestamp'] = datetime.now().isoformat()
            resultado['topic_requested'] = topic
            resultado['categoria_requested'] = categoria
            resultado['from_cache'] = False
            
            # Salva no cache
            news_cache[cache_key] = resultado
            
            return jsonify(resultado)
        else:
            return jsonify({
                "success": False,
                "error": "Falha ao processar notícia",
                "topic": topic,
                "timestamp": datetime.now().isoformat()
            }), 404
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "topic": topic,
            "timestamp": datetime.now().isoformat()
        }), 500


@app.route('/api/news', methods=['POST'])
def process_news_from_body():
    """Endpoint para processar notícia via POST com dados no body"""
    try:
        data = request.get_json()
        
        if not data or 'topico' not in data:
            return jsonify({
                "success": False,
                "error": "Campo 'topico' é obrigatório"
            }), 400
        
        topico = data['topico']
        categoria = data.get('categoria', 'Geral')
        
        resultado = news_system.search_and_process_news(topico, categoria)
        
        if resultado:
            resultado['timestamp'] = datetime.now().isoformat()
            resultado['topic_requested'] = topico
            resultado['categoria_requested'] = categoria
            
            return jsonify(resultado)
        else:
            return jsonify({
                "success": False,
                "error": "Falha ao processar notícia",
                "timestamp": datetime.now().isoformat()
            }), 404
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500


def process_batch_async(topics_list, job_id):
    """Processa múltiplos tópicos de forma assíncrona"""
    processing_status[job_id] = {
        "status": "processing",
        "progress": 0,
        "total": len(topics_list),
        "results": [],
        "started_at": datetime.now().isoformat()
    }
    
    try:
        for i, topic_data in enumerate(topics_list):
            if isinstance(topic_data, dict):
                topico = topic_data.get('topico', '')
                categoria = topic_data.get('categoria', 'Geral')
            else:
                topico = str(topic_data)
                categoria = 'Geral'
            
            resultado = news_system.search_and_process_news(topico, categoria)
            
            if resultado and resultado.get('noticia'):
                processing_status[job_id]["results"].append(resultado)
            
            # Atualiza progresso
            processing_status[job_id]["progress"] = i + 1
            
            # Pequena pausa para evitar sobrecarga
            time.sleep(1)
        
        processing_status[job_id]["status"] = "completed"
        processing_status[job_id]["completed_at"] = datetime.now().isoformat()
        
    except Exception as e:
        processing_status[job_id]["status"] = "error"
        processing_status[job_id]["error"] = str(e)
        processing_status[job_id]["completed_at"] = datetime.now().isoformat()


@app.route('/api/batch', methods=['POST'])
def process_batch_news():
    """Endpoint para processar múltiplas notícias de forma assíncrona"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Dados não fornecidos"
            }), 400
        
        # Aceita tanto 'topics' quanto 'topicos'
        topics_list = data.get('topics', data.get('topicos', []))
        
        if not topics_list:
            return jsonify({
                "success": False,
                "error": "Lista de tópicos não fornecida ou vazia"
            }), 400
        
        # Limita o número de tópicos
        topics_list = topics_list[:20]  # Máximo 20 tópicos
        
        # Gera ID único para o job
        job_id = f"batch_{int(time.time())}_{len(topics_list)}"
        
        # Inicia processamento em thread separada
        thread = threading.Thread(
            target=process_batch_async,
            args=(topics_list, job_id)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "success": True,
            "job_id": job_id,
            "message": "Processamento iniciado",
            "topics_count": len(topics_list),
            "status_url": f"/api/status/{job_id}",
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500


@app.route('/api/status/<job_id>', methods=['GET'])
def get_batch_status(job_id):
    """Endpoint para verificar status do processamento em lote"""
    if job_id not in processing_status:
        return jsonify({
            "success": False,
            "error": "Job ID não encontrado"
        }), 404
    
    status = processing_status[job_id].copy()
    status['success'] = True
    status['timestamp'] = datetime.now().isoformat()
    
    return jsonify(status)


@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """Endpoint para limpar cache de notícias"""
    global news_cache
    cache_size = len(news_cache)
    news_cache.clear()
    
    return jsonify({
        "success": True,
        "message": f"Cache limpo: {cache_size} itens removidos",
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/cache/status', methods=['GET'])
def cache_status():
    """Endpoint para verificar status do cache"""
    return jsonify({
        "success": True,
        "cache_size": len(news_cache),
        "processing_jobs": len(processing_status),
        "timestamp": datetime.now().isoformat()
    })


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint não encontrado",
        "timestamp": datetime.now().isoformat()
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "Erro interno do servidor",
        "timestamp": datetime.now().isoformat()
    }), 500


if __name__ == '__main__':
    print("🚀 Iniciando Sistema de Notícias Flask API...")
    print("📍 Endpoints disponíveis:")
    print("   GET  /api/topics - Buscar tópicos em alta")
    print("   GET  /api/news/<topic> - Processar notícia específica")
    print("   POST /api/news - Processar notícia via JSON")
    print("   POST /api/batch - Processar múltiplas notícias")
    print("   GET  /api/status/<job_id> - Status do processamento")
    print("   POST /api/cache/clear - Limpar cache")
    print("   GET  /api/cache/status - Status do cache")
    
    app.run(debug=True, host='0.0.0.0', port=5000)