from flask import Flask, render_template, request, redirect, flash, url_for, session, send_from_directory
from flask_mysqldb import MySQL
import hashlib
import os
from werkzeug.utils import secure_filename
from functools import wraps
from datetime import datetime  

data_publicacao = datetime.now()

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

# Decoradores
def adm_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('usuario_tipo') != 'adm':
            flash('Acesso restrito aos administradores.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


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

#Página ADMINITRADOR
@app.route('/index_adm')
@login_required
@adm_required
def index_adm():
    return render_template('index_adm.html', nome=session.get('usuario_nome'))

#GERENCIAR USUARIOS - ADM
@app.route('/gerenciar_usuarios')
@login_required
@adm_required
def gerenciar_usuarios():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, nome, email, tipo FROM usuarios")
    usuarios = cursor.fetchall()
    return render_template('gerenciar_usuarios.html', usuarios=usuarios)

#GERENCIAR MATERIAIS -  ADM
@app.route('/gerenciar_materiais')
@login_required
@adm_required
def gerenciar_materiais():
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT m.id, m.titulo, m.materia, m.descricao, m.url, u.nome 
        FROM materiais m
        JOIN usuarios u ON m.professor_id = u.id
    """)
    materiais = cursor.fetchall()
    return render_template('gerenciar_materiais.html', materiais=materiais)

#Editar Usuário
@app.route('/editar_usuario/<int:usuario_id>', methods=['POST'])
@login_required
@adm_required
def editar_usuario(usuario_id):
    nome = request.form.get('nome')
    email = request.form.get('email')
    tipo = request.form.get('tipo')

    if tipo not in ['aluno', 'professor', 'adm']:
        flash("Tipo inválido.", "danger")
        return redirect(url_for('gerenciar_usuarios'))

    cursor = mysql.connection.cursor()
    cursor.execute("""
        UPDATE usuarios SET nome = %s, email = %s, tipo = %s WHERE id = %s
    """, (nome, email, tipo, usuario_id))
    mysql.connection.commit()

    flash("Usuário atualizado com sucesso.", "success")
    return redirect(url_for('gerenciar_usuarios'))

#Excluir Usuário
@app.route('/excluir_usuario/<int:usuario_id>', methods=['POST'])
@login_required
@adm_required
def excluir_usuario(usuario_id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id = %s", (usuario_id,))
    mysql.connection.commit()

    flash("Usuário excluído com sucesso.", "success")
    return redirect(url_for('gerenciar_usuarios'))

#Editar Materiais
@app.route('/editar_material_adm/<int:material_id>', methods=['POST'])
@login_required
@adm_required
def editar_material_adm(material_id):
    novo_titulo = request.form.get('titulo')
    nova_descricao = request.form.get('descricao')

    cursor = mysql.connection.cursor()
    cursor.execute("""
        UPDATE materiais SET titulo = %s, descricao = %s WHERE id = %s
    """, (novo_titulo, nova_descricao, material_id))
    mysql.connection.commit()

    flash("Material atualizado com sucesso.", "success")
    return redirect(url_for('gerenciar_materiais'))

#Excluir Materiais
@app.route('/excluir_material_adm/<int:material_id>', methods=['POST'])
@login_required
@adm_required
def excluir_material_adm(material_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT url FROM materiais WHERE id = %s", (material_id,))
    resultado = cursor.fetchone()

    if resultado:
        caminho_arquivo = resultado[0]
        try:
            os.remove(caminho_arquivo)
        except:
            pass

        cursor.execute("DELETE FROM materiais WHERE id = %s", (material_id,))
        mysql.connection.commit()
        flash('Material excluído com sucesso.', 'success')
    else:
        flash('Material não encontrado.', 'danger')

    return redirect(url_for('gerenciar_materiais'))


# Cadastro
@app.route('/Cadastro', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        tipo = request.form['tipo']

        if tipo not in ['aluno', 'professor', 'adm']:
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
            elif usuario[4] == 'adm':
                return redirect(url_for('index_adm'))

        else:
            flash('Email ou senha inválidos.', 'danger')
            return redirect(url_for('index', abrir_login=1)) 

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
    "INSERT INTO materiais (professor_id, titulo, materia, descricao, url, data_publicacao) VALUES (%s, %s, %s, %s, %s, %s)",
    (professor_id, titulo, materia, descricao, url_arquivo, data_publicacao)
)

            mysql.connection.commit()
            flash('Material adicionado com sucesso!', 'success')
            return redirect(url_for('adicionar_materiais'))
        else:
            flash('Tipo de arquivo não permitido.', 'danger')

    cursor.execute("""
    SELECT m.id, m.titulo, m.materia, m.descricao, m.url, m.professor_id, u.nome, m.data_publicacao
    FROM materiais m
    JOIN usuarios u ON m.professor_id = u.id
    ORDER BY m.data_publicacao DESC
""")

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

#primeira tentativa para o quiz
@app.route('/quiz', methods=['GET', 'POST'])
@login_required
@aluno_required
def quiz():
    cursor = mysql.connection.cursor()
    
    if request.method == 'POST':
        respostas = request.form.to_dict()
        aluno_id = session['usuario_id']
        nivel_id = int(respostas.pop('nivel_id'))
        
        cursor.execute("INSERT INTO tentativas_quiz (aluno_id, nivel_id) VALUES (%s, %s)", (aluno_id, nivel_id))
        tentativa_id = cursor.lastrowid

        for questao_id_str, alternativa_id in respostas.items():
            questao_id = int(questao_id_str)
            cursor.execute("SELECT correta FROM alternativas WHERE id = %s", (alternativa_id,))
            correta = cursor.fetchone()[0]
            cursor.execute("""
                INSERT INTO respostas_alunos (tentativa_id, questao_id, alternativa_id, correta)
                VALUES (%s, %s, %s, %s)
            """, (tentativa_id, questao_id, alternativa_id, correta))

        mysql.connection.commit()
        flash("Respostas enviadas com sucesso!", "success")
        return redirect(url_for('index_aluno'))

    # GET: exibe quiz
    nivel_id = 1  # pode vir de um formulário ou ser aleatório
    cursor.execute("""
        SELECT q.id, q.enunciado FROM questoes q
        WHERE q.nivel_id = %s
        ORDER BY RAND() LIMIT 5
    """, (nivel_id,))
    questoes = cursor.fetchall()

    questoes_com_alternativas = []
    for questao in questoes:
        cursor.execute("SELECT id, texto FROM alternativas WHERE questao_id = %s", (questao[0],))
        alternativas = cursor.fetchall()
        questoes_com_alternativas.append({
            'id': questao[0],
            'enunciado': questao[1],
            'alternativas': alternativas
        })

    return render_template('quiz.html', questoes=questoes_com_alternativas, nivel_id=nivel_id)


#rota para enviar questões no bd
@app.route('/gerenciar_questoes')
@login_required
@professor_required
def gerenciar_questoes():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, descricao FROM niveis_dificuldade")
    niveis = cursor.fetchall()
    cursor.execute("SELECT id, nome FROM assuntos")
    assuntos = cursor.fetchall()
    return render_template('index_professor.html', nome=session['usuario_nome'], niveis=niveis, assuntos=assuntos)

@app.route('/adicionar_questao', methods=['POST'])
@login_required
@professor_required
def adicionar_questao():
    cursor = mysql.connection.cursor()
    autor_id = session['usuario_id']
    nivel_id = request.form.get('nivel_id')
    assunto_id = request.form.get('assunto_id')
    enunciado = request.form.get('enunciado')
    alternativas = request.form.getlist('alternativas')
    correta_index = int(request.form.get('correta_index')) - 1


    # Inserir questão
    cursor.execute("""
        INSERT INTO questoes (enunciado, nivel_id, assunto_id, autor_id)
        VALUES (%s, %s, %s, %s)
    """, (enunciado, nivel_id, assunto_id, autor_id))
    questao_id = cursor.lastrowid

    # Inserir alternativas
    for i, texto in enumerate(alternativas):
        correta = 1 if i == correta_index else 0
        cursor.execute("""
            INSERT INTO alternativas (questao_id, texto, correta)
            VALUES (%s, %s, %s)
        """, (questao_id, texto, correta))

    mysql.connection.commit()
    flash("Questão adicionada com sucesso!", "success")
    return redirect(url_for('gerenciar_questoes'))


if __name__ == '__main__':
    app.run(debug=True)
