from datetime import date
from google.adk.agents import Agent
from google.adk.tools import google_search
from utils import call_agent

def identificar_topicos_em_alta():
    """Identifica os tópicos mais relevantes da semana usando um Agente com busca do Google.

    Returns:
        list: Uma lista de dicionários, onde cada dicionário contém as chaves 'tópico' e 'categoria'.
              Retorna uma lista vazia se nenhum tópico for encontrado.
    """

    buscador = Agent(
        name="agente_buscador_topicos",
        model="gemini-2.0-flash",
        instruction="""
            Você é um assistente de pesquisa de tendências. A sua tarefa é usar a ferramenta de busca do Google (google_search)
            para identificar os 50 tópicos mais relevantes e comentados da semana.
            Organize os tópicos por ordem de relevância e atualidade, com base na quantidade e no entusiasmo das notícias e discussões sobre eles.
            Filtre temas sensíveis ou potencialmente ofensivos.
            Para cada tópico, tente identificar sua categoria principal.
            Formato de saída desejado:
            [Número]. **[Tópico]** (Categoria: [categoria]): [Informações adicionais]
        """,
        description="Agente que busca os tópicos em alta no Google e os categoriza.",
        tools=[google_search]
    )

    hoje = date.today().strftime("%Y-%m-%d")
    entrada_do_agente_buscador = f"Data de hoje: {hoje}"

    resposta_do_buscador = call_agent(buscador, entrada_do_agente_buscador)
    print("Resposta do Agente Buscador de Tópicos:")
    print(resposta_do_buscador)

    topicos_com_categoria = []
    if resposta_do_buscador:
        for linha in resposta_do_buscador.split('\n'):
            linha = linha.strip()
            if linha.startswith(tuple(f"{i}. **" for i in range(1, 51))):
                partes_topico = linha.split('**')
                if len(partes_topico) > 1:
                    topico = partes_topico[1].strip()
                    categoria = "A DEFINIR"  # Valor padrão para categoria
                    if len(partes_topico) > 2:
                        categoria_texto = partes_topico[2].strip()
                        inicio = categoria_texto.find('(')
                        fim = categoria_texto.find(')')
                        if inicio != -1 and fim != -1 and inicio < fim:
                            categoria = categoria_texto[inicio + 1:fim - 1].strip()  # Extrai a categoria sem os parênteses
                    topicos_com_categoria.append({'tópico': topico, 'categoria': categoria})
    print("Tópicos identificados:")
    for topico in topicos_com_categoria:
        print(topico)
    return topicos_com_categoria