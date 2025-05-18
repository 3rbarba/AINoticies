import time
from google.adk.agents import Agent
from google.adk.tools import google_search
from utils import call_agent

def pesquisar_ultimas_noticias(topico, categoria):
    """Pesquisa as últimas notícias relevantes sobre um tópico usando um Agente com busca do Google."""
    buscador_noticias = Agent(
        name="agente_pesquisador_noticias",
        model="gemini-2.0-flash",
        instruction=f"""
            Você é um especialista em pesquisa de notícias. Sua tarefa é usar a ferramenta de busca do google (google_search)
            para encontrar as 3 notícias mais relevantes e publicadas nos últimos 7 dias sobre o tópico: '{topico}' categoria: '{categoria}'.
            Se não encontrar notícias nas últimas 24 horas, considere até a última semana.
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
              Data: [Data da noticia]
        """,
        description="Agente que pesquisa notícias relevantes sobre um tópico.",
        tools=[google_search]
    )

    entrada_do_agente = f"Tópico: {topico}, Categoria: {categoria}"
    resposta_do_agente = call_agent(buscador_noticias, entrada_do_agente)
    print("Resposta do Agente Pesquisador de Notícias:")
    print(resposta_do_agente)

    time.sleep(4) # Adicionando a pausa DENTRO da função

    noticias = []
    if resposta_do_agente:
        if "- Título:" in resposta_do_agente:
            partes = resposta_do_agente.strip().split('\n- Título:')
            for parte in partes[1:]:
                detalhes = parte.strip().split('\n  Fonte:')
                if len(detalhes) == 2:
                    titulo = detalhes[0].strip()
                    fonte_resumo = detalhes[1].strip().split('\n  Resumo:')
                    if len(fonte_resumo) == 2:
                        fonte = fonte_resumo[0].strip()
                        resumo_data = fonte_resumo[1].strip().split('\n  Data:')
                        resumo = resumo_data[0].strip()
                        data = resumo_data[1].strip() if len(resumo_data) > 1 else "Data não disponível"
                        noticias.append({'título': titulo, 'fonte': fonte, 'resumo': resumo, 'data': data})
        else:
            linhas = resposta_do_agente.strip().split('\n')
            titulo_atual = fonte_atual = resumo_atual = data_atual = ""

            for linha in linhas:
                linha = linha.strip()
                if linha.startswith("Título:") or linha.startswith("- Título:"):
                    if titulo_atual:
                        if resumo_atual:
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
