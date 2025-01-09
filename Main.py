from flask import Flask, render_template
from flask import request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tareasDB.sqlite"
db = SQLAlchemy(app)

class Tarea(db.Model):
    id = db.Column(db.Integer, autoincrement= True, primary_key=True)
    description= db.Column(db.String(200))
    state = db.Column(db.Boolean)


with app.app_context():
    db.create_all()

# Función para obtener la descripción
def getDescription(description):
    description_lower = description.strip().lower()
    # Obtener todas las descripciones existentes
    tareas = Tarea.query.all()
    # Verificar si alguna descripción coincide
    for tarea in tareas:
        if tarea.description.strip().lower() == description_lower:
            return tarea  # Devuelve la tarea encontrada
    return None

@app.route('/')
def index():
    listaTareas = Tarea.query.all()
    return  render_template('index.html',Tareas=listaTareas)


@app.route('/agregar', methods=['POST'])
def agregar():
    description = request.form.get('description')

    listaTareas = Tarea.query.all() 
    message_error = None

    # Validar la descripción
    if not description or description.strip() == "":
        message_error = 'Por favor, ingrese descripción de la tarea.'
    elif getDescription(description) is not None:
        message_error = f'Ya existe la tarea: "{description.strip()}"'

    if  message_error:
        return render_template('index.html', Tareas=listaTareas, error_description=message_error)

    # Agregar nueva tarea
    nueva = Tarea(description=description, state=False)
    db.session.add(nueva)
    db.session.commit()
    return redirect(url_for('index'))



@app.route('/actualizar/<int:id_tarea>')
def actualizar(id_tarea):
    tarea = Tarea.query.filter_by(id=id_tarea).first()
    tarea.state = not tarea.state
    db.session.commit()
    return redirect(url_for('index')) 

@app.route('/eliminar/<int:id_tarea>')
def eliminar(id_tarea):
    tarea = Tarea.query.filter_by(id=id_tarea).first()
    db.session.delete(tarea)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True) 
