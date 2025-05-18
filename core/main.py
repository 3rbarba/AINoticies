# Exemplo de uso em main.py
from agents.news_searcher import pesquisar_noticias
import json

def main():
    topico = "Tecnologia"
    categoria = "Inovação"
    noticias_json = pesquisar_noticias(topico, categoria)
    noticias = json.loads(noticias_json)

    if noticias:  # Verifica se há notícias antes de tentar acessá-las
        for noticia in noticias:
            print(f"Título: {noticia['título']}")
            print(f"Fonte: {noticia['fonte']}")
            print(f"Resumo: {noticia['resumo']}")
            print(f"Data: {noticia['data']}")
            print("-" * 20)
    else:
        print("Nenhuma notícia encontrada.")

if __name__ == "__main__":
    main()