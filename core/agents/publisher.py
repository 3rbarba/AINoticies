def publicar_noticia(noticia_final):
    """Simula a publicação da notícia.

    Args:
        noticia_final (dict): Um dicionário contendo os detalhes da notícia a ser publicada.

    Returns:
        bool: True se a publicação for bem-sucedida, False caso contrário.
    """
    if noticia_final:
        print("\n--- NOVO ARTIGO ---")
        print(f"Título: {noticia_final.get('Título', '')}")
        print(f"Chamada: {noticia_final.get('Chamada', '')}")
        print(f"Texto Completo: {noticia_final.get('Notícia Completa', '')}")
        print(f"Fonte: {noticia_final.get('fonte', 'Desconhecida')}")
        print(f"Resumo: {noticia_final.get('Resumo', '')}")
        print(f"Categoria: {noticia_final.get('categoria', 'A DEFINIR')}")
        print(f"URL da Imagem: {noticia_final.get('URL da Imagem', 'URL_IMAGEM_PLACEHOLDER')}")
        print("--- FIM DO ARTIGO ---\n")
        return True
    return False