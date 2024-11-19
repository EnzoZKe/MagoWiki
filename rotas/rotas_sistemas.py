from flask import Blueprint, request, render_template, redirect, url_for, session
from conexao import criar_conexao, fechar_conexao
from psycopg2.extras import RealDictCursor

sistemas_bp = Blueprint('sistemas', __name__)

@sistemas_bp.route('/listar_sistemas', methods=['GET'])
def listar_sistema():
    conn = criar_conexao()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute("""SELECT * FROM SISTEMAS""")
    
    sistemas = cursor.fetchall()

    cursor.close()
    fechar_conexao(conn)
    return render_template('ver_sistemas.html', sistemas = sistemas)

@sistemas_bp.route('/novosistema', methods=['GET', 'POST'])
def criar_sistema():
    #validação se meu usuario esta na sessão
    if 'usuario' not in session:
        return redirect(url_for('usuarios.login_usuario'))
    conn = criar_conexao()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    if request.method == 'POST':
        NOME_SISTEMA = request.form['NOME_SISTEMA'] #1
        ID_USUARIO = session.get('usuario')['id_usuario']
        
        cursor.execute('INSERT INTO SISTEMAS(nome_sistema, id_usuario)'
                       "VALUES(%s, %s)", (NOME_SISTEMA, ID_USUARIO))
        
        conn.commit()
        cursor.close()
        fechar_conexao(conn)
        return redirect(url_for('sistemas.criar_sistema'), )

    return render_template('criar_sistema.html')

@sistemas_bp.route('/listar_seus_sistemas', methods=['GET'])
def listar_seus_sistemas():
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
        # Query para listar sistemas do usuário logado sem filtro de pesquisa
        cursor.execute("""
            SELECT *
            FROM SISTEMAS
            WHERE ID_USUARIO = %s;
        """, (ID_USUARIO, ))
        
        sistemas = cursor.fetchall()

        # Pega o número total de registros para calcular o total de páginas
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM SISTEMAS
            WHERE ID_USUARIO = %s
        """, (ID_USUARIO,))
        total_sistemas = cursor.fetchone()['total']

        total_pages = (total_sistemas + per_page - 1) // per_page  # Total de páginas

    else:
        cursor.execute("""
            SELECT *
            FROM SISTEMAS
            WHERE NOME_SISTEMA LIKE %s
            LIMIT %s OFFSET %s;
        """,'%' + PESQUISAR + '%', per_page, offset)
        total_sistemas = cursor.fetchone()['total']

        total_pages = (total_sistemas + per_page - 1) // per_page  # Total de páginas

    cursor.close()
    fechar_conexao(conn)

    return render_template('seus_sistemas.html', sistemas=sistemas, page=page, total_pages=total_pages)

@sistemas_bp.route('/excluir/<int:id>', methods=['GET'])
def excluir_sistema(id):

    if 'usuario' not in session:
        return redirect(url_for('usuarios.login_usuario'))
    
    ID_USUARIO = session.get('usuario')['id_usuario']
    conn = criar_conexao()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute("DELETE FROM SISTEMAS WHERE ID_SISTEMA = %s AND ID_USUARIO = %s", (id, ID_USUARIO))

    conn.commit()
    cursor.close()
    fechar_conexao(conn)
    return redirect(url_for('sistemas.listar_sistema'))