from app import app, db
from flask import render_template, redirect, flash, request, send_from_directory, current_app, url_for
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from datetime import date
import shapefile
import pygeoif
from geoalchemy2 import Geometry
from sqlalchemy import Table, column, create_engine, Unicode, MetaData, insert
from sqlalchemy.orm import mapper, create_session
import os
import requests
import json

from app.models.forms import LoginForm, RegisterForm, UploadForm, UserEditForm
from app.models.tables import User, Map

#------------------------------------Index------------------------------------
@app.route("/", methods=["POST","GET"])
def index():
    form = UploadForm()
    formEdit = UserEditForm()
    

    #------configurando conexão com postgres----------------------------------------------
    engine_postgres = create_engine('postgresql://postgisdb:33333333@rn-mapas.clt9yrv0p5yg.us-east-2.rds.amazonaws.com/rnmapas')
    metadata = MetaData(bind=engine_postgres)

    #------configurando geoserver---------------------------------------------------------
    workspace = 'rnemmapas'
    datastore = 'postgis'
    server = 'gs-env.zj4q7wpik5.us-east-2.elasticbeanstalk.com'
    auth = ('admin', 'geoserver')
    headers = {'Content-type': 'text/xml'}
    #-------------------------------------------------------------------------------------

    #------Pegando lista de layers no wokspace do projeto para enviar pro openlayers------
    layersInWorkspace = 'http://'+server +'/rest/workspaces/'+ workspace + '/layers.json'
    lyr_list_response = requests.get(layersInWorkspace, auth=auth)
 
    lyr_list_text = lyr_list_response.text

    print(lyr_list_text)

    #------Pegando nome dos layers no wokspace do projeto para enviar pro frontend------
    listMaps = Map.query.all()
    infraestrutura = []
    demografia = []
    aspectosSociais = []
    aspectosEconomicos = []
    caracterizacaoTerritorial = []

    for mapp in listMaps:
        if mapp.category == "infraestrutura":
            infraestrutura.append(mapp)
        elif mapp.category == "demografia":
            demografia.append(mapp)
        elif mapp.category == "aspectos sociais":
            aspectosSociais.append(mapp)
        elif mapp.category == "aspectos economicos":
            aspectosEconomicos.append(mapp)
        elif mapp.category == "caracterização territorial":
            caracterizacaoTerritorial.append(mapp)


    #--------------------------------------------------------------------------------------
    
    #------Verificando o usuário para exibir os mapas enviados pelo usuário----------------
    if current_user.is_anonymous:
        list_uploads_user = []
    else:
        #carrega lista de uploads feitos pelo usuário
        list_uploads_user = Map.query.filter_by(user_id = current_user.id).all()
    #--------------------------------------------------------------------------------------

    #------Tratando os arquivos enviados pelo formulário de upload-------------------------     
    if request.method == "POST":
        #Salvando arquivos na pasta de uploads
        for f in request.files.getlist("fileshape"):
            filename = secure_filename(f.filename)
            f.save(os.path.join('uploads/', filename))

        #Pegando valores do formulário
        map_title = form.title.data
        map_category = form.category.data

        #convertendo o título do mapa para caracteres minusculos
        map_title_lower = map_title.lower()

        verify_map_exists = Map.query.filter_by(title = map_title).first()

        #verfica se há um mapa cadastrado com essse titulo
        if verify_map_exists:
            flash("Já existe um mapa cadastrado com esse titulo!")
        else:
            #inserindo registro na tabela de mapas (Map)
            data_to_insert = Map(map_title, date.today(), map_category, False, current_user.name, current_user.id)
            db.session.add(data_to_insert)
            db.session.commit()

            #definindo informações dos shapefiles
            shapefile_imported = shapefile.Reader(os.path.join('uploads/', filename))
            shapefile_shapes = shapefile_imported.shapes()
            shapefile_type_name = shapefile_imported.shapeTypeName
            shapefile_records = shapefile_imported.records()
            shapefile_fields = shapefile_imported.fields


            #deleta o primeiro item do vetor que contem os campos
            shapefile_fields.pop(0)

            #Nesse Bloco de código são geradas as tabelas com os campos
            #de dados contidos nos shapefiles
            class MapTable(object):
                pass

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
                db.Column('ids', db.Integer, primary_key=True, autoincrement=True),
                *(db.Column(field[0], Unicode(255)) for field in shapefile_fields),
                db.Column('geom', Geometry(geometry_type='GEOMETRY', srid=4326))
            )

            metadata.create_all()
            mapper(MapTable, map_table)
            session = create_session(bind=engine_postgres, autocommit=False, autoflush=True)
            session.commit()

            #percorrendo a lista de registros para inserir no banco
            record_ids = 1
            for count, record in enumerate(shapefile_records):
                #adcionando um id no inicio da lista de atributos de cada registro
                record.insert(0, record_ids)
                
                #verificando tipo de geometria
                if (shapefile_type_name == 'POLYGON') or (shapefile_type_name == 'MULTIPOLYGON'):
                    gshape = pygeoif.MultiPolygon(pygeoif.geometry.as_shape(shapefile_shapes[count]))
                    geom = 'SRID=4326;{0}'.format(gshape.wkt)
                elif shapefile_type_name == 'POINT':
                    point = shapefile_shapes[count].points[0]
                    geom = 'SRID=4326;POINT({0} {1})'.format(point[0], point[1])

                record.append(geom)
                record_to_insert = map_table.insert().values(record)
                connection_with_db = engine_postgres.connect()
                connection_with_db.execute(record_to_insert)
                record_ids += 1
            
            connection_with_db.close()
            flash("Upload feito com sucesso!")

            #Criando layer em um datastore já existente.
            #o workspace e datastore devem ser criados anteriormente o funcionamento do sistema
            layerUrl = 'http://'+ server +'/rest/workspaces/'+ workspace +'/datastores/'+ datastore +'/featuretypes'
            create_layer_data = '<featureType><name>'+ map_title_lower +'</name></featureType>'
            layer_publish_response = requests.post(layerUrl, auth=auth, headers=headers, data=create_layer_data)
            
            print(layer_publish_response.text)
            

            

    return render_template("gis/map.html",
                            form_template = form,
                            form_template_edit = formEdit,
                            list_uploads_user = list_uploads_user,
                            lyr_list_text = lyr_list_text,
                            infraestrutura = infraestrutura,
                            demografia  = demografia,
                            caracterizacaoTerritorial = caracterizacaoTerritorial,
                            aspectosEconomicos = aspectosEconomicos,
                            aspectosSociais = aspectosSociais
                            )



#-------------------------------------About-----------------------------------
@app.route("/sobre")
def about():
    return render_template("gis/about.html")

#-------------------------------------Contributors----------------------------
@app.route("/colaboradores")
def contributors():
    return render_template("gis/contributors.html")



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
@app.route("/registre-se", methods=["POST","GET"])
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

#--------------------------------Register----------------------------------------
@app.route("/editar_usuario", methods=["POST", "GET"])
@login_required
def userEdit():
    if request.method == "POST":
        newName = request.form['name']
        newLastName = request.form['lastname']
        newEmail = request.form['email']
        newDescription = request.form['description']
        newPassword = request.form['password']
        newPasswordConfirm = request.form['password_confirm']
        currentPassword = request.form['current_password']

        user = User.query.filter_by(id = current_user.id).first()

        if user.password == currentPassword:
            if newName != "":
                user.name = newName
                db.session.commit()
                flash("Dados alterados com sucesso!")

            if newLastName != "":
                user.lastname = newLastName
                db.session.commit()
                flash("Dados alterados com sucesso!")

            if newDescription != "":
                user.description = newDescription
                db.session.commit()
                flash("Dados alterados com sucesso!")

            if newEmail != "":
                user.email = newEmail
                db.session.commit()
                flash("Dados alterados com sucesso!")

            if (newPassword != "" and newPasswordConfirm != ""):
                if newPassword == newPasswordConfirm:
                    user.password = newPassword
                    db.session.commit()
                    flash("Dados alterados com sucesso!")
                else:
                    flash("Senhas não são iguais.")
        else:
            flash("O password de confirmação dos dados está incorreto.")

    return redirect("/")
    

#--------------------------------Logout--------------------------------------------
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")

#--------------------------------Download----------------------------------------
@app.route("/shp", methods=["GET", "POST"])
def shp():
    if request.method == "POST":
        shpName = request.form['shp']
        return send_from_directory(directory='../uploads/', filename=shpName + '.shp', as_attachment=True)

@app.route("/dbf", methods=["GET", "POST"])
def dbf():
    if request.method == "POST":
        shpName = request.form['dbf']
        return send_from_directory(directory='../uploads/', filename=shpName + '.dbf', as_attachment=True)

@app.route("/shx", methods=["GET", "POST"])
def shx():
    if request.method == "POST":
        shpName = request.form['shx']
        return send_from_directory(directory='../uploads/', filename=shpName + '.shx', as_attachment=True)