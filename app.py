from flask import Flask, render_template, session, redirect, url_for
from flask_cors import CORS
from rotas.rotas_usuarios import usuarios_bp
from rotas.rotas_magias import magias_bp
from rotas.rotas_magias import magias_bp, listar_magia
from rotas.rotas_sistemas import sistemas_bp, listar_sistema
from rotas.rotas_classes import classes_bp, listar_classe
from rotas.rotas_favoritos import favoritos_bp

app = Flask(__name__)
CORS(app)
app.secret_key = "123456"

app.register_blueprint(usuarios_bp, url_prefix='/usuarios')
app.register_blueprint(magias_bp, url_prefix='/magias')
app.register_blueprint(sistemas_bp, url_prefix='/sistemas')
app.register_blueprint(classes_bp, url_prefix='/classes')
app.register_blueprint(favoritos_bp, url_prefix='/favoritos')

@app.route('/')
def home():
    #verificação se esta logado e redirecionamento da página
    if 'usuario' in session:
        return listar_magia()
    else: 
        return render_template('index.html')
    
if __name__ == "__main__":
    app.run(port=5000, host="localhost", debug=True)