from google.adk.agents import Agent
from google.adk.tools import google_search
from utils import call_agent

def pesquisar_noticias(topico, categoria):
    """Pesquisa as notícias relevantes sobre um tópico usando um Agente com busca do Google.

    Args:
        topico (str): O tópico da notícia a ser pesquisada.
        categoria (str): A categoria da notícia.

    Returns:
        list: Uma lista de dicionários, onde cada dicionário representa uma notícia
              e contém as chaves 'título', 'fonte', 'resumo' e 'data'.
              Retorna uma lista vazia se nenhuma notícia for encontrada.
    """

    buscador_noticias = Agent(
        name="agente_pesquisador_noticias",
        model="gemini-2.0-flash",
        instruction=f"""
            Você é um especialista em pesquisa de notícias. Sua tarefa é usar a ferramenta de busca do Google (google_search)
            para encontrar as 3 notícias mais relevantes e publicadas no último mês sobre o tópico: '{topico}' categoria: '{categoria}'.
            Se não encontrar notícias no último mês, considere estender a busca para um período um pouco maior, se necessário.
            Para cada notícia, apresente o título, um breve resumo e a fonte.
            Priorize fontes confiáveis e atuais. Se você não encontrar notícias relevantes sobre o topico informado, passe para o próximo tópico. até
            encontrar uma noticia valida
            Garanta que a noticia tenha uma data
            Formato de entrada:
            Tópico: [tópico]
            Categoria: [categoria]
            Formato de saída desejado para cada notícia:
            - Título: [título da notícia]
              Fonte: [nome da fonte]
              Resumo: [breve resumo da notícia]
              Data: [Data da notícia]
        """,
        description="Agente que pesquisa notícias relevantes sobre um tópico.",
        tools=[google_search]
    )

    entrada = f"Tópico: {topico}\nCategoria: {categoria}"
    resposta_do_agente = call_agent(buscador_noticias, entrada)
    print("Resposta do Agente Pesquisador de Notícias:")
    print(resposta_do_agente)

    noticias = []
    if resposta_do_agente:
        linhas = resposta_do_agente.split('\n')
        titulo_atual = fonte_atual = resumo_atual = data_atual = ""

        for linha in linhas:
            linha = linha.strip()
            if linha.startswith("Título:") or linha.startswith("- Título:"):
                if titulo_atual and resumo_atual:
                    noticias.append({
                        'título': titulo_atual,
                        'fonte': fonte_atual or "Desconhecida",
                        'resumo': resumo_atual,
                        'data': data_atual or "Data não disponível"
                    })
                titulo_atual = linha.replace("Título:", "").replace("- Título:", "").strip()
                fonte_atual = resumo_atual = data_atual = ""

            elif linha.startswith("Fonte:") or linha.startswith("  Fonte:"):
                fonte_atual = linha.replace("Fonte:", "").replace("  Fonte:", "").strip()

            elif linha.startswith("Resumo:") or linha.startswith("  Resumo:"):
                resumo_atual = linha.replace("Resumo:", "").replace("  Resumo:", "").strip()

            elif linha.startswith("Data:") or linha.startswith("  Data:"):
                data_atual = linha.replace("Data:", "").replace("  Data:", "").strip()

        if titulo_atual and resumo_atual:
            noticias.append({
                'título': titulo_atual,
                'fonte': fonte_atual or "Desconhecida",
                'resumo': resumo_atual,
                'data': data_atual or "Data não disponível"
            })
    return noticias