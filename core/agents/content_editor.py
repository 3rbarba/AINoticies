from google.adk.agents import Agent
from utils import call_agent

def editar_conteudo(noticias):
    """Resumi os fatos apurados, criando título, chamada e resumo usando um Agente.

    Args:
        noticias (list): Uma lista de dicionários, onde cada dicionário representa uma notícia.

    Returns:
        dict: Um dicionário contendo o conteúdo editado (título, chamada, resumo, etc.).
              Retorna um dicionário vazio se a edição falhar.
    """

    editor_conteudo = Agent(
        name="agente_editor_conteudo",
        model="gemini-2.0-flash",
        instruction="""
            Você é um editor de notícias experiente. Dada uma lista de notícias com título, fonte e resumo,
            sua tarefa é gerar para a primeira notícia da lista:
            - Um título principal chamativo e informativo (máximo 10 palavras).
            - Uma breve chamada de capa (máximo 20 palavras) que atraia o leitor.
            - Um resumo conciso do conteúdo (máximo 50 palavras).
            - Até 3 palavras-chave relevantes para uma imagem.
            - Uma emoção desejada para a imagem (ex: neutro, positivo, alerta).
            - Verificar a data da notícia.
            Formato de saída desejado:
            Título: [título]
            Chamada de Capa: [chamada]
            Resumo: [resumo]
            Palavras-chave para imagem: [palavras-chave]
            Emoção desejada para imagem: [emoção]
            Data: [Data-noticia]
        """,
        description="Agente que edita e resume notícias.",
        tools=[]  # Este agente não precisa de ferramentas externas
    )

    conteudo_editado = {}
    if noticias:
        primeira_noticia = noticias[0]
        entrada_do_agente = f"""
            Título: {primeira_noticia.get('título', '')}
            Fonte: {primeira_noticia.get('fonte', '')}
            Resumo: {primeira_noticia.get('resumo', '')}
            Data: {primeira_noticia.get('data', '')}
        """
        resposta_do_agente = call_agent(editor_conteudo, entrada_do_agente)
        print("Resposta do Agente Editor de Conteúdo:")
        print(resposta_do_agente)

        if resposta_do_agente:
            for linha in resposta_do_agente.split('\n'):
                linha = linha.strip()
                if ':' in linha:
                    chave, valor = linha.split(':', 1)
                    chave = chave.strip()
                    valor = valor.strip()
                    if chave:
                        conteudo_editado[chave] = valor
                        if chave == 'Palavras-chave para imagem':
                            conteudo_editado['palavras_chave_imagem'] = [p.strip() for p in valor.split(',')]

    # Preencher valores padrão para campos ausentes
    campos_necessarios = ['Título', 'Chamada de Capa', 'Resumo', 'Palavras-chave para imagem', 'Emoção desejada para imagem', 'Data']
    for campo in campos_necessarios:
        if campo not in conteudo_editado:
            if noticias:  # Verifica se noticias não está vazio antes de acessar o índice
                primeira_noticia = noticias[0]
                if campo == 'Título':
                    conteudo_editado[campo] = primeira_noticia.get('título', "Título não disponível")
                elif campo == 'Chamada de Capa':
                    conteudo_editado[campo] = "Nova notícia sobre " + primeira_noticia.get('título', "este tópico")
                elif campo == 'Resumo':
                    conteudo_editado[campo] = primeira_noticia.get('resumo', "")[:50] + "..."
                elif campo == 'Palavras-chave para imagem':
                    conteudo_editado[campo] = ["notícia", "atualidade"]
                elif campo == 'Emoção desejada para imagem':
                    conteudo_editado[campo] = "neutro"
                elif campo == 'Data':
                    conteudo_editado[campo] = primeira_noticia.get('data', "Data não disponível")
            else:
                conteudo_editado[campo] = "Valor padrão não disponível"  # Se noticias estiver vazio
    return conteudo_editado