from flask import Blueprint, request, render_template, redirect, url_for, session
from conexao import criar_conexao, fechar_conexao
from hashlib import sha256
from psycopg2.extras import RealDictCursor

usuarios_bp = Blueprint('usuarios', __name__)

@usuarios_bp.route('/novousuario', methods=['GET', 'POST'])
def criar_usuario():
    if request.method == 'POST':
        NOME = request.form['NOME']
        SENHA = request.form['SENHA']
        PFP = request.form['PFP']
        EMAIL = request.form['EMAIL']

        #criptografa a senha
        senhaCripto = sha256(SENHA.encode('utf-8')).hexdigest()

        conn = criar_conexao()
        cursor = conn.cursor()

        cursor.execute("insert into usuarios(nome, senha, PFP, email)" "values(%s, %s, %s, %s)", (NOME, senhaCripto, PFP, EMAIL))
        conn.commit()

        cursor.close()
        fechar_conexao(conn)
        return render_template('login.html', mensagem='Usuario Criado com sucesso')
    return render_template('criar_usuario.html')

@usuarios_bp.route('/login', methods=['GET', 'POST'])
def login_usuario():
    if request.method == "POST":
        EMAIL = request.form['EMAIL']
        SENHA = request.form['SENHA']
        conn = criar_conexao()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT SENHA, EMAIL, NOME, PFP, USUARIO_TIPO, ID_USUARIO FROM USUARIOS WHERE EMAIL = %s", (EMAIL,))
        senhaBanco = cursor.fetchone()

        print(senhaBanco)
        
        if senhaBanco and checar_senha(senhaBanco['senha'], SENHA):
            session['usuario'] = {
                'id_usuario': senhaBanco['id_usuario'],
                'email': senhaBanco['email'],
                'nome': senhaBanco['nome'],
                'pfp': senhaBanco['pfp'],
                'usuario_tipo': senhaBanco['usuario_tipo']
            }
            
            return redirect(url_for('home'))
        else:
            return render_template('login.html', mensagem = 'Login Incorreto')
        # cursor.close()
        # fechar_conexao(conn)
            
    return render_template('login.html')

        
def checar_senha(senhaBanco, senha):
    senha_convertida = sha256(senha.encode('utf-8')).hexdigest()
    return senha_convertida == senhaBanco

@usuarios_bp.route('/logout')
def logout():
    session.pop('usuario', None)#remove o usuario da sessao
    return redirect(url_for('home'))

@usuarios_bp.route('/perfil', methods=['GET'])
def perfil():
    if 'usuario' not in session:
        return redirect(url_for('usuarios.login_usuario'))

    ID_USUARIO = session['usuario']['id_usuario']

    # Conectando ao banco de dados
    conn = criar_conexao()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Consultar o número de magias cadastradas pelo usuário
    cursor.execute("SELECT COUNT(*) AS total_magias FROM MAGIAS WHERE ID_USUARIO = %s", (ID_USUARIO,))
    resultado = cursor.fetchone()
    total_magias = resultado['total_magias'] if resultado else 0

    cursor.execute("SELECT COUNT(*) AS total_classes FROM CLASSES WHERE ID_USUARIO = %s", (ID_USUARIO,))
    resultado = cursor.fetchone()
    total_classes = resultado['total_classes'] if resultado else 0

    cursor.execute("SELECT COUNT(*) AS total_sistemas FROM SISTEMAS WHERE ID_USUARIO = %s", (ID_USUARIO,))
    resultado = cursor.fetchone()
    total_sistemas = resultado['total_sistemas'] if resultado else 0

    cursor.close()
    fechar_conexao(conn)
    return render_template('perfil.html', usuario=session['usuario'], total_magias=total_magias, total_classes=total_classes, total_sistemas=total_sistemas)

@usuarios_bp.route('/atualizarperfil', methods=['GET', 'POST'])
def atualizar_perfil():
    conn = criar_conexao()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    ID_USUARIO = session.get('usuario')['id_usuario']
    
    if request.method == 'POST':
        NOME = request.form['NOME']
        EMAIL = request.form['EMAIL']
        PFP = request.form['PFP']
        USUARIO_TIPO = session['usuario'].get('usuario_tipo')  # Obtém o tipo de usuário da sessão

        # Atualiza o perfil, incluindo usuario_tipo
        cursor.execute("""
            UPDATE USUARIOS SET NOME = %s, EMAIL = %s, PFP = %s, USUARIO_TIPO = %s 
            WHERE ID_USUARIO = %s
        """, (NOME, EMAIL, PFP, USUARIO_TIPO, ID_USUARIO))

        conn.commit()

        # Atualiza a sessão com os dados atualizados
        session['usuario'] = {
            'id_usuario': ID_USUARIO,
            'email': EMAIL,
            'nome': NOME,
            'pfp': PFP,
            'usuario_tipo': USUARIO_TIPO
        }

        cursor.close()
        fechar_conexao(conn)

        return redirect(url_for('usuarios.perfil'))

    # Carrega os dados do usuário para exibir na página
    cursor.execute("""SELECT nome, email, PFP, USUARIO_TIPO FROM USUARIOS WHERE ID_USUARIO = %s""", (ID_USUARIO,))
    usuario = cursor.fetchone()

    cursor.close()
    fechar_conexao(conn)

    return render_template('atualizar_perfil.html', usuario=usuario)



@usuarios_bp.route('/atualizarsenha', methods=['GET', 'POST'])
def atualizar_senha():
    if 'usuario' not in session:
        return redirect(url_for('usuarios.login_usuario'))

    ID_USUARIO = session.get('usuario')['id_usuario']

    if request.method == 'POST':
        senha_atual = request.form['SENHA']
        nova_senha = request.form['NOVA_SENHA']
        confirmar_senha = request.form['CONFIRMAR_SENHA']

        # Validar se a nova senha e a confirmação são iguais
        if nova_senha != confirmar_senha:
            return render_template('atualizar_senha.html', mensagem='As senhas não coincidem', usuario=session['usuario'])

        # Verificar a senha atual
        conn = criar_conexao()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT SENHA FROM USUARIOS WHERE ID_USUARIO = %s", (ID_USUARIO,))
        usuario = cursor.fetchone()
        
        # Verifica se a senha atual inserida corresponde ao hash no banco de dados
        if not checar_senha(usuario['SENHA'], senha_atual):
            cursor.close()
            fechar_conexao(conn)
            return render_template('atualizar_senha.html', mensagem='Senha atual incorreta', usuario=session['usuario'])

        # Criptografa a nova senha
        nova_senha_hash = sha256(nova_senha.encode('utf-8')).hexdigest()

        # Atualiza a nova senha no banco de dados
        cursor.execute("UPDATE USUARIOS SET SENHA = %s WHERE ID_USUARIO = %s", (nova_senha_hash, ID_USUARIO))
        conn.commit()

        cursor.close()
        fechar_conexao(conn)

        return render_template('perfil.html', mensagem='Senha atualizada com sucesso', usuario=session['usuario'])

    return render_template('atualizar_senha.html', usuario=session['usuario'])