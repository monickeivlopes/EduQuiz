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

    # Buscar questões criadas pelo professor
    cursor.execute("""
        SELECT q.id, q.enunciado, n.descricao AS nivel, a.nome AS assunto
        FROM questoes q
        JOIN niveis_dificuldade n ON q.nivel_id = n.id
        JOIN assuntos a ON q.assunto_id = a.id
        WHERE q.autor_id = %s
    """, (usuario_id,))
    questoes = cursor.fetchall()

    return render_template('index_professor.html', nome=nome, questoes=questoes)


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
@app.route('/materiais')
@login_required
@aluno_required
def materiais():
    data_filtro = request.args.get('data')  # formato YYYY-MM-DD
    ordem = request.args.get('ordem', 'desc')  # 'asc' ou 'desc'

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

    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)

    if ordem.lower() == 'asc':
        query += " ORDER BY m.data_publicacao ASC"
    else:
        query += " ORDER BY m.data_publicacao DESC"

    cursor.execute(query, tuple(params))
    materiais = cursor.fetchall()

    return render_template(
        'materiais.html',
        materiais=materiais,
        data_filtro=data_filtro,
        ordem=ordem
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
            # Obter dados do formulário
            respostas = request.form.to_dict()
            aluno_id = session.get('usuario_id')
            nivel_id = int(respostas.pop('nivel_id'))
            assunto_id = respostas.pop('assunto_id', 'todos').strip()

            # assunto_id pode ser 'todos' (NULL)
            if assunto_id == 'todos' or assunto_id == '':
                assunto_id_value = None
            else:
                try:
                    assunto_id_value = int(assunto_id)
                    cursor.execute("SELECT id FROM assuntos WHERE id = %s", (assunto_id_value,))
                    if not cursor.fetchone():
                        flash('Assunto selecionado não existe', 'danger')
                        return redirect(url_for('index_aluno'))
                except ValueError:
                    flash('Valor de assunto inválido', 'danger')
                    return redirect(url_for('index_aluno'))

            # Verificar aluno
            cursor.execute("SELECT id FROM alunos WHERE id = %s", (aluno_id,))
            if not cursor.fetchone():
                flash('Aluno não encontrado', 'danger')
                return redirect(url_for('index_aluno'))

            # Inserir tentativa (data_hora tem DEFAULT CURRENT_TIMESTAMP)
            cursor.execute("""
                INSERT INTO tentativas_quiz (aluno_id, nivel_id, assunto_id)
                VALUES (%s, %s, %s)
            """, (aluno_id, nivel_id, assunto_id_value))
            tentativa_id = cursor.lastrowid

            # Processar respostas
            for questao_id_str, alternativa_id in respostas.items():
                if questao_id_str in ['nivel_id', 'assunto_id']:
                    continue
                questao_id = int(questao_id_str)
                cursor.execute("SELECT correta FROM alternativas WHERE id = %s", (alternativa_id,))
                correta = cursor.fetchone()[0]
                cursor.execute("""
                    INSERT INTO respostas_alunos (tentativa_id, questao_id, alternativa_id, correta)
                    VALUES (%s, %s, %s, %s)
                """, (tentativa_id, questao_id, alternativa_id, correta))

            # === NEW: calcular tempo_gasto ===
            from datetime import datetime
            fim_quiz = datetime.now()
            inicio_quiz = session.pop('inicio_quiz', None)

            tempo_gasto = None
            if inicio_quiz:
                try:
                    # inicio_quiz veio como datetime; se vier string, converta
                    if isinstance(inicio_quiz, str):
                        # fallback seguro caso o servidor serialize
                        from datetime import datetime
                        # tente formatos comuns
                        for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
                            try:
                                inicio_quiz = datetime.strptime(inicio_quiz, fmt)
                                break
                            except:
                                pass
                    tempo_gasto = int((fim_quiz - inicio_quiz).total_seconds())
                except Exception:
                    tempo_gasto = None

            if tempo_gasto is not None:
                cursor.execute("""
                    UPDATE tentativas_quiz
                    SET tempo_gasto = %s
                    WHERE id = %s
                """, (tempo_gasto, tentativa_id))

            mysql.connection.commit()
            return redirect(url_for('quiz_resultado', tentativa_id=tentativa_id))

        except Exception as e:
            mysql.connection.rollback()
            flash(f'Erro ao processar quiz: {str(e)}', 'danger')
            return redirect(url_for('index_aluno'))

    # ===== GET: exibe quiz =====
    if 'nivel_id' not in request.args:
        cursor.execute("SELECT id, descricao FROM niveis_dificuldade")
        niveis = cursor.fetchall()
        cursor.execute("SELECT id, nome FROM assuntos")
        assuntos = cursor.fetchall()
        return render_template('quiz_inicio.html', niveis=niveis, assuntos=assuntos)

    nivel_id = int(request.args['nivel_id'])
    assunto_id = request.args.get('assunto_id', 'todos')

    # Nome do assunto para exibição
    assunto_nome = 'Todos os assuntos'
    if assunto_id != 'todos':
        cursor.execute("SELECT nome FROM assuntos WHERE id = %s", (assunto_id,))
        resultado = cursor.fetchone()
        if resultado:
            assunto_nome = resultado[0]

    # Buscar questões
    query = """
        SELECT q.id, q.enunciado 
        FROM questoes q
        WHERE q.nivel_id = %s
    """
    params = [nivel_id]
    if assunto_id != 'todos':
        query += " AND q.assunto_id = %s"
        params.append(assunto_id)
    query += " ORDER BY RAND() LIMIT 5"
    cursor.execute(query, tuple(params))
    questoes = cursor.fetchall()

    if not questoes:
        flash('Não há questões disponíveis para esta combinação.', 'warning')
        return redirect(url_for('quiz'))

    # Alternativas
    questoes_com_alternativas = []
    for q in questoes:
        cursor.execute("SELECT id, texto FROM alternativas WHERE questao_id = %s", (q[0],))
        alternativas = cursor.fetchall()
        questoes_com_alternativas.append({
            'id': q[0],
            'enunciado': q[1],
            'alternativas': alternativas
        })

    # === NEW: marcar início do quiz para cronometrar ===
    from datetime import datetime
    session['inicio_quiz'] = datetime.now()

    return render_template('quiz.html',
                           questoes=questoes_com_alternativas,
                           nivel_id=nivel_id,
                           assunto_nome=assunto_nome)




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


@app.route('/quiz_resultado/<int:tentativa_id>')
@login_required
@aluno_required
def quiz_resultado(tentativa_id):
    aluno_id = session['usuario_id']
    cursor = mysql.connection.cursor()

    cursor.execute("SELECT nivel_id FROM tentativas_quiz WHERE id = %s AND aluno_id = %s", (tentativa_id, aluno_id))
    tentativa = cursor.fetchone()
    if not tentativa:
        flash("Tentativa inválida ou acesso negado.", "danger")
        return redirect(url_for('index_aluno'))
    
    nivel_id = tentativa[0]  

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

    return render_template("quiz_resultado.html",
                           total=total,
                           acertos=acertos,
                           erros=erros,
                           resultados=resultados,
                           nivel_id=nivel_id)  

@app.route('/desempenho')
@login_required
@aluno_required
def desempenho():
    aluno_id = session['usuario_id']
    cursor = mysql.connection.cursor()

    # Parâmetros (querystring ?assunto=...&inicio=YYYY-MM-DD&fim=YYYY-MM-DD)
    assunto = request.args.get('assunto')      # id ou "todos"
    data_inicio = request.args.get('inicio')   # 'YYYY-MM-DD'
    data_fim = request.args.get('fim')         # 'YYYY-MM-DD'

    filtros = "WHERE tq.aluno_id = %s"
    params = [aluno_id]

    if assunto and assunto != "todos":
        filtros += " AND tq.assunto_id = %s"
        params.append(assunto)

    if data_inicio:
        filtros += " AND tq.data_hora >= %s"
        params.append(f"{data_inicio} 00:00:00")

    if data_fim:
        # fim inclusivo
        filtros += " AND tq.data_hora < DATE_ADD(%s, INTERVAL 1 DAY)"
        params.append(data_fim)

    # Totais
    cursor.execute(f"""
        SELECT 
            COUNT(*) AS total_questoes,
            SUM(CASE WHEN ra.correta = 1 THEN 1 ELSE 0 END) AS acertos,
            SUM(CASE WHEN ra.correta = 0 THEN 1 ELSE 0 END) AS erros
        FROM respostas_alunos ra
        JOIN tentativas_quiz tq ON ra.tentativa_id = tq.id
        {filtros}
    """, params)
    resultados = cursor.fetchone() or (0, 0, 0)

    total_questoes = resultados[0] or 0
    acertos = resultados[1] or 0
    erros = resultados[2] or 0

    # Tentativas (com tempo_gasto)
    cursor.execute(f"""
        SELECT 
            tq.id,
            DATE_FORMAT(tq.data_hora, '%%d/%%m/%%Y') AS data,
            DATE_FORMAT(tq.data_hora, '%%H:%%i') AS hora,
            SUM(CASE WHEN ra.correta = 1 THEN 1 ELSE 0 END) AS acertos,
            tq.tempo_gasto
        FROM tentativas_quiz tq
        LEFT JOIN respostas_alunos ra ON ra.tentativa_id = tq.id
        {filtros}
        GROUP BY tq.id, data, hora, tq.tempo_gasto
        ORDER BY tq.data_hora
    """, params)
    tentativas = cursor.fetchall()

    labels = [f"{r[1]} {r[2]}" for r in tentativas]
    data = [int(r[3] or 0) for r in tentativas]

    # Assuntos para o <select>
    cursor.execute("SELECT id, nome FROM assuntos ORDER BY nome")
    assuntos = cursor.fetchall()

    return render_template('desempenho.html',
                           total=total_questoes,
                           acertos=acertos,
                           erros=erros,
                           tentativas=tentativas,
                           labels=labels,
                           data=data,
                           assuntos=assuntos,
                           filtro_assunto=(assunto or "todos"),
                           filtro_inicio=(data_inicio or ""),
                           filtro_fim=(data_fim or ""))

    aluno_id = session['usuario_id']
    cursor = mysql.connection.cursor()

    # Parâmetros de filtro
    tema = request.args.get('tema')
    data_inicio = request.args.get('inicio')
    data_fim = request.args.get('fim')

    filtros = "WHERE tq.aluno_id = %s"
    params = [aluno_id]

    if tema and tema != "todos":
        filtros += " AND tq.tema_id = %s"
        params.append(tema)

    if data_inicio:
        filtros += " AND tq.data_hora >= %s"
        params.append(data_inicio)

    if data_fim:
        filtros += " AND tq.data_hora <= %s"
        params.append(data_fim)

    # Total geral filtrado
    cursor.execute(f"""
        SELECT 
            COUNT(*) AS total_questoes,
            SUM(CASE WHEN correta = 1 THEN 1 ELSE 0 END) AS acertos,
            SUM(CASE WHEN correta = 0 THEN 1 ELSE 0 END) AS erros
        FROM respostas_alunos ra
        JOIN tentativas_quiz tq ON ra.tentativa_id = tq.id
        {filtros}
    """, params)
    resultados = cursor.fetchone()

    total_questoes = resultados[0] or 0
    acertos = resultados[1] or 0
    erros = resultados[2] or 0

    # Lista de tentativas com tempo
    cursor.execute(f"""
        SELECT 
            tq.id,
            DATE_FORMAT(tq.data_hora, '%%d/%%m/%%Y') AS data,
            DATE_FORMAT(tq.data_hora, '%%H:%%i') AS hora,
            SUM(CASE WHEN ra.correta = 1 THEN 1 ELSE 0 END) AS acertos,
            tq.tempo_gasto
        FROM tentativas_quiz tq
        LEFT JOIN respostas_alunos ra ON ra.tentativa_id = tq.id
        {filtros}
        GROUP BY tq.id, data, hora, tq.tempo_gasto
        ORDER BY tq.data_hora
    """, params)
    tentativas = cursor.fetchall()

    labels = [f"{r[1]} {r[2]}" for r in tentativas]
    data = [r[3] for r in tentativas]

    # Lista de temas para o select
    cursor.execute("SELECT id, nome FROM temas")
    temas = cursor.fetchall()

    return render_template('desempenho.html',
                           total=total_questoes,
                           acertos=acertos,
                           erros=erros,
                           tentativas=tentativas,
                           labels=labels,
                           data=data,
                           temas=temas)

#EDITAR QUESTÕES - EXCLUIR

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

    return render_template('editar_questao.html',
                           questao_id=questao_id,
                           questao=questao,
                           alternativas=alternativas,
                           niveis=niveis,
                           assuntos=assuntos)

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



if __name__ == '__main__':
    app.run(debug=True)
