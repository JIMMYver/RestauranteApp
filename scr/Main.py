from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from werkzeug.security import check_password_hash,generate_password_hash


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tareasDB.sqlite"
app.config["SECRET_KEY"] = "your_secret_key"
db = SQLAlchemy(app)

login_manager_app = LoginManager(app)

class Tarea(db.Model):
    id = db.Column(db.Integer, autoincrement= True, primary_key=True)
    description= db.Column(db.String(200))
    state = db.Column(db.Boolean, default=False)
    userid = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class User(db.Model,UserMixin):
    id = db.Column(db.Integer, autoincrement= True, primary_key=True)
    username =db.Column(db.String(150))
    password =db.Column(db.String(200))
    fullname =db.Column(db.String(180))
    listaTareas = db.relationship('Tarea', backref='user', lazy=True)

    def __init__(self, username, password, fullname="") -> None:
        self.username = username
        self.password = generate_password_hash(password)
        self.fullname = fullname
    
    @classmethod
    def check_password(self, hashed_password, password):
        return check_password_hash(hashed_password, password)

with app.app_context():
    db.create_all()
    admin_user = User.query.filter_by(username="jimmyvera@admin.com").first()
    if not admin_user:
        admin_user = User(username="jimmyvera@admin.com", password="jimmy2025", fullname="Jimmy Vera")
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user created: username='jimmyvera@admin.com', password='jimmy2025'") 

@login_manager_app.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Función para obtener la descripción
def getDescription(description):
    description_lower = description.strip().lower()
    # Obtener todas las descripciones existentes del usuario
    tareas = Tarea.query.filter_by(userid=current_user.id).all()
    # Verificar si alguna descripción coincide
    for tarea in tareas:
        if tarea.description.strip().lower() == description_lower:
            return tarea  # Devuelve la tarea encontrada
    return None

@app.route('/')
@login_required
def index():
    listaTareas = Tarea.query.filter_by(userid=current_user.id).all()
    return  render_template('index.html',Tareas=listaTareas, nombres= current_user.fullname)

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', nombres= current_user.fullname)

@app.route('/agregar', methods=['POST'])
@login_required
def agregar():
    description = request.form['description']

    # Validar la descripción
    if not description or description.strip() == "":
        error_description = 'Por favor, ingrese descripción de la tarea.'
    elif getDescription(description):
        error_description = 'La tarea ya existe'
    else:
        # Agregar nueva tarea
        nueva = Tarea(description=description, userid=current_user.id)
        db.session.add(nueva)
        db.session.commit()
        return redirect(url_for('index'))  # Redirige después de agregar la tarea

    # Si hay un error, renderiza la plantilla pasando el error y el nombre del usuario
    listaTareas = Tarea.query.filter_by(userid=current_user.id).all()  # Solo las tareas del usuario actual
    return render_template('index.html', Tareas=listaTareas, error_description=error_description, nombres=current_user.fullname)

@app.route('/actualizar/<int:id_tarea>')
@login_required
def actualizar(id_tarea):
    tarea = Tarea.query.filter_by(id=id_tarea).first()
    tarea.state = not tarea.state
    db.session.commit()
    return redirect(url_for('index')) 

@app.route('/eliminar/<int:id_tarea>')
@login_required
def eliminar(id_tarea):
    tarea = Tarea.query.filter_by(id=id_tarea).first()
    db.session.delete(tarea)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    errorlogin = None  # Inicializa la variable errorlogin

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Validación de los campos de usuario y contraseña vacíos
        if not username or username.strip() == "" or not password or password.strip() == "":
            errorlogin = "Por favor, ingrese usuario y contraseña"
        else:
            # Consulta al usuario en la base de datos
            user = User.query.filter_by(username=username).first()

            # Verificación de la contraseña
            if user and User.check_password(user.password, password):
                login_user(user)
                return redirect(url_for('index'))  # Redirige si el login es exitoso
            else:
                errorlogin = "Usuario o contraseña incorrecta"  # Si las credenciales son incorrectas

    return render_template('login.html', errorlogin=errorlogin)

@app.route('/logout')
def logout():
    nombres = current_user.fullname
    logout_user()
    return render_template('logout.html',nombres= nombres)

def status_401(error):
    return redirect(url_for('login'))

def status_404(error):
    return render_template('error.html')

if __name__ == '__main__':
    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404)
    app.run(debug=True, port=8000) 