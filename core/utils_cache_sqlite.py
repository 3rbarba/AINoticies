import sqlite3
import json
from datetime import datetime

DB_PATH = "cache.db"

def init_cache_db():
    """
    Inicializa o banco de dados SQLite para cache de notícias.
    Cria a tabela 'cache_noticias' se não existir, incluindo colunas para dados de áudio e tipo MIME.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Adicionando a coluna 'audio_data' para armazenar o áudio em BLOB
    # e 'audio_mime_type' para o tipo MIME do áudio.
    c.execute("""
        CREATE TABLE IF NOT EXISTS cache_noticias (
            topico TEXT NOT NULL,
            categoria TEXT NOT NULL,
            noticia TEXT NOT NULL,
            audio_data BLOB,           -- Nova coluna para dados de áudio
            audio_mime_type TEXT,      -- Nova coluna para tipo MIME do áudio
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (topico, categoria)
        );
    """)
    conn.commit()
    conn.close()

def get_db_connection():
    """
    Cria e retorna uma conexão com o banco de dados SQLite.
    Define o row_factory para sqlite3.Row para acesso por nome às colunas.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_cached_news(topico, categoria):
    """
    Recupera uma notícia do cache com base no tópico e categoria.
    Retorna um dicionário com a notícia, dados de áudio e tipo MIME, ou None se não encontrado.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    # Seleciona também os dados de áudio e tipo MIME
    cur.execute("SELECT noticia, audio_data, audio_mime_type FROM cache_noticias WHERE topico = ? AND categoria = ?", (topico, categoria))
    row = cur.fetchone()
    conn.close()
    if row:
        return {
            "noticia": json.loads(row["noticia"]),
            "audio_data": row["audio_data"],
            "audio_mime_type": row["audio_mime_type"]
        }
    return None

def save_news_to_cache(topico, categoria, noticia_dict, audio_data=None, audio_mime_type=None):
    """
    Salva ou atualiza uma notícia no cache.
    Armazena o dicionário da notícia, dados de áudio (opcional) e tipo MIME (opcional).
    """
    conn = get_db_connection()
    cur = conn.cursor()
    # Insere ou substitui a notícia, incluindo os dados de áudio e tipo MIME
    cur.execute(
        "REPLACE INTO cache_noticias (topico, categoria, noticia, audio_data, audio_mime_type) VALUES (?, ?, ?, ?, ?)",
        (topico, categoria, json.dumps(noticia_dict), audio_data, audio_mime_type)
    )
    conn.commit()
    conn.close()

def get_latest_news_by_title(title_part, limit=1):
    """
    Busca as notícias mais recentes cujo título contenha o texto especificado.
    Retorna uma lista de dicionários com informações da notícia, áudio, tipo MIME e data de criação.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    # Busca notícias que contenham 'title_part' no título, ordenadas pela mais recente
    # Adicionamos 'audio_data' e 'audio_mime_type' na seleção
    cur.execute(
        "SELECT topico, categoria, noticia, audio_data, audio_mime_type, created_at FROM cache_noticias WHERE noticia LIKE ? ORDER BY created_at DESC LIMIT ?",
        (f"%{title_part}%", limit)
    )
    rows = cur.fetchall()
    conn.close()
    
    results = []
    for row in rows:
        news_data = json.loads(row["noticia"])
        # Verifica se o 'titulo' está na notícia para o filtro 'LIKE'
        if title_part.lower() in news_data.get('titulo', '').lower():
            results.append({
                "topico": row["topico"],
                "categoria": row["categoria"],
                "noticia": news_data,
                "audio_data": row["audio_data"],
                "audio_mime_type": row["audio_mime_type"],
                "created_at": row["created_at"]
            })
    return results

def get_news_history(limit=10):
    """
    Retorna o histórico das notícias mais recentes do cache, limitado pelo parâmetro.
    Cada item inclui dados da notícia, áudio, tipo MIME e data de criação.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    # Busca todas as notícias, ordenadas pela mais recente, com limite
    cur.execute(
        "SELECT topico, categoria, noticia, audio_data, audio_mime_type, created_at FROM cache_noticias ORDER BY created_at DESC LIMIT ?",
        (limit,)
    )
    rows = cur.fetchall()
    conn.close()
    
    results = []
    for row in rows:
        news_data = json.loads(row["noticia"])
        results.append({
            "topico": row["topico"],
            "categoria": row["categoria"],
            "noticia": news_data,
            "audio_data": row["audio_data"],
            "audio_mime_type": row["audio_mime_type"],
            "created_at": row["created_at"]
        })
    return results