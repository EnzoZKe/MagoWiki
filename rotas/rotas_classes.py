from flask import Blueprint, request, render_template, redirect, url_for, session
from conexao import criar_conexao, fechar_conexao
from psycopg2.extras import RealDictCursor

classes_bp = Blueprint('classes', __name__)

@classes_bp.route('/listar_classes', methods=['GET'])
def listar_classe():

    PESQUISAR = request.args.get('PESQUISAR', "")

    conn = criar_conexao()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    if not PESQUISAR:

        cursor.execute("""SELECT * FROM CLASSES""")
        classes = cursor.fetchall()
    
    else:
        cursor.execute("""SELECT * FROM CLASSES WHERE nome_classe like %s""", ('%' + PESQUISAR + '%',))
        classes = cursor.fetchall()

    cursor.close()
    fechar_conexao(conn)
    return render_template('ver_classes.html', classes = classes)

@classes_bp.route('/novaclasse', methods=['GET', 'POST'])
def criar_classe():
    #validação se meu usuario esta na sessão
    if 'usuario' not in session:
        return redirect(url_for('usuarios.login_usuario'))
    conn = criar_conexao()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    if request.method == 'POST':
        NOME_CLASSE = request.form['NOME_CLASSE'] #1
        DESCRICAO_CLASSE = request.form['DESCRICAO_CLASSE']
        ID_USUARIO = session.get('usuario')['id_usuario']
        
        cursor.execute('INSERT INTO CLASSES(nome_classe, id_usuario, descricao_classe)'
                       "VALUES(%s, %s, %s)", (NOME_CLASSE, ID_USUARIO, DESCRICAO_CLASSE))
        
        conn.commit()
        cursor.close()
        fechar_conexao(conn)
        return redirect(url_for('classes.criar_classe'), )
    
    return render_template('criar_classe.html')

@classes_bp.route('/listar_suas_classes', methods=['GET'])
def listar_suas_classes():
    if 'usuario' not in session or 'id_usuario' not in session['usuario']:
        return redirect(url_for('usuarios.login_usuario'))

    PESQUISAR = request.args.get('PESQUISAR', "")
    page = request.args.get('page', 1, type=int)
    per_page = 5  # Número de registros por página (ajuste conforme necessário)

    offset = (page - 1) * per_page  # Calcula o offset para a consulta SQL
    
    ID_USUARIO = session.get('usuario')['id_usuario']
    
    conn = criar_conexao()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    if not PESQUISAR:
        # Query para listar as classes do usuário logado sem filtro de pesquisa
        cursor.execute("""
            SELECT *
            FROM CLASSES
            WHERE ID_USUARIO = %s
            LIMIT %s OFFSET %s;
        """, (ID_USUARIO, per_page, offset))
        
        classes = cursor.fetchall()  # Correção: Usar 'classes' em vez de 'classses'

        # Pega o número total de registros para calcular o total de páginas
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM CLASSES
            WHERE ID_USUARIO = %s
        """, (ID_USUARIO,))
        total_classes = cursor.fetchone()['total']

        total_pages = (total_classes + per_page - 1) // per_page  # Total de páginas

    else:
        # Query com filtro de pesquisa
        cursor.execute("""
            SELECT *
            FROM CLASSES
            WHERE NOME_CLASSE LIKE %s AND ID_USUARIO = %s
            LIMIT %s OFFSET %s;
        """, ('%' + PESQUISAR + '%', ID_USUARIO, per_page, offset))
        
        classes = cursor.fetchall()  # Correção aqui também

        # Pega o número total de registros filtrados
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM CLASSES
            WHERE NOME_CLASSE LIKE %s AND ID_USUARIO = %s
        """, ('%' + PESQUISAR + '%', ID_USUARIO))
        total_classes = cursor.fetchone()['total']

        total_pages = (total_classes + per_page - 1) // per_page  # Total de páginas

    cursor.close()
    fechar_conexao(conn)

    # Corrigir o retorno para passar 'classes' corretamente
    return render_template('suas_classes.html', classes=classes, page=page, total_pages=total_pages)

@classes_bp.route('/excluir/<int:id>', methods=['GET'])
def excluir_classe(id):
    conn = criar_conexao()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    ID_USUARIO = session.get('usuario')['id_usuario']

    cursor.execute("DELETE FROM CLASSES WHERE ID_CLASSE = %s AND ID_USUARIO =%s", (id, ID_USUARIO))

    conn.commit()
    cursor.close()
    fechar_conexao(conn)
    return redirect(url_for('classes.listar_classe'))

@classes_bp.route('/alterar/<int:id>', methods=['GET', 'POST'])
def atualizar_classe(id):
    conn = criar_conexao()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    if request.method == 'POST':
        # Se o metodo for post, significa que o formulario de alteração foi submetido

        # Coleta os dados que o usuario enviou
        NOME_CLASSE = request.form['NOME_CLASSE'] #1
        DESCRICAO_CLASSE = request.form['DESCRICAO_CLASSE'] #2

        # Executa o comando SQL
        cursor.execute(""" UPDATE CLASSES
                       SET NOME_CLASSE = %s, DESCRICAO_CLASSE = %s WHERE ID_CLASSE = %s 
                        """, (NOME_CLASSE, DESCRICAO_CLASSE,id))
        conn.commit()

        cursor.close()
        fechar_conexao(conn)

        return redirect(url_for('classes.listar_classe'))
    
    # Se o metodo for get, busca e preenche os dados do livro
    cursor.execute("SELECT * FROM CLASSES WHERE ID_CLASSE = %s ", (id,))
    classe = cursor.fetchone()

    cursor.close()
    fechar_conexao(conn)

    return render_template('alterar_classe.html', classe=classe)