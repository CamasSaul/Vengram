import os
import sqlite3
import argparse

from datetime import datetime
from rich import print


TABLE_THOUGHT = 'thought'
TABLE_TAG = 'tag'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQL_SCHEMA_PATH = os.path.join(BASE_DIR, 'vengram.sql')
DB_PATH = os.path.join(BASE_DIR, 'vengram.db')



def connect_db():
    if not os.path.exists(DB_PATH):
        with sqlite3.connect(DB_PATH) as conn:
            with open(SQL_SCHEMA_PATH) as f:
                conn.cursor().executescript(f.read())
    
    with sqlite3.connect(DB_PATH) as conn:
        return conn


def insert(table:str, kargs:dict):
    '''Recive los datos a insertar como diccionario; columna-valor'''
    # Conecta a la db
    conn = connect_db()
    cursor = conn.cursor()
    # Construye la query
    query = f'INSERT INTO {table} '
    query += str(list(str(key) for key in list(kargs.keys()))).replace('[','(').replace(']',')')
    query += ' VALUES ' + str(tuple('?' for _ in range(len(kargs)))).replace('\'', '').replace(',)', ')')
    # Ejecuta la query
    print(query)
    cursor.execute(query, list(kargs.values()))
    conn.commit()


def select(table):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM {table}')
    rows = cursor.fetchall()
    return rows


def update(id_item, nuevo_nombre):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE items SET nombre = ? WHERE id = ?", (nuevo_nombre, id_item))
    conn.commit()
    print(f"[bold yellow]⚠ Item {id_item} actualizado a '{nuevo_nombre}'.[/bold yellow]")


def delete(id_item):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM items WHERE id = ?", (id_item,))
    conn.commit()
    print(f"[bold red]✘ Item {id_item} eliminado.[/bold red]")



def search_tags (thought:str):
    """Encuentra posibles tags para un texto dado"""
    saved_tags = select(TABLE_TAG) # expected: <list>[ (id, name), (id, name), ... ]
    tags_founded = []
    thought = thought.lower()
    print(saved_tags)
    for tag in saved_tags:
        tag = tag[1] # the second value is the name of tag
        if tag in thought:
            tags_founded.append(tag)
    return ' '.join(tags_founded)




def main ():
    # Obtener argumentos
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--add-tags",
        nargs='*',
    )
    # Procesar argumentos
    args = parser.parse_args().add_tags

    if args:
        for arg in args:
            insert(TABLE_TAG, {'name':arg})
        return

    print('[bold]Thought: [/bold]', end='')
    thought = input()
    tags = search_tags(thought)



    insert(TABLE_THOUGHT, {'tags':tags, 'content':thought, 'timestamp':datetime.now().isoformat()})
    print(select(TABLE_THOUGHT))