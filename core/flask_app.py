import requests
import json
import time
from datetime import datetime


class NewsAPIClient:
    """Cliente para interagir com a API de Notícias Flask"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'NewsAPI-Client/1.0'
        })
    
    def get_trending_topics(self, limit=10):
        """Busca tópicos em alta"""
        try:
            response = self.session.get(f"{self.base_url}/api/topics?limit={limit}")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def process_single_news(self, topic, categoria="Geral"):
        """Processa uma notícia específica"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/news/{topic}?categoria={categoria}"
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def process_news_post(self, topico, categoria="Geral"):
        """Processa notícia via POST"""
        try:
            data = {"topico": topico, "categoria": categoria}
            response = self.session.post(f"{self.base_url}/api/news", json=data)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def process_batch_news(self, topics_list):
        """Processa múltiplas notícias em lote"""
        try:
            data = {"topics": topics_list}
            response = self.session.post(f"{self.base_url}/api/batch", json=data)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_batch_status(self, job_id):
        """Verifica status do processamento em lote"""
        try:
            response = self.session.get(f"{self.base_url}/api/status/{job_id}")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def wait_for_batch_completion(self, job_id, max_wait=300):
        """Aguarda conclusão do processamento em lote"""
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            status = self.get_batch_status(job_id)
            
            if status.get("status") == "completed":
                return status
            elif status.get("status") == "error":
                return status
            
            print(f"Progresso: {status.get('progress', 0)}/{status.get('total', 0)}")
            time.sleep(5)
        
        return {"error": "Timeout aguardando conclusão"}
    
    def clear_cache(self):
        """Limpa o cache da API"""
        try:
            response = self.session.post(f"{self.base_url}/api/cache/clear")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_cache_status(self):
        """Verifica status do cache"""
        try:
            response = self.session.get(f"{self.base_url}/api/cache/status")
            return response.json()
        except Exception as e:
            return {"error": str(e)}


def exemplo_uso_completo():
    """Exemplo completo de uso da API"""
    
    print("🚀 Iniciando cliente da API de Notícias")
    client = NewsAPIClient()
    
    # 1. Buscar tópicos em alta
    print("\n📈 Buscando tópicos em alta...")
    topics_response = client.get_trending_topics(limit=5)
    
    if topics_response.get("success"):
        topics = topics_response["topics"]
        print(f"✅ Encontrados {len(topics)} tópicos:")
        for i, topic in enumerate(topics, 1):
            print(f"   {i}. {topic['topico']} ({topic['categoria']})")
    else:
        print("❌ Erro ao buscar tópicos:", topics_response.get("error"))
        return
    
    # 2. Processar notícia individual
    if topics:
        print(f"\n📰 Processando notícia sobre: {topics[0]['topico']}")
        news_response = client.process_single_news(
            topics[0]['topico'], 
            topics[0]['categoria']
        )
        
        if news_response.get("noticia"):
            noticia = news_response["noticia"]
            print("✅ Notícia processada com sucesso!")
            print(f"   Título: {noticia.get('titulo', 'N/A')}")
            print(f"   Data: {noticia.get('data', 'N/A')}")
            print(f"   Fonte: {noticia.get('fonte', 'N/A')[:100]}...")
            print(f"   Preview: {noticia.get('noticia_completa', 'N/A')[:200]}...")
        else:
            print("❌ Erro ao processar notícia:", news_response.get("status"))
    
    # 3. Processamento em lote
    if len(topics) > 1:
        print(f"\n📦 Iniciando processamento em lote de {min(3, len(topics))} notícias...")
        batch_topics = topics[:3]  # Primeiros 3 tópicos
        
        batch_response = client.process_batch_news(batch_topics)
        
        if batch_response.get("success"):
            job_id = batch_response["job_id"]
            print(f"✅ Job iniciado: {job_id}")
            
            # Aguarda conclusão
            print("⏳ Aguardando conclusão...")
            final_status = client.wait_for_batch_completion(job_id)
            
            if final_status.get("status") == "completed":
                results = final_status.get("results", [])
                print(f"✅ Processamento concluído! {len(results)} notícias processadas:")
                
                for i, result in enumerate(results, 1):
                    if result.get("noticia"):
                        noticia = result["noticia"]
                        print(f"   {i}. {noticia.get('titulo', 'Sem título')}")
            else:
                print("❌ Erro no processamento em lote:", final_status.get("error"))
        else:
            print("❌ Erro ao iniciar lote:", batch_response.get("error"))
    
    # 4. Status do cache
    print("\n💾 Verificando status do cache...")
    cache_status = client.get_cache_status()
    if cache_status.get("success"):
        print(f"   Cache size: {cache_status['cache_size']} itens")
        print(f"   Jobs ativos: {cache_status['processing_jobs']}")
    
    print("\n🎉 Exemplo concluído!")


def exemplo_requests_diretos():
    """Exemplos usando requests diretamente"""
    base_url = "http://localhost:5000"
    
    print("🔧 Exemplos com requests diretos:\n")
    
    # GET tópicos
    print("1. Buscar tópicos:")
    print(f"   GET {base_url}/api/topics?limit=5")
    
    # GET notícia específica
    print("\n2. Processar notícia específica:")
    print(f"   GET {base_url}/api/news/Bitcoin?categoria=Economia")
    
    # POST notícia
    print("\n3. Processar via POST:")
    print(f"   POST {base_url}/api/news")
    print("   Body: {\"topico\": \"Inteligência Artificial\", \"categoria\": \"Tecnologia\"}")
    
    # POST lote
    print("\n4. Processamento em lote:")
    print(f"   POST {base_url}/api/batch")
    print("   Body: {\"topics\": [{\"topico\": \"ChatGPT\", \"categoria\": \"IA\"}, {\"topico\": \"Tesla\", \"categoria\": \"Carros\"}]}")
    
    # GET status
    print("\n5. Verificar status do lote:")
    print(f"   GET {base_url}/api/status/{{job_id}}")
    
    # Cache
    print("\n6. Gerenciar cache:")
    print(f"   GET {base_url}/api/cache/status")
    print(f"   POST {base_url}/api/cache/clear")


def exemplo_curl_commands():
    """Gera comandos curl para teste"""
    base_url = "http://localhost:5000"
    
    print("🖥️  Comandos cURL para teste:\n")
    
    print("# Buscar tópicos em alta")
    print(f"curl -X GET \"{base_url}/api/topics?limit=5\"\n")
    
    print("# Processar notícia específica")
    print(f"curl -X GET \"{base_url}/api/news/Bitcoin?categoria=Economia\"\n")
    
    print("# Processar via POST")
    print(f"curl -X POST \"{base_url}/api/news\" \\")
    print("     -H \"Content-Type: application/json\" \\")
    print("     -d '{\"topico\": \"Inteligência Artificial\", \"categoria\": \"Tecnologia\"}'\n")
    
    print("# Processamento em lote")
    print(f"curl -X POST \"{base_url}/api/batch\" \\")
    print("     -H \"Content-Type: application/json\" \\")
    print("     -d '{\"topics\": [{\"topico\": \"ChatGPT\", \"categoria\": \"IA\"}, {\"topico\": \"Tesla\", \"categoria\": \"Carros\"}]}'\n")
    
    print("# Verificar status (substitua JOB_ID)")
    print(f"curl -X GET \"{base_url}/api/status/JOB_ID\"\n")
    
    print("# Limpar cache")
    print(f"curl -X POST \"{base_url}/api/cache/clear\"\n")


if __name__ == "__main__":
    print("📋 Escolha uma opção:")
    print("1. Executar exemplo completo")
    print("2. Ver exemplos de requests diretos")
    print("3. Ver comandos cURL")
    
    choice = input("\nOpção (1-3): ").strip()
    
    if choice == "1":
        exemplo_uso_completo()
    elif choice == "2":
        exemplo_requests_diretos()
    elif choice == "3":
        exemplo_curl_commands()
    else:
        print("Opção inválida!")
        exemplo_requests_diretos()
        print("\n" + "="*50)
        exemplo_curl_commands()