from flask import Flask, request, render_template, session, redirect, url_for, make_response
import sqlite3

app = Flask(__name__)
app.secret_key = 'chave-secreta'


DATABASE = 'database.db'

def conectar_banco():
    return sqlite3.connect(DATABASE)

def criar_tabela():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT NOT NULL,
            tipo_usuario TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Inicializa o banco de dados ao iniciar a aplicação
criar_tabela()


@app.route("/")
def index():
    return render_template("index.html")

#ROTA LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']
        conn = conectar_banco()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM usuarios WHERE usuario = ? AND password = ? ''', (usuario, password))
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



#ROTA CADASTRO
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']
        email = request.form['email']
        tipo_usuario = request.form['tipo_usuario']
        try:
            conn = conectar_banco()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO usuarios (usuario, password, email, tipo_usuario)
                VALUES (?, ?, ?, ?)
            ''', (usuario, password, email, tipo_usuario))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return render_template('register.html', erro='Usuário já cadastrado.')
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
