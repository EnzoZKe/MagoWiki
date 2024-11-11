from flask import Blueprint, request, render_template, redirect, url_for, session
from conexao import criar_conexao, fechar_conexao

favoritos_bp = Blueprint('favoritos', __name__)

@favoritos_bp.route('/listar_favoritos', methods=['GET'])
def listar_favoritos():
    conn = criar_conexao()
    cursor = conn.cursor(dictionary=True)

    ID_USUARIO = session.get('usuario')['id_usuario']

    # Consulta para pegar os favoritos do usuário
    cursor.execute("""
        SELECT f.*, m.*, s.nome_sistema, c.nome_classe
        FROM favoritos f
        INNER JOIN magias m ON f.id_magia = m.id_magia
        INNER JOIN sistemas s ON m.id_sistema = s.id_sistema
        INNER JOIN classes c ON m.id_classe = c.id_classe
        WHERE f.id_usuario = %s;
    """, (ID_USUARIO,))

    # Armazena os favoritos do usuário
    favoritos = cursor.fetchall()
    
    cursor.close()
    fechar_conexao(conn)
    
    # Renderiza a página com os favoritos
    return render_template('favoritos.html', favoritos=favoritos)

@favoritos_bp.route('/favoritar', methods=['POST'])
def favoritar():
    if 'usuario' not in session:
        return redirect(url_for('usuarios.login_usuario'))

    conn = criar_conexao()
    cursor = conn.cursor(dictionary=True)

    ID_USUARIO = session.get('usuario')['id_usuario']
    ID_MAGIA = request.form['ID_MAGIA']

    # Verifica se a magia já foi favoritada pelo usuário
    cursor.execute("""
        SELECT * FROM favoritos WHERE id_usuario = %s AND id_magia = %s;
    """, (ID_USUARIO, ID_MAGIA))

    favorito = cursor.fetchone()

    if favorito:
        # Se já for favoritada, remove o favorito (desfavorita)
        cursor.execute("""
            DELETE FROM favoritos WHERE id_usuario = %s AND id_magia = %s;
        """, (ID_USUARIO, ID_MAGIA))
    else:
        # Caso contrário, adiciona aos favoritos
        cursor.execute("""
            INSERT INTO favoritos (id_usuario, id_magia) VALUES (%s, %s);
        """, (ID_USUARIO, ID_MAGIA))

    conn.commit()
    cursor.close()
    fechar_conexao(conn)

    return redirect(url_for('magias.listar_magia'))

@favoritos_bp.route('/desfavoritar', methods=['POST'])
def desfavoritar():
    conn = criar_conexao()
    cursor = conn.cursor(dictionary=True)

    ID_USUARIO = session.get('usuario')['id_usuario']
    ID_MAGIA = request.form['ID_MAGIA']


    cursor.execute("""
            DELETE FROM favoritos WHERE id_usuario = %s AND id_magia = %s;
        """, (ID_USUARIO, ID_MAGIA))
    
    conn.commit()
    cursor.close()
    fechar_conexao(conn)

    return redirect(url_for('favoritos.listar_favoritos'))


