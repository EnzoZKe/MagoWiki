import mysql.connector

def criar_conexao():
    return mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = "admin",
        database = "magowiki"
    )

def fechar_conexao(conexao):
    if conexao:
        conexao.close()