from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy.orm import Session 
from sqlalchemy import create_engine
from models import Base,User
from flask import flash
import secrets  
from flask_mail import Mail, Message




#Criando bd
engine = create_engine('sqlite:///database.db')

Base.metadata.create_all(bind=engine)
session = Session(bind=engine)

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")

#ROTA LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        usuario = User.query.filter_by(email=email, password=password).first()

        if usuario:
            if usuario.tipo_usuario == "aluno":
                return redirect(url_for("index_alu"))

            elif usuario.tipo_usuario == "professor":
                return redirect(url_for("index_prof"))

        else:
            return "Usuário ou senha inválidos"

    return render_template("login.html")



#ROTA DE RECUPERAÇÃO DE SENHA
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'seuemail@gmail.com'
app.config['MAIL_PASSWORD'] = 'suasenha'
mail = Mail(app)

@app.route("/recuperar-senha", methods=["GET", "POST"])
def recuperar_senha():
    if request.method == "POST":
        email = request.form["email"]
        usuario = session.query(User).filter_by(email=email).first()
        
        if usuario:
            # Gerar token de recuperação
            token = secrets.token_urlsafe(16)
            usuario.recovery_token = token
            session.commit()

            # Enviar email com o link
            msg = Message("Recuperação de senha", sender="seuemail@gmail.com", recipients=[email])
            msg.body = f"Para redefinir sua senha, clique no link abaixo:\n\n{request.host_url}redefinir-senha/{token}"
            mail.send(msg)

            flash("Um email foi enviado com instruções para redefinir sua senha.")
        else:
            flash("Email não encontrado.")

        return redirect(url_for("login"))
    return render_template("recuperar-senha.html")



#ROTA CADASTRO
@app.route("/register", methods=['GET','POST'])
def register():
    if request.method == 'POST':
        usuario = request.form['usuario']
        email = request.form['email']
        password = request.form['password']
        tipo_usuario = request.form['tipo_usuario']

        user = User(usuario=usuario, password=password, email=email, tipo_usuario=tipo_usuario)
        session.add(user)
        session.commit()

        return redirect(url_for('login'))
    return render_template('register.html')


if __name__ == "__main__":
    app.run(debug=True)
