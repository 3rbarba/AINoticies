from google.adk.agents import Agent
from utils import call_agent

def editar_conteudo(noticias):
    """Resumi os fatos apurados, criando título, chamada e resumo usando um Agente."""
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
            - Verificar o a data da noticia
            Formato de saída desejado:
            Título: [título]
            Chamada de Capa: [chamada]
            Resumo: [resumo]
            Palavras-chave para imagem: [palavras-chave]
            Emoção desejada para imagem: [emoção]
            Data: [Data-noticia]
        """,
        description="Agente que edita e resume notícias.",
        tools=[] # Este agente não precisa de ferramentas externas
    )

    if noticias:
        primeira_noticia = noticias[0]
        entrada_do_agente = f"""
            Título: {primeira_noticia['título']}
            Fonte: {primeira_noticia['fonte']}
            Resumo: {primeira_noticia['resumo']}
            Data: {primeira_noticia['data']}
        """
        resposta_do_agente = call_agent(editor_conteudo, entrada_do_agente)
        print("Resposta do Agente Editor de Conteúdo:")
        print(resposta_do_agente)

        conteudo_editado = {}
        if resposta_do_agente:
            for linha in resposta_do_agente.split('\n'):
                linha = linha.strip()
                if ':' in linha:
                    partes = linha.split(':', 1)
                    if len(partes) == 2:
                        chave, valor = partes[0].strip(), partes[1].strip()
                        if chave == 'Título':
                            conteudo_editado['título'] = valor
                        elif chave == 'Chamada de Capa':
                            conteudo_editado['chamada'] = valor
                        elif chave == 'Resumo':
                            conteudo_editado['resumo'] = valor
                        elif chave == 'Palavras-chave para imagem':
                            conteudo_editado['palavras_chave_imagem'] = [p.strip() for p in valor.split(',')]
                        elif chave == 'Emoção desejada para imagem':
                            conteudo_editado['emocao_imagem'] = valor
                        elif chave == 'Data':
                            conteudo_editado['data'] = valor

        if not all(key in conteudo_editado for key in ['título', 'chamada', 'resumo', 'palavras_chave_imagem', 'emocao_imagem', 'data']):
            print("AVISO: Alguns campos estão faltando na edição. Preenchendo valores padrão.")
            if 'título' not in conteudo_editado:
                conteudo_editado['título'] = primeira_noticia['título']
            if 'chamada' not in conteudo_editado:
                conteudo_editado['chamada'] = "Nova notícia sobre " + primeira_noticia['título']
            if 'resumo' not in conteudo_editado:
                conteudo_editado['resumo'] = primeira_noticia['resumo'][:50] + "..."
            if 'palavras_chave_imagem' not in conteudo_editado:
                conteudo_editado['palavras_chave_imagem'] = ["notícia", "atualidade"]
            if 'emocao_imagem' not in conteudo_editado:
                conteudo_editado['emocao_imagem'] = "neutro"
            if 'data' not in conteudo_editado:
                conteudo_editado['data'] = primeira_noticia.get('data', 'Data não disponível')

        return conteudo_editado
    return {}
