from flask import Flask, render_template, url_for, redirect, request, flash
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_mail import Message
from flask_login import LoginManager
from flask_login import login_user, logout_user, login_required, current_user
import os

app=Flask(__name__)
Bootstrap(app)
bcrypt = Bcrypt()
bcrypt.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.log_view='acceder'
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = '17460080@colima.tecnm.mx'
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:12345@localhost:5432/agecon'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://qqrasfeyzsyisf:0079bd5ff9337fcf13e238e1757947dd6833f0e367c68825493153177c26c67a@ec2-52-54-174-5.compute-1.amazonaws.com:5432/dkotop8g7gkk4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False
db = SQLAlchemy(app)

class Contactos(db.Model):
    __tablename__ = 'contactos'
    id = db.Column(db.Integer,primary_key=True)
    nombre = db.Column(db.String(50))
    apellido = db.Column(db.String(50))
    correo = db.Column(db.String(50), unique=True, nullable=False, index=True)
    telefono = db.Column(db.Numeric(10))
    direccion = db.Column(db.String(100))
    id_agenda= db.Column(db.Integer, db.ForeignKey('agenda.id'))

class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password = db.Column(db.String(300))

    def is_authenticated(self):
             return True

    def is_active(self):
             return True

    def is_anonymous(self):
             return False

    def get_id(self):
             return str(self.id)

class Agenda(db.Model):
    __tablename__ = 'agenda'
    id = db.Column(db.Integer, primary_key=True)
    nombre_agenda = db.Column(db.String(50))
    id_usuario= db.Column(db.Integer, db.ForeignKey('usuario.id'))

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.filter_by(id=user_id).first()

#decoradores
#def = definir una funcion
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template("index.html")

@app.route('/registrar', methods=['GET', 'POST'])
#mandar mensaje si el correo es el mismo que ya se ha registrado con anterioridad --PENDIENTE
def registrar():
    if request.method == 'POST':
        campo_usuario = request.form["email"]
        campo_passw = request.form["pswd"]
        #password=bcrypt.generate_password_hash(campo_passw).decode('utf-8')
        consulta=Usuario.query.filter_by(usuario=campo_usuario).first()
        if consulta is not None:
            mensaje="Usuario ya existente"
            return render_template("registrar.html", mensaje=mensaje)
        else:
            user = Usuario(usuario=campo_usuario,password=bcrypt.generate_password_hash(campo_passw).decode('utf-8'))
            db.session.add(user)
            db.session.commit()
            mensaje="Registrado con Éxito"
            msg = Message("Gracias por Registrarte", sender="17460080@colima.tecnm.mx", recipients=[campo_usuario])
            msg.body = "Este es un email de prueba"
            msg.html = "<p>Este es un email</p>"
            mail.send(msg)
            return render_template("registrar.html", mensaje=mensaje)
    return render_template("registrar.html")

@app.route('/acceder', methods=['GET', 'POST'])
#tengo pendiente la validacion de si el correo no coincide
def acceder():
    if request.method == "POST":
        email = request.form["email"]
        pwd = request.form["pswd"]
        usuario_existe = Usuario.query.filter_by(usuario=email).first()
        if usuario_existe != None:
            if bcrypt.check_password_hash(usuario_existe.password, pwd):
                login_user(usuario_existe)
                if current_user.is_authenticated:
                    return redirect("/principal")
            else:
                mensaje="Contraseña Incorrecta, Intente de nuevo"
                return render_template("acceder.html", mensaje=mensaje)
    else:
        return render_template("acceder.html")
@app.route('/principal', methods=['GET', 'POST'])
#agregar para todas las rutas que son usuarios autenticados
@login_required
def principal():
    return render_template("principal.html")

@app.route('/nuevagenda', methods=['GET', 'POST'])
def nuevagenda():
    if request.method == 'POST':
        campo_nombre = request.form["name"]
        user = Agenda(nombre_agenda=campo_nombre, id_usuario=current_user.get_id())
        db.session.add(user)
        db.session.commit()
        mensaje="Creada con Éxito"
        return render_template("nuevagenda.html", mensaje=mensaje)
    else:
        return render_template("nuevagenda.html")

@app.route('/nuevocontacto/<id>/<nombre_agenda>', methods=['GET', 'POST'])
def nuevocontacto(id, nombre_agenda):
        #usuario_secion=current_user.get_id()
        consulta = Agenda.query.get(id)
        print(consulta)
        return render_template("nuevocontacto.html", consulta=consulta)

@app.route('/muestra/<id>/<nombre_agenda>', methods=['GET', 'POST'])
def muestra(id, nombre_agenda):
        #usuario_secion=current_user.get_id()
        consulta = Contactos.query.filter_by(id_agenda=id)
        print(consulta)
        return render_template("muestra.html", variable=consulta)


@app.route('/nuevocontacto', methods=['GET', 'POST'])
def nuevoc():
    if request.method == 'POST':
        select_agenda = request.form["select_agenda"]
        print(select_agenda)
        campo_nombre = request.form["name"]
        campo_apellido = request.form["apellido"]
        campo_correo = request.form["email"]
        campo_telefono = request.form["telefono"]
        campo_direccion = request.form["address"]
        user = Contactos(nombre=campo_nombre, apellido=campo_apellido, correo=campo_correo, telefono=campo_telefono, direccion=campo_direccion, id_agenda=select_agenda)
        #id_agenda=current_user.get_id() HAY QUE CHECARLO
        db.session.add(user)
        db.session.commit()
        #mensaje="Contacto Registrado con Éxito"
        return redirect('/nuevocontacto')
    else:
        consulta=""
        mensaje="Contacto Registrado con Éxito"
        return render_template("nuevocontacto.html", mensaje=mensaje, consulta=consulta)

#@app.route('/muestra', methods=['GET', 'POST'])
#def muestra():
    #usuario_secion=current_user.get_id()
    #consulta = Contactos.query.get(usuario_secion)
    #print(consulta)
    #return render_template("muestra.html", variable=consulta)

@app.route('/vistas', methods=['GET', 'POST'])
def vistas():
    usuario_secion=current_user.get_id()
    consulta = Agenda.query.filter_by(id_usuario=usuario_secion)
    print(consulta)
    #consulta = Agenda.query.all()
    print(consulta)
    return render_template("vistas.html", variable=consulta)

@app.route('/editar/<id>')
def editar(id):
    r=Contactos.query.filter_by(id=int(id)).first()
    return render_template("editar.html", contactos=r)

@app.route('/actualizar', methods=['GET', 'POST'])
def actualizar():
    if request.method == 'POST':
        qry = Contactos.query.get(request.form['id'])
        qry.nombre = request.form['nombreE']
        qry.apellido = request.form['apellidoE']
        qry.correo = request.form['correoE']
        qry.telefono = request.form['telefonoE']
        qry.direccion = request.form['direccionE']
        db.session.commit()
        return redirect(url_for('vistas'))

@app.route('/eliminar/<id>')
def eliminar(id):
    q = Contactos.query.filter_by(id=int(id)).delete()
    db.session.commit()
    return redirect(url_for('vistas'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__=="__main__":
    db.create_all()
    app.run(debug=True)
