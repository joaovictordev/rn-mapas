from app import app, db
from flask import render_template, redirect, flash, request, send_from_directory
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from datetime import date
import shapefile
from geoalchemy2 import Geometry
import os
from app.models.forms import LoginForm, RegisterForm, UploadForm
from app.models.tables import User, Map

#------------------------------------Index------------------------------------
@app.route("/", methods=["POST","GET"])
def index():
    form = UploadForm()

    #carrega lista de uploads feitos pelo usuário
    if current_user.is_anonymous:
        list_uploads_user = []
    else:
        list_uploads_user = Map.query.filter_by(user_id = current_user.id).all()

    if request.method == "POST":
        #uploads dos arquivos
        for f in request.files.getlist("fileshape"):
            filename = secure_filename(f.filename)
            f.save(filename)

        #Pegando valores do formulário
        map_title = form.title.data
        map_category = form.category.data

        #transformando o titulo para caracteres minusculos
        map_title_lower = map_title.lower()

        verify_map_exists = Map.query.filter_by(title = map_title).first()

        #verfica se há um mapa cadastrado com essse titulo
        if verify_map_exists:
            flash("Já existe um mapa cadastrado com esse titulo!")
        else:
            #inserindo registro na tabela de mapas (Map)
            data_to_insert = Map(map_title, date.today(), map_category, False, current_user.id)
            db.session.add(data_to_insert)
            db.session.commit()

            #definindo informações dos shapefiles
            shapefile_imported = shapefile.Reader(filename)
            shapefile_geometry = shapefile_imported.shapes()
            shapefile_records = shapefile_imported.records()
            shapefile_fields = shapefile_imported.fields

            columns_to_insert = []

            #armazenando os campos e seus respectivos tipos em vetores
            for field in shapefile_fields:
                field_name = field[0]
                field_type = field[1]
                
                if field_type == 'C':
                    columns_to_insert.append(field_name +'= db.Column(db.Integer)')
                elif field_type == 'N':
                   columns_to_insert.append(field_name +'= db.Column(db.INumeric)')
                elif field_type == 'F':
                    columns_to_insert.append(field_name +'= db.Column(db.Float)')
                elif field_type == 'L':
                    columns_to_insert.append(field_name +'= db.Column(db.Boolean)')
                elif field_type == 'D':
                    columns_to_insert.append(field_name +'= db.Column(db.DateTime)')

                

            print(columns_to_insert)
            
            #definindo a tabela que representa o mapa
            class User(db.Model):
                __tablename__ = map_title_lower
                id = db.Column(db.Integer, primary_key=True)
                
            

   #         db.create_all()
    #        db.session.commit()
            #criando tabela no banco

            #inserindo registros na tabela de um mapa
#            me = User('admin', 'admin@example.com')
#            db.session.add(me)
#            db.session.commit()

    return render_template("gis/map.html", form_template = form, list_uploads_user = list_uploads_user)



#-------------------------------------About-----------------------------------
@app.route("/sobre")
def about():
    return render_template("gis/about.html")



#--------------------------------------Login---------------------------------
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
                return redirect('/')
            else:
                flash("Senha incorreta")
        else:
            flash("Usuário não cadastrado!")
        
    return render_template("auth/login.html", form_template = form)



#------------------------------Register--------------------------------
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
                #inserindo registro na tabela de usuários (User)
                data_to_insert = User(name, lastname, description, email, password)

                db.session.add(data_to_insert)
                db.session.commit()
                flash("Usuário foi cadastrado!")
            else:
                flash("As senhas inseridas não são iguais")

    return render_template("auth/register.html", form_template = form)

    

#--------------------------------Logout----------------------------------------
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")