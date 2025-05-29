import time
import traceback
from google.genai import errors as genai_errors
from google.genai import types
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from config import MAX_RETRIES, INITIAL_BACKOFF

def call_agent(agent: Agent, message_text: str) -> str:
    """
    Envia uma mensagem para um agente via Runner com lógica de retentativa exponencial.
    
    Args:
        agent (Agent): Instância do agente ADK.
        message_text (str): Texto da mensagem a ser enviada ao agente.
    
    Returns:
        str: Resposta final do agente.
    
    Raises:
        Exception: Se exceder o número máximo de tentativas ou ocorrer erro inesperado.
    """
    session_service = InMemorySessionService()
    session = session_service.create_session(app_name=agent.name, user_id="user1", session_id="session1")
    runner = Runner(agent=agent, app_name=agent.name, session_service=session_service)
    content = types.Content(role="user", parts=[types.Part(text=message_text)])

    final_response = ""
    retries = 0
    while retries < MAX_RETRIES:
        try:
            for event in runner.run(user_id="user1", session_id="session1", new_message=content):
                if event.is_final_response():
                    for part in event.content.parts:
                        if part.text is not None:
                            final_response += part.text
                            final_response += "\n"
            return final_response
        except genai_errors.ServerError as e:
            print(f"Erro de servidor ao chamar o agente '{agent.name}': {e}")
            retries += 1
            backoff_time = INITIAL_BACKOFF * (2 ** (retries - 1))
            print(f"Retentando em {backoff_time} segundos...")
            time.sleep(backoff_time)
        except Exception as e:
            print(f"Erro inesperado ao chamar o agente '{agent.name}': {e}")
            raise  # Relevanta outras exceções
    raise Exception(f"Falha ao chamar o agente '{agent.name}' após {MAX_RETRIES} tentativas.")