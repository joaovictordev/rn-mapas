from app import app, db
from flask import render_template, redirect, flash
from flask_login import login_user, login_required, logout_user, current_user

from app.models.forms import LoginForm, RegisterForm
from app.models.tables import User

@app.route("/logado")
@app.route("/")
def index():
    return render_template("gis/map.html")

@app.route("/sobre")
def about():
    return render_template("gis/about.html")

@app.route("/login", methods=["POST","GET"])
def login():
    #Instancia a classe LoginForm de tables.py
    form = LoginForm()

    #Pegando os valores que foram inseridos no formulário de login
    email = form.email.data
    password = form.password.data

    #Validando o fomulário
    if form.validate_on_submit():
        #Pesquisando usuário no banco
        search_user = User.query.filter_by(email = email).first()

        #caso o usuário exista e a senha do formulário seja igual a cadastrada no banco
        #o usuário é logado
        if search_user:
            if search_user.password == password:
                login_user(search_user)
                return redirect('/logado')
            else:
                flash("Senha incorreta")
        else:
            flash("Usuário não cadastrado!")
        
    return render_template("auth/login.html", form_template = form)

@app.route("/cadastrar-se", methods=["POST","GET"])
def register():
    #Instancia a classe RegisterForm de tables.py
    form = RegisterForm()

    #Pegando os valores que foram inseridos no formulário de cadastro
    name = form.name.data
    lastname = form.lastname.data
    description = form.description.data
    email = form.email.data
    password = form.password.data
    password_confirm = form.password_confirm.data

    #Validando o fomulário
    if form.validate_on_submit():
        verify_user_exists = User.query.filter_by(email = email).first()

        #verfica se há um usuário cadastrado com esse email
        if verify_user_exists:
            flash("Já existe um usuário cadastrado com esse email!")
        else:
            if password == password_confirm:
                #inserindo os dados no banco
                data_to_insert = User(name, lastname, description, email, password)

                db.session.add(data_to_insert)
                db.session.commit()
                flash("Usuário foi cadastrado!")
            else:
                flash("As senhas inseridas não são iguais")

    return render_template("auth/register.html", form_template = form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")