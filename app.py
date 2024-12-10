from flask import Flask, request, render_template, session, redirect, url_for, make_response
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'chave-secreta'

# Configurações do banco de dados MySQL
DATABASE_CONFIG = {
    'host': 'localhost',  # Substitua pelo host do seu servidor MySQL
    'user': 'root',       # Substitua pelo usuário do banco de dados
    'password': 'senha',  # Substitua pela senha do banco de dados
    'database': 'database'  # Nome do banco de dados
}

# Conectar ao banco de dados MySQL
def conectar_banco():
    try:
        conn = mysql.connector.connect(**DATABASE_CONFIG)
        return conn
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return None

# Criar tabela no banco de dados
def criar_tabela():
    conn = conectar_banco()
    if conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                email VARCHAR(100) NOT NULL,
                tipo_usuario ENUM('professor', 'aluno') NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

# Inicializa o banco de dados ao iniciar a aplicação
criar_tabela()

@app.route("/")
def index():
    return render_template("index.html")

# ROTA LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']
        conn = conectar_banco()
        if conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM usuarios WHERE usuario = %s AND password = %s
            ''', (usuario, password))
            usuario = cursor.fetchone()
            conn.close()

            if usuario:
                session['usuario'] = {
                    'id': usuario[0],
                    'usuario': usuario[1],
                    'tipo_usuario': usuario[4]
                }
                if usuario[4] == 'professor':
                    return redirect(url_for('index_professor'))
                else:
                    return redirect(url_for('index_aluno'))

        return render_template('login.html', erro='Usuário ou senha inválidos.')

    if 'usuario' in session:
        if session['usuario']['tipo_usuario'] == 'professor':
            return redirect(url_for('index_professor'))
        return redirect(url_for('index_aluno'))

    return render_template('login.html')


@app.route("/recuperar-senha", methods=["GET", "POST"])
def recuperar_senha():
    return render_template("recuperar-senha.html")

# ROTA CADASTRO
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']
        email = request.form['email']
        tipo_usuario = request.form['tipo_usuario']
        try:
            conn = conectar_banco()
            if conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO usuarios (usuario, password, email, tipo_usuario)
                    VALUES (%s, %s, %s, %s)
                ''', (usuario, password, email, tipo_usuario))
                conn.commit()
                conn.close()
                return redirect(url_for('login'))
        except mysql.connector.Error as e:
            return render_template('register.html', erro='Erro ao cadastrar: ' + str(e))
    return render_template('register.html')


@app.route("/index_prof")
def index_professor():
    if 'usuario' in session and session['usuario']['tipo_usuario'] == 'professor':
        return render_template('index_prof.html', nome=session['usuario']['usuario'])
    return redirect(url_for('login'))

@app.route("/index_alu")
def index_aluno():
    if 'usuario' in session and session['usuario']['tipo_usuario'] == 'aluno':
        return render_template('index_alu.html', nome=session['usuario']['usuario'])
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
