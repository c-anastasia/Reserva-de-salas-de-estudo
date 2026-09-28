from flask import Flask, render_template, redirect, url_for, request, session, flash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Users.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "anas"

db = SQLAlchemy(app)

HORARIOS_VALIDOS = [
    "08:00",
    "09:00",
    "11:00",
    "16:00",
    "17:00"
]

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    passe = db.Column(db.String(200), nullable=False)


class Logins(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False)
    data = db.Column(db.DateTime, default=datetime.now)


class Reservas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    sala = db.Column(db.Integer, nullable=False)
    data = db.Column(db.String(20), nullable=False)
    hora = db.Column(db.String(10), nullable=False)
    pessoas = db.Column(db.Integer, nullable=False)


def capacidade_sala(sala):
    capacidades = {
        1: 3,
        2: 4,
        3: 4,
        4: 5,
        5: 8
    }
    return capacidades.get(sala, 0)


def pessoas_reservadas(sala, data, hora):
    reservas = Reservas.query.filter_by(
        sala=sala,
        data=data,
        hora=hora
    ).all()

    return sum(reserva.pessoas for reserva in reservas)


def obter_salas(data=None, hora=None):
    salas = []
    for numero in range(1, 6):
        capacidade = capacidade_sala(numero)

        if data and hora and hora in HORARIOS_VALIDOS:
            ocupadas = pessoas_reservadas(numero,data,hora)
        else:
            ocupadas = 0

        disponiveis = capacidade - ocupadas

        if disponiveis < 0:
            disponiveis = 0

        if disponiveis == 0:
            estado = f"Ocupada ({ocupadas}/{capacidade})"

        elif ocupadas == 0:
            estado = f"{capacidade} lugares disponíveis"

        else:
            estado = f"{disponiveis} disponível(eis)"

        salas.append({"numero": numero,
                      "capacidade": capacidade,
                      "ocupadas": ocupadas,
                      "disponiveis": disponiveis,
                      "estado": estado})
    return salas


@app.route("/")
def index():

    if "user_id" not in session:
        return redirect(url_for("login"))

    utilizador = db.session.get(Users,session["user_id"])

    data = request.args.get("data", "")
    hora = request.args.get("hora", "")

    if data and hora and hora in HORARIOS_VALIDOS:
        salas = obter_salas(data, hora)
    else:
        salas = obter_salas()

    return render_template(
        "index.html",
        utilizador=utilizador,
        salas=salas,
        data=data,
        hora=hora,
        horarios=HORARIOS_VALIDOS
    )


@app.route("/login", methods=["GET", "POST"])
def login():

    if "user_id" in session:
        return redirect(url_for("index"))
    
    if request.method == "POST":
        email = request.form.get("email")
        passe = request.form.get("passe")
        utilizador = Users.query.filter_by(email=email).first()

        if utilizador and check_password_hash(utilizador.passe,passe):
            session.permanent = True
            session["user_id"] = utilizador.id
            session["user_name"] = utilizador.nome

            novo_login = Logins(email=email)

            db.session.add(novo_login)
            db.session.commit()

            return redirect(url_for("index"))
        flash("Email ou palavra-passe incorretos.")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/registar", methods=["GET", "POST"])
def registar():

    if "user_id" in session:
        return redirect(url_for("index"))

    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        passe = request.form.get("passe")

        utilizador_existente = Users.query.filter((Users.nome == nome) | (Users.email == email)).first()

        if utilizador_existente:
            flash("O nome ou email já está registado.")
            return redirect(url_for("registar"))

        nova_password = generate_password_hash(passe)
        novo_utilizador = Users(nome=nome,email=email,passe=nova_password)

        db.session.add(novo_utilizador)
        db.session.commit()

        flash("Registo efetuado com sucesso. Faça login.")
        return redirect(url_for("login"))
    
    return render_template("registar.html")


@app.route("/reserva/<int:sala>",methods=["GET", "POST"])
def reserva(sala):
    if "user_id" not in session:
        return redirect(url_for("login"))

    capacidade = capacidade_sala(sala)

    data = request.values.get("data", "")
    hora = request.values.get("hora", "")
    ocupadas = 0
    disponiveis = capacidade

    if data and hora and hora in HORARIOS_VALIDOS:
        ocupadas = pessoas_reservadas(sala,data,hora)
        disponiveis = capacidade - ocupadas

    if request.method == "POST":
        utilizador = db.session.get(Users, session["user_id"])

        if not utilizador:
            return redirect(url_for("login"))
        
        nome = utilizador.nome

        data = request.form.get("data")
        hora = request.form.get("hora")
        pessoas_texto = request.form.get("pessoas")

        reserva_existente = Reservas.query.filter_by(
            nome=nome,
            data=data).first()

        if reserva_existente:
            flash("Já tem uma reserva para este dia." \
            "Só é possível reservar uma sala por dia.")
            return redirect(url_for("index",data=data,hora=hora))

        pessoas_texto = request.form.get("pessoas")
        pessoas = int(pessoas_texto)
        
        nova_reserva = Reservas(
            nome=nome,
            sala=sala,
            data=data,
            hora=hora,
            pessoas=pessoas
        )

        db.session.add(nova_reserva)
        db.session.commit()

        flash("Reserva efetuada com sucesso.")
        return redirect(url_for("index",data=data,hora=hora))

    return render_template(
        "reserva.html",
        sala=sala,
        capacidade=capacidade,
        ocupadas=ocupadas,
        disponiveis=disponiveis,
        data=data,
        hora=hora,
        horarios=HORARIOS_VALIDOS
    )

with app.app_context():
    db.create_all()


@app.route("/utilizadores/editar/<int:id>",methods=["GET", "POST"])
def editar_utilizador(id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    utilizador = Users.query.get_or_404(id)

    if request.method == "POST":
        nome = (request.form.get("nome") or "").strip()
        email = (request.form.get("email") or "").strip()
        passe = request.form.get("passe") or ""

        if not nome or not email:
            flash("Nome e email são obrigatórios.")
            return render_template("editar_utilizador.html",utilizador=utilizador)

        outro_utilizador = Users.query.filter(
            ((Users.nome == nome)|(Users.email == email)),Users.id != id).first()

        if outro_utilizador:
            flash("O nome ou email já está a ser utilizado.")
            return render_template("editar_utilizador.html",utilizador=utilizador)

        utilizador.nome = nome
        utilizador.email = email

        if passe:
            utilizador.passe = generate_password_hash(passe)

        db.session.commit()

        if session.get("user_id") == utilizador.id:session["user_name"] = utilizador.nome

        flash("Dados atualizados com sucesso")
        return redirect(url_for("index"))
    return render_template("editar_utilizador.html",utilizador=utilizador)


if __name__ == "__main__":
    app.run(debug=True)