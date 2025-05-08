from flask import Flask, render_template, request, redirect
from flask_mysqldb import MySQL
import hashlib



app = Flask(__name__)

#Configuração do banco de dados
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  
app.config['MYSQL_PASSWORD'] = ''  
app.config['MYSQL_DB'] = 'Eduquiz'

mysql = MySQL(app)

#Rota da primeira página
@app.route("/")
def index():
    return render_template("index.html")

#Rota de cadastro
@app.route('/Cadastro', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        tipo = request.form['tipo']
        
        # Criptografar a senha
        senha_hash = hashlib.sha256(senha.encode()).hexdigest()

        # Inserir na tabela usuarios do BD
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO usuarios (nome, email, senha_hash, tipo) VALUES (%s, %s, %s, %s)', 
                       (nome, email, senha_hash, tipo))
        mysql.connection.commit()

        return redirect('/') 

    return render_template('register.html')


if __name__ == '__main__':
    app.run(debug=True)