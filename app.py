from flask import Flask, render_template, request, redirect, flash, url_for, session, send_from_directory
from flask_mysqldb import MySQL
import hashlib
import os
from werkzeug.utils import secure_filename
from functools import wraps

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

# Decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Você precisa estar logado para acessar essa página.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def professor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('usuario_tipo') != 'professor':
            flash('Acesso restrito aos professores.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def aluno_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('usuario_tipo') != 'aluno':
            flash('Acesso restrito aos alunos.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Rota da página inicial
@app.route("/")
def index():
    return render_template("index.html")

# Página inicial do aluno
@app.route('/index_aluno')
@login_required
@aluno_required
def index_aluno():
    usuario_id = session.get('usuario_id')
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT nome FROM usuarios WHERE id = %s', (usuario_id,))
    usuario = cursor.fetchone()
    nome = usuario[0] if usuario else 'Aluno'
    return render_template('index_aluno.html', nome=nome)

# Página inicial do professor
@app.route('/index_professor')
@login_required
@professor_required
def index_professor():
    usuario_id = session.get('usuario_id')
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT nome FROM usuarios WHERE id = %s', (usuario_id,))
    usuario = cursor.fetchone()
    nome = usuario[0] if usuario else 'Professor'
    return render_template('index_professor.html', nome=nome)

# Cadastro
@app.route('/Cadastro', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        tipo = request.form['tipo']

        if tipo not in ['aluno', 'professor']:
            flash('Tipo de usuário inválido.', 'danger')
            return redirect(url_for('register'))

        cursor = mysql.connection.cursor()

        # Verifica se o email já está cadastrado
        cursor.execute('SELECT id FROM usuarios WHERE email = %s', (email,))
        if cursor.fetchone():
            flash('Este e-mail já está cadastrado.', 'danger')
            return redirect(url_for('register'))

        senha_hash = hashlib.sha256(senha.encode()).hexdigest()

        cursor.execute(
            'INSERT INTO usuarios (nome, email, senha_hash, tipo) VALUES (%s, %s, %s, %s)',
            (nome, email, senha_hash, tipo)
        )
        mysql.connection.commit()

        flash('Cadastro realizado com sucesso!', 'success')
        return redirect(url_for('index'))

    return render_template('register.html')

# Login
@app.route('/Login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        senha_hash = hashlib.sha256(senha.encode()).hexdigest()

        cursor = mysql.connection.cursor()
        cursor.execute(
            'SELECT id, nome, email, senha_hash, tipo FROM usuarios WHERE email = %s AND senha_hash = %s',
            (email, senha_hash)
        )
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
            flash('Email ou senha inválidos.', 'danger')
            return redirect(url_for('index', abrir_login=1))  # <-- mantém o modal aberto

    return render_template('index.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('index'))

# Adicionar materiais

@app.route('/adicionar_materiais', methods=['GET', 'POST'])
@login_required
@professor_required
def adicionar_materiais():
    professor_id = session['usuario_id']
    cursor = mysql.connection.cursor()

    if request.method == 'POST':
        cursor.execute("SELECT id FROM usuarios WHERE id = %s AND tipo = 'professor'", (professor_id,))
        resultado = cursor.fetchone()
        if resultado is None:
            flash('Erro: professor não encontrado no sistema.', 'danger')
            return redirect(url_for('index_professor'))

        titulo = request.form['titulo']
        materia = request.form['materia']
        descricao = request.form['descricao']
        arquivo = request.files['arquivo']

        if arquivo:
            print(f"Arquivo recebido: {arquivo.filename}")  # DEBUG
        else:
            print("Nenhum arquivo recebido")  # DEBUG

        if arquivo and allowed_file(arquivo.filename):
            filename = secure_filename(arquivo.filename)
            caminho = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            arquivo.save(caminho)

            url_arquivo = f'uploads/{filename}'

            cursor.execute(
                "INSERT INTO materiais (professor_id, titulo, materia, descricao, url) VALUES (%s, %s, %s, %s, %s)",
                (professor_id, titulo, materia, descricao, url_arquivo)
            )

            mysql.connection.commit()
            flash('Material adicionado com sucesso!', 'success')
            return redirect(url_for('adicionar_materiais'))
        else:
            flash('Tipo de arquivo não permitido.', 'danger')

    cursor.execute(
        "SELECT id, titulo, materia, descricao, url FROM materiais WHERE professor_id = %s",
        (professor_id,)
    )
    materiais = cursor.fetchall()

    return render_template('adicionar_materiais.html', materiais=materiais)



# Editar material (somente professor)
@app.route('/editar_material/<int:material_id>', methods=['POST'])
@login_required
@professor_required
def editar_material(material_id):
    novo_titulo = request.form['novo_titulo']
    nova_descricao = request.form['nova_descricao']

    cursor = mysql.connection.cursor()
    cursor.execute(
        "UPDATE materiais SET titulo = %s, descricao = %s WHERE id = %s AND professor_id = %s",
        (novo_titulo, nova_descricao, material_id, session['usuario_id'])
    )
    mysql.connection.commit()

    flash('Material atualizado com sucesso!', 'success')
    return redirect(url_for('adicionar_materiais'))

# Excluir material (somente professor)
@app.route('/excluir_material/<int:material_id>', methods=['POST'])
@login_required
@professor_required
def excluir_material(material_id):
    cursor = mysql.connection.cursor()

    cursor.execute(
        "SELECT url FROM materiais WHERE id = %s AND professor_id = %s",
        (material_id, session['usuario_id'])
    )
    resultado = cursor.fetchone()

    if resultado:
        caminho_arquivo = resultado[0]
        try:
            os.remove(caminho_arquivo)
        except:
            pass

        cursor.execute(
            "DELETE FROM materiais WHERE id = %s AND professor_id = %s",
            (material_id, session['usuario_id'])
        )
        mysql.connection.commit()
        flash('Material excluído com sucesso.', 'success')
    else:
        flash('Material não encontrado ou acesso negado.', 'danger')

    return redirect(url_for('adicionar_materiais'))

# Baixar material (usuário logado)
@app.route('/baixar_material/<int:material_id>')
@login_required
def baixar_material(material_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT url FROM materiais WHERE id = %s", (material_id,))
    resultado = cursor.fetchone()

    if resultado:
        caminho_relativo = resultado[0]
        filename = os.path.basename(caminho_relativo)
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    else:
        flash('Material não encontrado.', 'danger')
        return redirect(url_for('index'))


# Arquivos públicos
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Página de materiais
@app.route('/materiais')
@login_required
@aluno_required
def materiais():
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT m.id, m.titulo, m.materia, m.descricao, m.url, u.nome 
        FROM materiais m
        JOIN usuarios u ON m.professor_id = u.id
    """)
    materiais = cursor.fetchall()
    return render_template('materiais.html', materiais=materiais)


@app.route('/ajuda')
def ajuda():
    return render_template('ajuda.html')



if __name__ == '__main__':
    app.run(debug=True)
