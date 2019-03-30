from app import app, db
from flask import render_template, redirect, flash, request, send_from_directory
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from datetime import date
import shapefile
import pygeoif
from geoalchemy2 import Geometry
from sqlalchemy import Table, column, create_engine, Unicode, MetaData, insert
from sqlalchemy.orm import mapper, create_session

from app.models.forms import LoginForm, RegisterForm, UploadForm
from app.models.tables import User, Map

#------------------------------------Index------------------------------------
@app.route("/", methods=["POST","GET"])
def index():
    form = UploadForm()
    
    #carrega lista de uploads feitos pelo usuário
    list_uploads_user = Map.query.filter_by(user_id = current_user.id).all()

    if current_user.is_anonymous:
        list_uploads_user = []
         
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
            shapefile_shapes = shapefile_imported.shapes()
            shapefile_type_name = shapefile_imported.shapeTypeName
            shapefile_records = shapefile_imported.records()
            shapefile_fields = shapefile_imported.fields

            print(shapefile_imported.bbox)

            #deleta o primeiro item do vetor que contem os campos
            shapefile_fields.pop(0)

            #Nesse Bloco de código são geradas as tabelas com os campos
            #de dados contidos nos shapefiles
            class MapTable(object):
                pass

            engine_postgres = create_engine('postgresql://postgres:3333@localhost/rnmapas')
            metadata = MetaData(bind=engine_postgres)

            #adcionado postgis
            connection_with_db = engine_postgres.connect()
            try:
                connection_with_db.execute("CREATE EXTENSION postgis")
            except Exception as e:
                print(e)
                print("extension postgis already exists")
            connection_with_db.close()

            #definindo o modelo de tabela que recebrá os shapefiles
            map_table = db.Table(map_title_lower, metadata,
                db.Column('id', db.Integer, primary_key=True, autoincrement=True),
                *(db.Column(field[0], Unicode(255)) for field in shapefile_fields),
                db.Column('geom', Geometry(geometry_type='GEOMETRY', srid=4326))
            )

            metadata.create_all()
            mapper(MapTable, map_table)
            session = create_session(bind=engine_postgres, autocommit=False, autoflush=True)
            session.commit()

            #percorrendo a lista de registros para inserir no banco
            record_id = 1
            for count, record in enumerate(shapefile_records):
                #adcionando um id no inicio da lista de atributos de cada registro
                record.insert(0, record_id)

                gshape = pygeoif.MultiPolygon(pygeoif.geometry.as_shape(shapefile_shapes[count]))
                geom = 'SRID=4326;{0}'.format(gshape.wkt)
                record.append(geom)

                record_to_insert = map_table.insert().values(record)
                connection_with_db = engine_postgres.connect()
                connection_with_db.execute(record_to_insert)
                record_id += 1



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