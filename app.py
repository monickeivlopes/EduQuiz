from flask import Flask, render_template, request, redirect, flash, url_for, session
from flask_mysqldb import MySQL
import hashlib
import os
from werkzeug.utils import secure_filename


app = Flask(__name__)

# Configuração do banco de dados
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'Eduquiz'
app.secret_key = 'supersecretkey' 
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


mysql = MySQL(app)


#Função auxiliar para mandar os materiais para o banco
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Rota da página inicial
@app.route("/")
def index():
    return render_template("index.html")
    

@app.route('/index_aluno')
def index_aluno():
    usuario_id = session.get('usuario_id')
    if not usuario_id:
        flash('Usuário não está logado.', 'danger')
        return redirect(url_for('index'))

    cursor = mysql.connection.cursor()
    cursor.execute('SELECT nome FROM usuarios WHERE id = %s', (usuario_id,))
    usuario = cursor.fetchone()

    if usuario:
        nome = usuario[0]
    else:
        nome = 'Aluno'
    return render_template('index_aluno.html', nome=nome)

    
@app.route('/index_professor')
def index_professor():
    usuario_id = session.get('usuario_id')
    if not usuario_id:
        flash('Usuário não está logado.', 'danger')
        return redirect(url_for('index'))

    cursor = mysql.connection.cursor()
    cursor.execute('SELECT nome FROM usuarios WHERE id = %s', (usuario_id,))
    usuario = cursor.fetchone()

    if usuario:
        nome = usuario[0] 
    else:
        nome = 'Professor'
        
    return render_template('index_professor.html', nome=nome)

# Rota de cadastro
@app.route('/Cadastro', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        tipo = request.form['tipo']  

        if tipo not in ['aluno', 'professor']:
            flash('Tipo de usuário inválido. Escolha "aluno" ou "professor".', 'danger')
            return redirect(url_for('register'))

        senha_hash = hashlib.sha256(senha.encode()).hexdigest()

        cursor = mysql.connection.cursor()
        cursor.execute(
            'INSERT INTO usuarios (nome, email, senha_hash, tipo) VALUES (%s, %s, %s, %s)',
            (nome, email, senha_hash, tipo)
        )
        mysql.connection.commit()

        flash('Cadastro realizado com sucesso!', 'success')
        return redirect(url_for('index'))

    return render_template('register.html')


# Rota de login
@app.route('/Login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        senha_hash = hashlib.sha256(senha.encode()).hexdigest()

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT id, nome, email, senha_hash, tipo FROM usuarios WHERE email = %s AND senha_hash = %s', (email, senha_hash))
        usuario = cursor.fetchone()

        if usuario:
            session['usuario_id'] = usuario[0]
            session['usuario_nome'] = usuario[1]
            session['usuario_tipo'] = usuario[4]

            if usuario[4] == 'aluno':
                return redirect(url_for('index_aluno'))
            elif usuario[4] == 'professor':
                return redirect(url_for('index_professor'))
            else:
                flash('Tipo de usuário inválido.', 'danger')
                return redirect(url_for('index'))
        else:
            flash('Email ou senha inválidos.', 'danger')
            return redirect(url_for('index'))

    return render_template('index.html')  


@app.route('/logout')
def logout():
    session.clear()
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('index'))

@app.route('/adicionar_materiais', methods=['GET', 'POST'])
def adicionar_materiais():
    if 'usuario_id' not in session or session.get('usuario_tipo') != 'professor':
        flash('Acesso restrito aos professores.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        titulo = request.form['titulo']
        materia = request.form['materia']
        descricao = request.form['descricao']
        arquivo = request.files['arquivo']

        if arquivo and allowed_file(arquivo.filename):
            filename = secure_filename(arquivo.filename)
            caminho = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            arquivo.save(caminho)

            url_arquivo = os.path.join('uploads', filename)
            professor_id = session['usuario_id']

            cursor = mysql.connection.cursor()
            cursor.execute(
                "INSERT INTO materiais (professor_id, titulo, url) VALUES (%s, %s, %s)",
                (professor_id, titulo, url_arquivo)
            )
            mysql.connection.commit()

            flash('Material adicionado com sucesso!', 'success')
            return redirect(url_for('index_professor'))
        else:
            flash('Tipo de arquivo não permitido.', 'danger')

    return render_template('adicionar_materiais.html')



if __name__ == '__main__':
    app.run(debug=True)
