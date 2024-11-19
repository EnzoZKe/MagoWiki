from flask import Blueprint, request, render_template, redirect, url_for, session
from conexao import criar_conexao, fechar_conexao


magias_bp = Blueprint('magias', __name__)

@magias_bp.route('/listar_magias', methods=['GET'])
def listar_magia():
    PESQUISAR = request.args.get('PESQUISAR', "")
    SELECAO = request.args.get('SELECAO')

    ID_USUARIO = session.get('usuario')['id_usuario']
    print(ID_USUARIO)

    # Recebe o número da página e o limite de registros por página
    page = request.args.get('page', 1, type=int)
    per_page = 8  # Número de registros por página (ajuste conforme necessário)

    offset = (page - 1) * per_page  # Calcula o offset para a consulta SQL

    conn = criar_conexao()
    cursor = conn.cursor(dictionary=True)

    # Se o campo PESQUISAR estiver vazio, executa a query normal com paginação
    if not PESQUISAR:  
        cursor.execute("""
        SELECT m.*, s.nome_sistema, c.nome_classe, u.nome
        FROM magias m 
        INNER JOIN sistemas s ON m.id_sistema = s.id_sistema
        INNER JOIN classes c ON m.id_classe = c.id_classe
        INNER JOIN usuarios u ON m.id_usuario = u.id_usuario
        ORDER BY id_magia
        LIMIT %s OFFSET %s;
        """, (per_page, offset))

        magias = cursor.fetchall()

        # Pega o número total de registros para calcular o total de páginas
        cursor.execute("SELECT COUNT(*) AS total FROM magias")
        total_magias = cursor.fetchone()['total']

        total_pages = (total_magias + per_page - 1) // per_page  # Total de páginas

    else:
        # Filtrando a busca com base no campo SELECAO
        if SELECAO == 'SISTEMA':
            cursor.execute("""
            SELECT m.*, s.nome_sistema
            FROM magias m 
            INNER JOIN sistemas s ON m.id_sistema = s.id_sistema
            WHERE s.nome_sistema LIKE %s
            LIMIT %s OFFSET %s;
            """, ('%' + PESQUISAR + '%', per_page, offset))

        elif SELECAO == 'NOME':
            cursor.execute("""
            SELECT m.*, s.nome_sistema, c.nome_classe
            FROM magias m
            INNER JOIN sistemas s ON m.id_sistema = s.id_sistema
            INNER JOIN classes c ON m.id_classe = c.id_classe
            WHERE m.nome_magia LIKE %s
            LIMIT %s OFFSET %s;
            """, ('%' + PESQUISAR + '%', per_page, offset))

        elif SELECAO == 'CLASSE':
            cursor.execute("""
            SELECT m.*, c.nome_classe, s.nome_sistema
            FROM magias m 
            INNER JOIN classes c ON m.id_classe = c.id_classe
            INNER JOIN sistemas s ON m.id_sistema = s.id_sistema
            WHERE c.nome_classe LIKE %s
            LIMIT %s OFFSET %s;
            """, ('%' + PESQUISAR + '%', per_page, offset))

        # Pegar os resultados filtrados
        magias = cursor.fetchall()

        # Pega o número total de registros filtrados para calcular o total de páginas
        cursor.execute("""
        SELECT COUNT(*) AS total
        FROM magias m 
        INNER JOIN sistemas s ON m.id_sistema = s.id_sistema
        INNER JOIN classes c ON m.id_classe = c.id_classe
        INNER JOIN usuarios u ON m.id_usuario = u.id_usuario
        WHERE s.nome_sistema LIKE %s OR c.nome_classe LIKE %s OR m.nome_magia LIKE %s
        """, ('%' + PESQUISAR + '%', '%' + PESQUISAR + '%', '%' + PESQUISAR + '%'))
        total_magias = cursor.fetchone()['total']

        total_pages = (total_magias + per_page - 1) // per_page  # Total de páginas

    
        # Todos favorito do usuario logado
    cursor.execute("""
    SELECT m.id_magia
    FROM favoritos f
    INNER JOIN magias m ON f.id_magia = m.id_magia
    WHERE f.id_usuario = %s;
""", (ID_USUARIO,))

    favoritos = cursor.fetchall()
    print(favoritos)

    cursor.close()
    fechar_conexao(conn)

    return render_template('index.html', magias=magias, page=page, total_pages=total_pages, favoritos = favoritos)

@magias_bp.route('/novomagia', methods=['GET', 'POST'])
def criar_magia():
    #validação se meu usuario esta na sessão
    if 'usuario' not in session:
        return redirect(url_for('usuarios.login_usuario'))
    conn = criar_conexao()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        NOME_MAGIA = request.form['NOME_MAGIA'] #1
        CLASSE = request.form['CLASSE'] #2
        ALCANCE = request.form['ALCANCE'] #3
        SISTEMA = request.form['SISTEMA'] #4
        NIVEL = request.form['NIVEL'] #5
        IMAGEM = request.form['IMAGEM'] #6
        DESCRICAO = request.form['DESCRICAO'] #7
        DURACAO = request.form['DURACAO'] #8
        TEMPO_CONJURACAO = request.form['TEMPO_CONJURACAO'] #9
        ID_USUARIO = session.get('usuario')['id_usuario'] #10
        
        #                                       1            2       3          4          5         6        7          8          9
        cursor.execute('INSERT INTO magias(nome_magia, id_classe, alcance, id_sistema, nivel_uso, imagem, descricao, id_usuario, duracao, tempo_conjuracao)'
                       "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (NOME_MAGIA, CLASSE, ALCANCE, SISTEMA, NIVEL, IMAGEM, DESCRICAO, ID_USUARIO, DURACAO, TEMPO_CONJURACAO))
        
        conn.commit()
        cursor.close()
        fechar_conexao(conn)
        return redirect(url_for('magias.criar_magia'), )
    

    cursor.execute("SELECT * FROM CLASSES")
    classes = cursor.fetchall()
    

    cursor.execute("SELECT * FROM SISTEMAS")
    sistemas = cursor.fetchall()

    return render_template('criar_magia.html', classes = classes, sistemas = sistemas)

@magias_bp.route('/listar_suas_magias', methods=['GET'])
def listar_suas_magias():
    if 'usuario' not in session or 'id_usuario' not in session['usuario']:
        return redirect(url_for('usuarios.login_usuario'))
    
    PESQUISAR = request.args.get('PESQUISAR', "")
    SELECAO = request.args.get('SELECAO')

    # Recebe o número da página e o limite de registros por página
    page = request.args.get('page', 1, type=int)
    per_page = 5  # Número de registros por página (ajuste conforme necessário)

    offset = (page - 1) * per_page  # Calcula o offset para a consulta SQL
    
    id_usuario_logado = session['usuario']['id_usuario']
    conn = criar_conexao()
    cursor = conn.cursor(dictionary=True)

    if not PESQUISAR:
        # Query padrão para listar as magias do usuário logado sem filtro de pesquisa
        cursor.execute("""
            SELECT m.*, s.nome_sistema, c.nome_classe, u.nome
            FROM magias m
            INNER JOIN sistemas s ON m.id_sistema = s.id_sistema
            INNER JOIN classes c ON m.id_classe = c.id_classe
            INNER JOIN usuarios u ON m.id_usuario = u.id_usuario
            WHERE m.id_usuario = %s
            LIMIT %s OFFSET %s;
        """, (id_usuario_logado, per_page, offset))
        
        magias = cursor.fetchall()

        # Pega o número total de registros para calcular o total de páginas
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM magias
            WHERE id_usuario = %s
        """, (id_usuario_logado,))
        total_magias = cursor.fetchone()['total']

        total_pages = (total_magias + per_page - 1) // per_page  # Total de páginas

    else:
        # Filtrando a busca com base no campo SELECAO
        if SELECAO == 'SISTEMA':
            cursor.execute("""
                SELECT m.*, s.nome_sistema
                FROM magias m 
                INNER JOIN sistemas s ON m.id_sistema = s.id_sistema
                WHERE m.id_usuario = %s AND s.nome_sistema LIKE %s
                LIMIT %s OFFSET %s;
            """, (id_usuario_logado, '%' + PESQUISAR + '%', per_page, offset))

        elif SELECAO == 'NOME':
            cursor.execute("""
                SELECT * FROM magias
                WHERE id_usuario = %s AND nome_magia LIKE %s
                LIMIT %s OFFSET %s;
            """, (id_usuario_logado, '%' + PESQUISAR + '%', per_page, offset))

        elif SELECAO == 'CLASSE':
            cursor.execute("""
                SELECT m.*, c.nome_classe
                FROM magias m 
                INNER JOIN classes c ON m.id_classe = c.id_classe
                WHERE m.id_usuario = %s AND c.nome_classe LIKE %s
                LIMIT %s OFFSET %s;
            """, (id_usuario_logado, '%' + PESQUISAR + '%', per_page, offset))

        # Pegar os resultados filtrados
        magias = cursor.fetchall()

        # Pega o número total de registros filtrados para calcular o total de páginas
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM magias m 
            INNER JOIN sistemas s ON m.id_sistema = s.id_sistema
            INNER JOIN classes c ON m.id_classe = c.id_classe
            WHERE m.id_usuario = %s AND (s.nome_sistema LIKE %s OR c.nome_classe LIKE %s OR m.nome_magia LIKE %s)
        """, (id_usuario_logado, '%' + PESQUISAR + '%', '%' + PESQUISAR + '%', '%' + PESQUISAR + '%'))
        total_magias = cursor.fetchone()['total']

        total_pages = (total_magias + per_page - 1) // per_page  # Total de páginas

    cursor.close()
    fechar_conexao(conn)

    return render_template('magia.html', magias=magias, page=page, total_pages=total_pages)

@magias_bp.route('/alterar/<int:id>', methods=['GET', 'POST'])
def alterar_magia(id):
    conn = criar_conexao()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        # Se o metodo for post, significa que o formulario de alteração foi submetido

        # Coleta os dados que o usuario enviou
        NOME_MAGIA = request.form['NOME_MAGIA'] #1
        CLASSE = request.form['CLASSE'] #2
        ALCANCE = request.form['ALCANCE'] #3
        SISTEMA = request.form['SISTEMA'] #4
        NIVEL = request.form['NIVEL'] #5
        IMAGEM = request.form['IMAGEM'] #6
        DESCRICAO = request.form['DESCRICAO'] #7
        DURACAO = request.form['DURACAO'] #8
        TEMPO_CONJURACAO = request.form['TEMPO_CONJURACAO'] #9


        # Executa o comando SQL
        cursor.execute(""" UPDATE MAGIAS
                       SET NOME_MAGIA = %s, ID_CLASSE = %s, ALCANCE = %s, ID_SISTEMA = %s, nivel_uso = %s, IMAGEM = %s, DESCRICAO = %s,
                       DURACAO = %s, TEMPO_CONJURACAO = %s WHERE ID_MAGIA = %s 
                        """, (NOME_MAGIA, CLASSE, ALCANCE, SISTEMA, NIVEL, IMAGEM, DESCRICAO, DURACAO, TEMPO_CONJURACAO,id))
        conn.commit()

        cursor.close()
        fechar_conexao(conn)

        return redirect(url_for('magias.listar_magia'))
    
    # Se o metodo for get, busca e preenche os dados do livro
    cursor.execute("SELECT * FROM MAGIAS WHERE ID_MAGIA = %s ", (id,))
    magia = cursor.fetchone()

    cursor.execute("SELECT * FROM USUARIOS")
    usuarios = cursor.fetchall()

    cursor.execute("SELECT * FROM CLASSES")
    classes = cursor.fetchall()
    
    cursor.execute("SELECT * FROM SISTEMAS")
    sistemas = cursor.fetchall()

    cursor.close()
    fechar_conexao(conn)

    return render_template('alterar_magia.html', magia=magia, usuarios=usuarios, classes = classes, sistemas = sistemas)

@magias_bp.route('/excluir/<int:id>', methods=['GET'])
def excluir_magia(id):
    conn = criar_conexao()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("DELETE FROM MAGIAS WHERE ID_MAGIA = %s", (id,))

    conn.commit()
    cursor.close()
    fechar_conexao(conn)
    return redirect(url_for('magias.listar_magia'))

@magias_bp.route('/ver/<int:id>', methods=['GET'])
def ver_magia(id):
    conn = criar_conexao()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
    select m.*, s.nome_sistema, c.nome_classe, u.nome
    from magias m inner join sistemas s on m.id_sistema = s.id_sistema
			  inner join classes c on m.id_classe = c.id_classe
			  inner join usuarios u on m.id_usuario = u.id_usuario
              where id_magia = %s """, (id,))
    magia = cursor.fetchone()

    cursor.close()
    fechar_conexao(conn)

    return render_template('ver_magia.html', magia=magia)