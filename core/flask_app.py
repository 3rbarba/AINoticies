import requests
import json
import time
from datetime import datetime
import os

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
        """Processa uma notícia específica (usando GET)"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/news/{topic}?categoria={categoria}"
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def process_news_post(self, topico, categoria="Geral"):
        """Processa notícia específica (usando POST)"""
        try:
            data = {"topico": topico, "categoria": categoria}
            response = self.session.post(f"{self.base_url}/api/news", json=data)
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def get_news_by_category(self, categoria):
        """Filtra notícias por categoria"""
        try:
            response = self.session.get(f"{self.base_url}/api/news/filter?categoria={categoria}")
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def get_available_categories(self):
        """Obtém categorias disponíveis"""
        try:
            response = self.session.get(f"{self.base_url}/api/news/categorias")
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def generate_audio_from_text(self, text, voice="Zephyr", output_filename="audio_news.wav"):
        """
        Gera áudio a partir de um texto usando o endpoint Gemini TTS.
        Salva o áudio em um arquivo e retorna o nome do arquivo.
        """
        try:
            headers = {'Content-Type': 'application/json'}
            data = json.dumps({"text": text, "voice": voice})
            response = self.session.post(f"{self.base_url}/api/gemini-tts", headers=headers, data=data, stream=True)

            if response.status_code == 200:
                content_type = response.headers.get('Content-Type')
                if 'audio/' in content_type:
                    with open(output_filename, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    print(f"✅ Áudio salvo em: {output_filename}")
                    return {"success": True, "filename": output_filename, "content_type": content_type}
                else:
                    return {"success": False, "error": f"Tipo de conteúdo inesperado: {content_type}"}
            else:
                error_message = response.text
                try:
                    error_json = response.json()
                    error_message = error_json.get('error', error_message)
                except json.JSONDecodeError:
                    pass
                return {"success": False, "error": f"Erro na API TTS: {response.status_code} - {error_message}"}
        except Exception as e:
            return {"success": False, "error": str(e)}


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

    # 2. Processar notícia individual (usando GET)
    if topics:
        print(f"\n📰 Processando notícia sobre: {topics[0]['topico']} (GET)")
        news_response_get = client.process_single_news(
            topics[0]['topico'],
            topics[0]['categoria']
        )

        if news_response_get.get("noticia"):
            noticia_get = news_response_get["noticia"]
            print("✅ Notícia processada com sucesso via GET!")
            print(f"   Título: {noticia_get.get('titulo', 'N/A')}")
            print(f"   Data: {noticia_get.get('data', 'N/A')}")
            print(f"   Fonte: {noticia_get.get('fonte', 'N/A')[:100]}...")
            print(f"   Preview: {noticia_get.get('noticia_completa', 'N/A')[:200]}...")

            # Gerar áudio para a notícia completa processada via GET
            print("\n🔊 Gerando áudio da notícia processada via GET...")
            text_to_speak_get = noticia_get.get('noticia_completa', 'Conteúdo da notícia não disponível para áudio.')
            if len(text_to_speak_get) > 4000:
                print("AVISO: Notícia muito longa para TTS. Usando apenas os primeiros 4000 caracteres.")
                text_to_speak_get = text_to_speak_get[:4000]

            audio_result_get = client.generate_audio_from_text(text_to_speak_get, voice="Zephyr", output_filename="noticia_audio_get.wav")
            if audio_result_get.get("success"):
                print(f"✅ Áudio da notícia GET gerado e salvo em: {audio_result_get['filename']}")
            else:
                print("❌ Erro ao gerar áudio GET:", audio_result_get.get("error"))
        else:
            print("❌ Erro ao processar notícia via GET:", news_response_get.get("error"))

    # 3. Processar notícia individual (usando POST)
    if len(topics) > 1:
        print(f"\n📰 Processando notícia sobre: {topics[1]['topico']} (POST)")
        news_response_post = client.process_news_post(
            topics[1]['topico'],
            topics[1]['categoria']
        )

        if news_response_post.get("noticia"):
            noticia_post = news_response_post["noticia"]
            print("✅ Notícia processada com sucesso via POST!")
            print(f"   Título: {noticia_post.get('titulo', 'N/A')}")
            print(f"   Data: {noticia_post.get('data', 'N/A')}")
            print(f"   Fonte: {noticia_post.get('fonte', 'N/A')[:100]}...")
            print(f"   Preview: {noticia_post.get('noticia_completa', 'N/A')[:200]}...")

            # Gerar áudio para a notícia completa processada via POST
            print("\n🔊 Gerando áudio da notícia processada via POST...")
            text_to_speak_post = noticia_post.get('noticia_completa', 'Conteúdo da notícia não disponível para áudio.')
            if len(text_to_speak_post) > 4000:
                print("AVISO: Notícia muito longa para TTS. Usando apenas os primeiros 4000 caracteres.")
                text_to_speak_post = text_to_speak_post[:4000]

            audio_result_post = client.generate_audio_from_text(text_to_speak_post, voice="Zephyr", output_filename="noticia_audio_post.wav")
            if audio_result_post.get("success"):
                print(f"✅ Áudio da notícia POST gerado e salvo em: {audio_result_post['filename']}")
            else:
                print("❌ Erro ao gerar áudio POST:", audio_result_post.get("error"))
        else:
            print("❌ Erro ao processar notícia via POST:", news_response_post.get("error"))

    # 4. Filtrar notícias por categoria (se houver categorias)
    print("\n📚 Buscando categorias disponíveis...")
    categorias_response = client.get_available_categories()
    if categorias_response.get("success") and categorias_response["categorias"]:
        primeira_categoria = categorias_response["categorias"][0]
        print(f"✅ Categorias disponíveis: {categorias_response['categorias']}")
        print(f"\n🔍 Filtrando notícias pela categoria: '{primeira_categoria}'")
        filtered_news_response = client.get_news_by_category(primeira_categoria)
        if filtered_news_response.get("success"):
            print(f"✅ Encontradas {filtered_news_response['count']} notícias na categoria '{primeira_categoria}':")
            for i, news_item in enumerate(filtered_news_response["noticias"][:3], 1): # Mostrar apenas as 3 primeiras
                print(f"   {i}. {news_item['noticia'].get('titulo', 'Sem título')}")
        else:
            print("❌ Erro ao filtrar notícias por categoria:", filtered_news_response.get("error"))
    else:
        print("⚠️ Nenhuma categoria disponível ou erro ao buscar categorias.")

    print("\n🎉 Exemplo concluído!")


def exemplo_requests_diretos():
    """Exemplos usando requests diretamente"""
    base_url = "http://localhost:5000"

    print("🔧 Exemplos com requests diretos:\n")

    # GET tópicos
    print("1. Buscar tópicos:")
    print(f"   GET {base_url}/api/topics?limit=5")

    # GET notícia específica
    print("\n2. Processar notícia específica (via GET):")
    print(f"   GET {base_url}/api/news/Bitcoin?categoria=Economia")

    # POST notícia
    print("\n3. Processar notícia específica (via POST):")
    print(f"   POST {base_url}/api/news")
    print("   Body: {\"topico\": \"Inteligência Artificial\", \"categoria\": \"Tecnologia\"}")

    # GET filtrar por categoria
    print("\n4. Filtrar notícias por categoria:")
    print(f"   GET {base_url}/api/news/filter?categoria=Tecnologia")

    # GET categorias disponíveis
    print("\n5. Obter categorias disponíveis:")
    print(f"   GET {base_url}/api/news/categorias")

    # POST Gemini TTS
    print("\n6. Gerar áudio a partir de texto (Gemini TTS):")
    print(f"   POST {base_url}/api/gemini-tts")
    print("   Headers: {'Content-Type': 'application/json'}")
    print("   Body: {\"text\": \"Olá, esta é uma notícia de teste.\", \"voice\": \"Zephyr\"}")


def exemplo_curl_commands():
    """Gera comandos curl para teste"""
    base_url = "http://localhost:5000"

    print("🖥️  Comandos cURL para teste:\n")

    print("# Buscar tópicos em alta")
    print(f"curl -X GET \"{base_url}/api/topics?limit=5\"\n")

    print("# Processar notícia específica (via GET)")
    print(f"curl -X GET \"{base_url}/api/news/Bitcoin?categoria=Economia\"\n")

    print("# Processar notícia específica (via POST)")
    print(f"curl -X POST \"{base_url}/api/news\" \\")
    print("     -H \"Content-Type: application/json\" \\")
    print("     -d '{\"topico\": \"Inteligência Artificial\", \"categoria\": \"Tecnologia\"}'\n")

    print("# Filtrar notícias por categoria")
    print(f"curl -X GET \"{base_url}/api/news/filter?categoria=Tecnologia\"\n")

    print("# Obter categorias disponíveis")
    print(f"curl -X GET \"{base_url}/api/news/categorias\"\n")

    print("# Gerar áudio a partir de texto (Gemini TTS)")
    print(f"curl -X POST \"{base_url}/api/gemini-tts\" \\")
    print("     -H \"Content-Type: application/json\" \\")
    print("     -d '{\"text\": \"Olá, esta é uma notícia de teste para a API Gemini TTS.\", \"voice\": \"Zephyr\"}' --output noticia_teste.wav\n")


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