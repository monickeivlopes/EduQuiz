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
    
    # Busca nome do usuário
    cursor.execute('SELECT nome FROM usuarios WHERE id = %s', (usuario_id,))
    usuario = cursor.fetchone()
    nome = usuario[0] if usuario else 'Aluno'
    
    # Busca todos os assuntos cadastrados
    cursor.execute("SELECT id, nome FROM assuntos")
    assuntos = cursor.fetchall()
    
    return render_template('index_aluno.html', nome=nome, assuntos=assuntos)

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
    senha = request.form.get('senha') 

    if tipo not in ['aluno', 'professor', 'adm']:
        flash("Tipo inválido.", "danger")
        return redirect(url_for('gerenciar_usuarios'))

    cursor = mysql.connection.cursor()

    if senha:  # Se ADM digitou nova senha
        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        cursor.execute("""
            UPDATE usuarios SET nome = %s, email = %s, tipo = %s, senha_hash = %s WHERE id = %s
        """, (nome, email, tipo, senha_hash, usuario_id))
    else:
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

    # Descobrir o tipo do usuário
    cursor.execute("SELECT tipo FROM usuarios WHERE id = %s", (usuario_id,))
    resultado = cursor.fetchone()

    if not resultado:
        flash("Usuário não encontrado.", "danger")
        return redirect(url_for('gerenciar_usuarios'))

    tipo = resultado[0]

    # Apagar da tabela relacionada
    if tipo == 'aluno':
        cursor.execute("DELETE FROM alunos WHERE id = %s", (usuario_id,))
    elif tipo == 'professor':
        cursor.execute("DELETE FROM professores WHERE id = %s", (usuario_id,))

    # Agora apagar da tabela usuarios
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
        curso_nome = request.form.get('curso')

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

        # Inserir usuário
        cursor.execute(
            'INSERT INTO usuarios (nome, email, senha_hash, tipo) VALUES (%s, %s, %s, %s)',
            (nome, email, senha_hash, tipo)
        )
        mysql.connection.commit()

        # Recuperar o ID recém-criado
        cursor.execute("SELECT LAST_INSERT_ID()")
        usuario_id = cursor.fetchone()[0]

        # Inserir em professores ou alunos
        if tipo == 'professor':
            cursor.execute("INSERT INTO professores (id) VALUES (%s)", (usuario_id,))
        
        elif tipo == 'aluno':
            # Verifica se o curso foi selecionado
            if not curso_nome:
                flash('Você precisa selecionar um curso.', 'danger')
                return redirect(url_for('register'))

            # Verifica se o curso existe no banco
            cursor.execute("SELECT id FROM cursos WHERE nome = %s", (curso_nome,))
            curso = cursor.fetchone()

            if not curso:
                flash('Curso inválido ou não encontrado.', 'danger')
                return redirect(url_for('register'))

            curso_id = curso[0]
            cursor.execute("INSERT INTO alunos (id, curso_id) VALUES (%s, %s)", (usuario_id, curso_id))

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

# Página de materiais (VIZUALIZAR)
# Página de materiais (VIZUALIZAR) - ATUALIZADA
# Página de materiais (VIZUALIZAR) - ATUALIZADA
@app.route('/materiais')
@login_required
@aluno_required
def materiais():
    data_filtro = request.args.get('data')  # formato YYYY-MM-DD
    ordem = request.args.get('ordem', 'desc')  # 'asc' ou 'desc'
    assunto_filtro = request.args.get('assunto', 'todos')  # Novo filtro por assunto

    cursor = mysql.connection.cursor()
    query = """
        SELECT m.id, m.titulo, m.materia, m.descricao, m.url, u.nome,
               DATE_FORMAT(m.data_publicacao, '%%Y-%%m-%%d')
        FROM materiais m
        JOIN usuarios u ON m.professor_id = u.id
    """
    params = []
    where_clauses = []

    if data_filtro:
        where_clauses.append("DATE(m.data_publicacao) = %s")
        params.append(data_filtro)

    if assunto_filtro != 'todos':
        where_clauses.append("m.materia = %s")
        params.append(assunto_filtro)

    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)

    if ordem.lower() == 'asc':
        query += " ORDER BY m.data_publicacao ASC"
    else:
        query += " ORDER BY m.data_publicacao DESC"

    cursor.execute(query, tuple(params))
    materiais = cursor.fetchall()

    # Assuntos fixos conforme definido no formulário (usando os VALUES)
    assuntos_disponiveis = [
        "Números e Operações",
        "Geometria e Medidas", 
        "Estatística e Probabilidade",
        "Álgebra e Funções",
        "Matemática Financeira e Aplicada"
    ]

    return render_template(
        'materiais.html',
        materiais=materiais,
        data_filtro=data_filtro,
        ordem=ordem,
        assunto_filtro=assunto_filtro,
        assuntos_disponiveis=assuntos_disponiveis
    )



@app.route('/ajuda')
def ajuda():
    return render_template('ajuda.html')

@app.route('/ajudaAluno')
def ajudaAluno():
    return render_template('ajudaAluno.html')

@app.route('/ajudaProf')
def ajudaProf():
    return render_template('ajudaProf.html')

#primeira tentativa para o quiz

@app.route('/quiz', methods=['GET', 'POST'])
@login_required
@aluno_required
def quiz():
    cursor = mysql.connection.cursor()

    if request.method == 'POST':
        try:
            form = request.form
            print("DEBUG /quiz POST form ->", dict(form))

            aluno_id = session.get('usuario_id')

            nivel_id_raw = form.get('nivel_id')            
            assunto_id_raw = form.get('assunto_id', 'todos')

            if nivel_id_raw is None:
                flash('Nível não informado no formulário.', 'danger')
                return redirect(url_for('index_aluno'))

            nivel_id = None if nivel_id_raw == 'variada' else (int(nivel_id_raw) if nivel_id_raw.isdigit() else None)
            assunto_id_value = None if (assunto_id_raw in [None, '', 'todos']) else int(assunto_id_raw)


            cursor.execute("SELECT id FROM alunos WHERE id = %s", (aluno_id,))
            if not cursor.fetchone():
                flash('Aluno não encontrado', 'danger')
                return redirect(url_for('index_aluno'))

            inicio_quiz_str = session.get('inicio_quiz')
            if inicio_quiz_str:
                try:
                    inicio_quiz = datetime.strptime(inicio_quiz_str, "%Y-%m-%d %H:%M:%S.%f")
                    tempo_gasto = int((datetime.now() - inicio_quiz).total_seconds())
                except Exception:
                    tempo_gasto = 0
            else:
                tempo_gasto = 0

            cursor.execute("""
                INSERT INTO tentativas_quiz (aluno_id, nivel_id, assunto_id, tempo_gasto)
                VALUES (%s, %s, %s, %s)
            """, (aluno_id, nivel_id, assunto_id_value, tempo_gasto))
            mysql.connection.commit()

 
            cursor.execute("SELECT LAST_INSERT_ID()")
            tentativa_row = cursor.fetchone()
            tentativa_id = tentativa_row[0] if tentativa_row else None
            if not tentativa_id:
                raise Exception("Não foi possível recuperar o id da tentativa inserida.")

            for chave, valor in form.items():
                if chave in ('nivel_id', 'assunto_id'):
                    continue
                try:
                    questao_id = int(chave)
                except Exception:
                    continue

                if not valor:
                    continue
                try:
                    alternativa_id = int(valor)
                except Exception:
                    continue

                cursor.execute("SELECT correta FROM alternativas WHERE id = %s", (alternativa_id,))
                row = cursor.fetchone()
                correta = int(row[0]) if row and row[0] is not None else 0

                cursor.execute("""
                    INSERT INTO respostas_alunos (tentativa_id, questao_id, alternativa_id, correta)
                    VALUES (%s, %s, %s, %s)
                """, (tentativa_id, questao_id, alternativa_id, correta))

            mysql.connection.commit()

            session.pop('inicio_quiz', None)

            return redirect(url_for('quiz_resultado', tentativa_id=tentativa_id))

        except Exception as e:
            import traceback
            traceback.print_exc()
            mysql.connection.rollback()
            flash(f'Erro ao processar quiz: {str(e)}', 'danger')
            return redirect(url_for('index_aluno'))


    if 'nivel_id' not in request.args:
        cursor.execute("SELECT id, descricao FROM niveis_dificuldade")
        niveis = cursor.fetchall()
        cursor.execute("SELECT id, nome FROM assuntos")
        assuntos = cursor.fetchall()
        return render_template('quiz_inicio.html', niveis=niveis, assuntos=assuntos)

    session['inicio_quiz'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

    nivel_id_raw = request.args['nivel_id']
    assunto_id = request.args.get('assunto_id', 'todos')

    nivel_variado = (nivel_id_raw == 'variada')
    assunto_nome = 'Todos os assuntos'
    if assunto_id != 'todos':
        cursor.execute("SELECT nome FROM assuntos WHERE id = %s", (assunto_id,))
        resultado = cursor.fetchone()
        if resultado:
            assunto_nome = resultado[0]

    query = """
        SELECT q.id, q.enunciado
        FROM questoes q
        WHERE 1=1
    """
    params = []
    if not nivel_variado:
        try:
            nivel_id = int(nivel_id_raw)
            query += " AND q.nivel_id = %s"
            params.append(nivel_id)
        except Exception:
            pass

    if assunto_id != 'todos':
        query += " AND q.assunto_id = %s"
        params.append(assunto_id)

    query += " ORDER BY RAND() LIMIT 5"
    cursor.execute(query, tuple(params))
    questoes = cursor.fetchall()

    if not questoes:
        flash('Não há questões disponíveis para esta combinação.', 'warning')
        return redirect(url_for('quiz'))

    questoes_com_alternativas = []
    for q in questoes:
        cursor.execute("SELECT id, texto FROM alternativas WHERE questao_id = %s", (q[0],))
        alternativas = cursor.fetchall()
        questoes_com_alternativas.append({
            'id': q[0],
            'enunciado': q[1],
            'alternativas': alternativas
        })

    return render_template('quiz.html',
                           questoes=questoes_com_alternativas,
                           nivel_id=nivel_id_raw,
                           assunto_nome=assunto_nome)



#rota para enviar questões no bd
@app.route('/gerenciar_questoes')
@login_required
@professor_required
def gerenciar_questoes():
    professor_id = session.get('usuario_id')
    cursor = mysql.connection.cursor()

    # Questões do professor
    cursor.execute("""
        SELECT q.id, q.enunciado, n.descricao AS nivel, a.nome AS assunto
        FROM questoes q
        JOIN niveis_dificuldade n ON q.nivel_id = n.id
        JOIN assuntos a ON q.assunto_id = a.id
        WHERE q.autor_id = %s
    """, (professor_id,))
    questoes = cursor.fetchall()

    # Carregar listas para o modal
    cursor.execute("SELECT id, descricao FROM niveis_dificuldade")
    niveis = cursor.fetchall()
    cursor.execute("SELECT id, nome FROM assuntos")
    assuntos = cursor.fetchall()

    return render_template('gerenciar_questoes.html',
                           nome=session['usuario_nome'],
                           questoes=questoes,
                           niveis=niveis,
                           assuntos=assuntos)



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


@app.route('/quiz_resultado/<int:tentativa_id>')
@login_required
@aluno_required
def quiz_resultado(tentativa_id):
    aluno_id = session['usuario_id']
    cursor = mysql.connection.cursor()

    # agora aceita nivel_id NULL (variado)
    cursor.execute("""
        SELECT t.nivel_id, n.descricao
        FROM tentativas_quiz t
        LEFT JOIN niveis_dificuldade n ON t.nivel_id = n.id
        WHERE t.id = %s AND t.aluno_id = %s
    """, (tentativa_id, aluno_id))
    tentativa = cursor.fetchone()

    if not tentativa:
        flash("Tentativa inválida ou acesso negado.", "danger")
        return redirect(url_for('index_aluno'))

    nivel_id = tentativa[0]  # pode ser None
    nivel_descricao = tentativa[1] if tentativa[1] else "Variada"

    cursor.execute("""
        SELECT q.enunciado, a.texto AS resposta_marcada, alt.texto AS resposta_correta, ra.correta
        FROM respostas_alunos ra
        JOIN questoes q ON ra.questao_id = q.id
        JOIN alternativas a ON ra.alternativa_id = a.id
        JOIN alternativas alt ON alt.questao_id = q.id AND alt.correta = 1
        WHERE ra.tentativa_id = %s
    """, (tentativa_id,))
    resultados = cursor.fetchall()

    total = len(resultados)
    acertos = sum(1 for r in resultados if r[3] == 1)
    erros = total - acertos

    return render_template(
        "quiz_resultado.html",
        total=total,
        acertos=acertos,
        erros=erros,
        resultados=resultados,
        nivel_descricao=nivel_descricao
    )

@app.route('/desempenho')
@login_required
@aluno_required
def desempenho():
    aluno_id = session['usuario_id']
    cursor = mysql.connection.cursor()

    assunto_id = request.args.get('assunto')
    nivel_id = request.args.get('nivel')
    tempo_min = request.args.get('tempo_min')
    tempo_max = request.args.get('tempo_max')
    data_inicio = request.args.get('inicio')
    data_fim = request.args.get('fim')

    base_query = """
        FROM respostas_alunos ra
        JOIN tentativas_quiz tq ON ra.tentativa_id = tq.id
        JOIN questoes q ON ra.questao_id = q.id
        WHERE tq.aluno_id = %s
    """
    params = [aluno_id]
    
    filters = []
    
    if assunto_id and assunto_id != "todos":
        filters.append("q.assunto_id = %s")
        params.append(assunto_id)
    
    if nivel_id and nivel_id != "todos":
        if nivel_id == "variada":
            filters.append("tq.nivel_id IS NULL")
        else:
            filters.append("tq.nivel_id = %s")
            params.append(nivel_id)

    
    if tempo_min:
        try:
            filters.append("tq.tempo_gasto >= %s")
            params.append(int(tempo_min) * 60)  
        except ValueError:
            flash('Tempo mínimo inválido', 'warning')
    
    if tempo_max:
        try:
            filters.append("tq.tempo_gasto <= %s")
            params.append(int(tempo_max) * 60)  
        except ValueError:
            flash('Tempo máximo inválido', 'warning')
    
    if data_inicio:
        filters.append("tq.data_hora >= %s")
        params.append(f"{data_inicio} 00:00:00")
    
    if data_fim:
        filters.append("tq.data_hora < DATE_ADD(%s, INTERVAL 1 DAY)")
        params.append(data_fim)
    
    query_totais = f"""
        SELECT 
            COUNT(*) AS total_questoes,
            SUM(CASE WHEN ra.correta = 1 THEN 1 ELSE 0 END) AS acertos,
            SUM(CASE WHEN ra.correta = 0 THEN 1 ELSE 0 END) AS erros
        {base_query}
    """
    if filters:
        query_totais += " AND " + " AND ".join(filters)
    
    query_tentativas = f"""
        SELECT 
            tq.id,
            DATE_FORMAT(tq.data_hora, '%%d/%%m/%%Y') AS data,
            DATE_FORMAT(tq.data_hora, '%%H:%%i') AS hora,
            SUM(CASE WHEN ra.correta = 1 THEN 1 ELSE 0 END) AS acertos,
            tq.tempo_gasto,
            nd.descricao AS nivel
        FROM tentativas_quiz tq
        LEFT JOIN respostas_alunos ra ON ra.tentativa_id = tq.id
        LEFT JOIN questoes q ON ra.questao_id = q.id
        LEFT JOIN niveis_dificuldade nd ON tq.nivel_id = nd.id
        WHERE tq.aluno_id = %s
    """
    tentativas_params = [aluno_id]
    
    if filters:
        query_tentativas += " AND " + " AND ".join(filters)
        tentativas_params.extend(params[1:])

    query_tentativas += " GROUP BY tq.id, data, hora, tq.tempo_gasto, nivel ORDER BY tq.data_hora"

    # Executar consultas
    try:
        cursor.execute(query_totais, tuple(params))
        resultados = cursor.fetchone() or (0, 0, 0)
        total_questoes = resultados[0] or 0
        acertos = resultados[1] or 0
        erros = resultados[2] or 0

        cursor.execute(query_tentativas, tuple(tentativas_params))
        tentativas = cursor.fetchall()
    except Exception as e:
        flash(f'Erro ao filtrar resultados: {str(e)}', 'danger')
        return redirect(url_for('desempenho'))

    labels = [f"{r[1]} {r[2]}" for r in tentativas]
    data = [int(r[3] or 0) for r in tentativas]

    cursor.execute("SELECT id, nome FROM assuntos ORDER BY nome")
    assuntos = cursor.fetchall()
    
    cursor.execute("SELECT id, descricao FROM niveis_dificuldade ORDER BY id")
    niveis = cursor.fetchall()

    return render_template('desempenho.html',
                         total=total_questoes,
                         acertos=acertos,
                         erros=erros,
                         tentativas=tentativas,
                         labels=labels,
                         data=data,
                         assuntos=assuntos,
                         niveis=niveis,
                         filtro_assunto=(assunto_id or "todos"),
                         filtro_nivel=(nivel_id or "todos"),
                         filtro_tempo_min=(tempo_min or ""),
                         filtro_tempo_max=(tempo_max or ""),
                         filtro_inicio=(data_inicio or ""),
                         filtro_fim=(data_fim or ""))

@app.route('/editar_questao/<int:questao_id>', methods=['GET', 'POST'])
@login_required
@professor_required
def editar_questao(questao_id):
    professor_id = session['usuario_id']
    cursor = mysql.connection.cursor()

    cursor.execute("SELECT enunciado, nivel_id, assunto_id FROM questoes WHERE id = %s AND autor_id = %s", (questao_id, professor_id))
    questao = cursor.fetchone()
    if not questao:
        flash("Questão não encontrada ou acesso negado.", "danger")
        return redirect(url_for('gerenciar_questoes'))

    if request.method == 'POST':
        novo_enunciado = request.form.get('enunciado')
        nivel_id = request.form.get('nivel_id')
        assunto_id = request.form.get('assunto_id')
        alternativas = request.form.getlist('alternativas')
        correta_index = int(request.form.get('correta_index')) - 1

        cursor.execute("""
            UPDATE questoes SET enunciado = %s, nivel_id = %s, assunto_id = %s WHERE id = %s
        """, (novo_enunciado, nivel_id, assunto_id, questao_id))

        cursor.execute("DELETE FROM alternativas WHERE questao_id = %s", (questao_id,))


        for i, texto in enumerate(alternativas):
            correta = 1 if i == correta_index else 0
            cursor.execute("""
                INSERT INTO alternativas (questao_id, texto, correta)
                VALUES (%s, %s, %s)
            """, (questao_id, texto, correta))

        mysql.connection.commit()
        flash("Questão atualizada com sucesso!", "success")
        return redirect(url_for('gerenciar_questoes'))

    cursor.execute("SELECT descricao, id FROM niveis_dificuldade")
    niveis = cursor.fetchall()
    cursor.execute("SELECT nome, id FROM assuntos")
    assuntos = cursor.fetchall()
    cursor.execute("SELECT id, texto, correta FROM alternativas WHERE questao_id = %s", (questao_id,))
    alternativas = cursor.fetchall()

    return render_template('editar_questao.html', questao_id=questao_id,questao=questao,alternativas=alternativas,niveis=niveis,assuntos=assuntos)

@app.route('/excluir_questao/<int:questao_id>', methods=['POST'])
@login_required
@professor_required
def excluir_questao(questao_id):
    professor_id = session['usuario_id']
    cursor = mysql.connection.cursor()

    cursor.execute("SELECT id FROM questoes WHERE id = %s AND autor_id = %s", (questao_id, professor_id))
    questao = cursor.fetchone()

    if not questao:
        flash("Questão não encontrada ou acesso negado.", "danger")
        return redirect(url_for('gerenciar_questoes'))


    cursor.execute("DELETE FROM alternativas WHERE questao_id = %s", (questao_id,))
    cursor.execute("DELETE FROM questoes WHERE id = %s", (questao_id,))
    mysql.connection.commit()

    flash("Questão excluída com sucesso.", "success")
    return redirect(url_for('gerenciar_questoes'))

@app.route("/relatorio_alunos")
@login_required
@professor_required
def relatorio_alunos():
    cur = mysql.connection.cursor()

    # Médias gerais da turma
    cur.execute("""
        SELECT 
            COALESCE(AVG(CASE WHEN ra.correta = 1 THEN 1 ELSE 0 END) * 100, 0) AS media_acertos_percentual,
            COALESCE(AVG(CASE WHEN ra.correta = 0 THEN 1 ELSE 0 END) * 100, 0) AS media_erros_percentual,
            COALESCE(AVG(t.tempo_gasto), 0) AS media_tempo
        FROM respostas_alunos ra
        JOIN tentativas_quiz t ON ra.tentativa_id = t.id
        WHERE ra.correta IS NOT NULL;
    """)
    medias = cur.fetchone() or (0, 0, 0)

    # Desempenho por aluno
    cur.execute("""
        SELECT 
            u.id AS aluno_id,
            u.nome,
            c.nome AS curso,
            COUNT(DISTINCT t.id) AS total_quizzes,
            COALESCE(ROUND(SUM(CASE WHEN ra.correta = 1 THEN 1 ELSE 0 END) / NULLIF(COUNT(ra.id), 0) * 100, 2), 0) AS media_acertos_percentual,
            COALESCE(ROUND(SUM(CASE WHEN ra.correta = 0 THEN 1 ELSE 0 END) / NULLIF(COUNT(ra.id), 0) * 100, 2), 0) AS media_erros_percentual,
            COALESCE(ROUND(AVG(t.tempo_gasto), 2), 0) AS tempo_medio
        FROM usuarios u
        LEFT JOIN alunos a ON u.id = a.id
        LEFT JOIN cursos c ON a.curso_id = c.id
        LEFT JOIN tentativas_quiz t ON a.id = t.aluno_id
        LEFT JOIN respostas_alunos ra ON t.id = ra.tentativa_id
        WHERE u.tipo = 'aluno'
        GROUP BY u.id, u.nome, c.nome
        ORDER BY u.nome;
    """)
    alunos = cur.fetchall()

    # Dados para os gráficos
    # 1. Distribuição de desempenho (labels e data para o gráfico de barras)
    cur.execute("""
        SELECT 
            CONCAT(u.nome, ' - ', DATE_FORMAT(MAX(t.data_hora), '%%d/%%m')) as label,
            SUM(CASE WHEN ra.correta = 1 THEN 1 ELSE 0 END) as acertos
        FROM usuarios u
        JOIN alunos a ON u.id = a.id
        JOIN tentativas_quiz t ON a.id = t.aluno_id
        JOIN respostas_alunos ra ON t.id = ra.tentativa_id
        GROUP BY u.id
        ORDER BY t.data_hora DESC
        LIMIT 10;
    """)
    
    resultados_grafico = cur.fetchall()
    labels = [r[0] for r in resultados_grafico]
    data = [r[1] for r in resultados_grafico]
    
    # 2. Médias por curso para o gráfico de pizza
    cur.execute("""
        SELECT 
            c.nome AS curso,
            COALESCE(ROUND(AVG(CASE WHEN ra.correta = 1 THEN 1 ELSE 0 END) * 100, 2), 0) AS media_acertos
        FROM cursos c
        LEFT JOIN alunos a ON c.id = a.curso_id
        LEFT JOIN usuarios u ON a.id = u.id
        LEFT JOIN tentativas_quiz t ON a.id = t.aluno_id
        LEFT JOIN respostas_alunos ra ON t.id = ra.tentativa_id
        GROUP BY c.id, c.nome;
    """)
    
    medias_por_curso = cur.fetchall()
    cursos_labels = [r[0] for r in medias_por_curso]
    cursos_data = [r[1] for r in medias_por_curso]

    cur.close()

    return render_template("relatorio_geral.html", 
                         medias=medias, 
                         alunos=alunos,
                         labels=labels,
                         data=data,
                         cursos_labels=cursos_labels,
                         cursos_data=cursos_data,
                         acertos=sum(data) if data else 0,
                         erros=sum([max(5 - d, 0) for d in data]) if data else 0)  # Assumindo 5 questões por quiz



# -----------------------
# RELATÓRIO INDIVIDUAL
# -----------------------
@app.route("/relatorio_aluno/<int:aluno_id>")
@login_required
@professor_required
def relatorio_aluno(aluno_id):
    cur = mysql.connection.cursor()

    # Verificar se o aluno existe e obter informações completas
    cur.execute("""
        SELECT u.id, u.nome, u.email, c.nome as curso
        FROM usuarios u
        JOIN alunos a ON u.id = a.id
        JOIN cursos c ON a.curso_id = c.id
        WHERE u.id = %s AND u.tipo = 'aluno'
    """, (aluno_id,))
    aluno_info = cur.fetchone()
    
    if not aluno_info:
        flash("Aluno não encontrado.", "danger")
        return redirect(url_for('relatorio_alunos'))

    # Estatísticas do aluno
    cur.execute("""
        SELECT 
            COUNT(DISTINCT t.id) AS total_quizzes,
            COALESCE(ROUND(SUM(CASE WHEN ra.correta = 1 THEN 1 ELSE 0 END) / NULLIF(COUNT(ra.id), 0) * 100, 2), 0) AS taxa_acertos,
            COALESCE(ROUND(AVG(t.tempo_gasto), 2), 0) AS tempo_medio,
            MIN(t.data_hora) AS primeira_tentativa,
            MAX(t.data_hora) AS ultima_tentativa
        FROM usuarios u
        LEFT JOIN alunos a ON u.id = a.id
        LEFT JOIN tentativas_quiz t ON a.id = t.aluno_id
        LEFT JOIN respostas_alunos ra ON t.id = ra.tentativa_id
        WHERE u.id = %s
    """, (aluno_id,))
    estatisticas = cur.fetchone() or (0, 0, 0, None, None)

    # Detalhes das tentativas
    cur.execute("""
        SELECT 
            t.id AS tentativa_id,
            t.data_hora,
            t.tempo_gasto,
            n.descricao AS nivel,
            COALESCE(a.nome, 'Todos os assuntos') AS assunto,
            SUM(CASE WHEN ra.correta = 1 THEN 1 ELSE 0 END) AS acertos,
            SUM(CASE WHEN ra.correta = 0 THEN 1 ELSE 0 END) AS erros,
            COUNT(ra.id) AS total_questoes,
            COALESCE(ROUND(SUM(CASE WHEN ra.correta = 1 THEN 1 ELSE 0 END) / NULLIF(COUNT(ra.id), 0) * 100, 2), 0) AS percentual_acerto
        FROM tentativas_quiz t
        JOIN niveis_dificuldade n ON t.nivel_id = n.id
        LEFT JOIN assuntos a ON t.assunto_id = a.id
        LEFT JOIN respostas_alunos ra ON t.id = ra.tentativa_id
        WHERE t.aluno_id = %s
        GROUP BY t.id, t.data_hora, t.tempo_gasto, n.descricao, a.nome
        ORDER BY t.data_hora DESC;
    """, (aluno_id,))
    
    tentativas = cur.fetchall()

    # Estatísticas por assunto (acertos e erros)
    cur.execute("""
        SELECT 
            COALESCE(a.nome, 'Todos os assuntos') AS assunto,
            COUNT(ra.id) AS total_questoes,
            SUM(CASE WHEN ra.correta = 1 THEN 1 ELSE 0 END) AS acertos,
            SUM(CASE WHEN ra.correta = 0 THEN 1 ELSE 0 END) AS erros,
            ROUND(SUM(CASE WHEN ra.correta = 1 THEN 1 ELSE 0 END) / NULLIF(COUNT(ra.id), 0) * 100, 2) AS percentual_acerto
        FROM respostas_alunos ra
        JOIN tentativas_quiz t ON ra.tentativa_id = t.id
        JOIN questoes q ON ra.questao_id = q.id
        LEFT JOIN assuntos a ON q.assunto_id = a.id
        WHERE t.aluno_id = %s
        GROUP BY a.id, a.nome
        ORDER BY total_questoes DESC, percentual_acerto DESC;
    """, (aluno_id,))
    
    estatisticas_assuntos = cur.fetchall()

    # Assuntos com melhor desempenho (top 3)
    cur.execute("""
        SELECT 
            COALESCE(a.nome, 'Todos os assuntos') AS assunto,
            ROUND(SUM(CASE WHEN ra.correta = 1 THEN 1 ELSE 0 END) / NULLIF(COUNT(ra.id), 0) * 100, 2) AS percentual_acerto,
            COUNT(ra.id) AS total_questoes
        FROM respostas_alunos ra
        JOIN tentativas_quiz t ON ra.tentativa_id = t.id
        JOIN questoes q ON ra.questao_id = q.id
        LEFT JOIN assuntos a ON q.assunto_id = a.id
        WHERE t.aluno_id = %s
        GROUP BY a.id, a.nome
        HAVING total_questoes >= 3
        ORDER BY percentual_acerto DESC
        LIMIT 3;
    """, (aluno_id,))
    
    melhores_assuntos = cur.fetchall()

    # Assuntos com pior desempenho (top 3)
    cur.execute("""
        SELECT 
            COALESCE(a.nome, 'Todos os assuntos') AS assunto,
            ROUND(SUM(CASE WHEN ra.correta = 1 THEN 1 ELSE 0 END) / NULLIF(COUNT(ra.id), 0) * 100, 2) AS percentual_acerto,
            COUNT(ra.id) AS total_questoes
        FROM respostas_alunos ra
        JOIN tentativas_quiz t ON ra.tentativa_id = t.id
        JOIN questoes q ON ra.questao_id = q.id
        LEFT JOIN assuntos a ON q.assunto_id = a.id
        WHERE t.aluno_id = %s
        GROUP BY a.id, a.nome
        HAVING total_questoes >= 3
        ORDER BY percentual_acerto ASC
        LIMIT 3;
    """, (aluno_id,))
    
    piores_assuntos = cur.fetchall()

    cur.close()

    return render_template("relatorio_aluno.html", 
                         aluno_info=aluno_info,
                         estatisticas=estatisticas,
                         tentativas=tentativas,
                         estatisticas_assuntos=estatisticas_assuntos,
                         melhores_assuntos=melhores_assuntos,
                         piores_assuntos=piores_assuntos)

# GERENCIAR QUESTÕES - ADM
@app.route('/gerenciar_questoes_adm')
@login_required
@adm_required
def gerenciar_questoes_adm():
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT q.id, q.enunciado, n.descricao AS nivel, a.nome AS assunto, u.nome AS autor
        FROM questoes q
        JOIN niveis_dificuldade n ON q.nivel_id = n.id
        JOIN assuntos a ON q.assunto_id = a.id
        JOIN usuarios u ON q.autor_id = u.id
    """)
    questoes = cursor.fetchall()

    cursor.execute("SELECT id, descricao FROM niveis_dificuldade")
    niveis = cursor.fetchall()
    cursor.execute("SELECT id, nome FROM assuntos")
    assuntos = cursor.fetchall()

    return render_template('gerenciar_questoes_adm.html',
                           questoes=questoes,
                           niveis=niveis,
                           assuntos=assuntos)

# EDITAR QUESTÃO - ADM
@app.route('/editar_questao_adm/<int:questao_id>', methods=['GET', 'POST'])
@login_required
@adm_required
def editar_questao_adm(questao_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT enunciado, nivel_id, assunto_id FROM questoes WHERE id = %s", (questao_id,))
    questao = cursor.fetchone()
    if not questao:
        flash("Questão não encontrada.", "danger")
        return redirect(url_for('gerenciar_questoes_adm'))

    if request.method == 'POST':
        novo_enunciado = request.form.get('enunciado')
        nivel_id = request.form.get('nivel_id')
        assunto_id = request.form.get('assunto_id')
        alternativas = request.form.getlist('alternativas')
        correta_index = int(request.form.get('correta_index')) - 1

        cursor.execute("""
            UPDATE questoes SET enunciado = %s, nivel_id = %s, assunto_id = %s WHERE id = %s
        """, (novo_enunciado, nivel_id, assunto_id, questao_id))

        cursor.execute("DELETE FROM alternativas WHERE questao_id = %s", (questao_id,))
        for i, texto in enumerate(alternativas):
            correta = 1 if i == correta_index else 0
            cursor.execute("""
                INSERT INTO alternativas (questao_id, texto, correta)
                VALUES (%s, %s, %s)
            """, (questao_id, texto, correta))

        mysql.connection.commit()
        flash("Questão atualizada com sucesso!", "success")
        return redirect(url_for('gerenciar_questoes_adm'))

    cursor.execute("SELECT descricao, id FROM niveis_dificuldade")
    niveis = cursor.fetchall()
    cursor.execute("SELECT nome, id FROM assuntos")
    assuntos = cursor.fetchall()
    cursor.execute("SELECT id, texto, correta FROM alternativas WHERE questao_id = %s", (questao_id,))
    alternativas = cursor.fetchall()

    return render_template('editar_questao_adm.html', 
                           questao_id=questao_id,
                           questao=questao,
                           alternativas=alternativas,
                           niveis=niveis,
                           assuntos=assuntos)


# EXCLUIR QUESTÃO - ADM
@app.route('/excluir_questao_adm/<int:questao_id>', methods=['POST'])
@login_required
@adm_required
def excluir_questao_adm(questao_id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM alternativas WHERE questao_id = %s", (questao_id,))
    cursor.execute("DELETE FROM questoes WHERE id = %s", (questao_id,))
    mysql.connection.commit()

    flash("Questão excluída com sucesso.", "success")
    return redirect(url_for('gerenciar_questoes_adm'))


if __name__ == '__main__':
    app.run(debug=True)
