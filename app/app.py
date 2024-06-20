from flask import Flask, render_template, url_for, redirect, request, flash
import os
import psycopg2
from  flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
csrf = CSRFProtect()

#LLAMAR A LA BASE DE DATOS

def get_db_conection():
    try:
        conn=psycopg2.connect(host='localhost',
                              dbname='SCRBM',
                              user = os.environ['username2'],
                              password = os.environ['password2'])
        return conn
    except psycopg2.Error as error:
        print(f"Base de datos no encontrada {error}")
        return None

#FIN LLAMADA DE BASDE DE DATOS

app.secret_key='mysecretkey'

@app.route ("/")
def index():
    return render_template('index.html')

@app.route ("/dashboard")
def dashboard():
    return render_template('dashboard.html')

@app.route("/dashboard/materiales")
def materiales():
    return render_template('materiales.html')

#-----------------------------------------------INICIO READ UNIDAD------------------------------------------------------

@app.route("/dashboard/unidades")
def unidades():
    conn = get_db_conection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM unidades '
                'ORDER BY nombre_unidad ASC')
    unidad = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('unidades.html', unidad = unidad)

#-----------------------------------------------FIN READ UNIDAD ------------------------------------------------------

#-------------------------INICIO REGISTRO UNIDAD------------------------------------------------------------------


@app.route("/dashboard/unidades/registrar")
def form_regis_unidad():
    return render_template('form_regis_unidad.html')


@app.route("/dashboard/unidades/registrar/regitrando", methods=('GET', 'POST'))
def registrando_unidad():
    if request.method == 'POST':
        unidad = request.form['unidad']
        
        conn = get_db_conection()
        cur = conn.cursor()
        cur.execute('INSERT INTO unidades(nombre_unidad)'
                    'VALUES (%s)',
                    (unidad,))
        conn.commit()
        cur.close()
        conn.close()
        flash('Unidad registrada correctamente')
        return redirect(url_for('unidades'))
    return redirect(url_for('unidades'))

#-------------------------FIN REGISTRO UNIDAD------------------------------------------------------------------
         
#----------------------------INICIO UBDATE UNIDADE-----------------------------------------------------------------
@app.route('/unidades/editar/<string:id_unidad>')
def editar_unidad(id_unidad):
    conn = get_db_conection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM unidades WHERE id_unidad ={0}'.format(id_unidad))
    unidad = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return render_template('unidades_editar.html', unidad = unidad[0])

@app.route('/unidad/editar/proceso/<string:id_unidad>', methods =['POST'] )
def editar_unidad_proceso(id_unidad):
    if request.method == 'POST':
        nombre_unidad = request.form['nombre_unidad']
        
        conn = get_db_conection()
        cur = conn.cursor()
        sql = "UPDATE unidades SET nombre_unidad=%s WHERE id_unidad =%s;"
        valores = (nombre_unidad, id_unidad)
        cur.execute(sql, valores)
        conn.commit()
        cur.close()
        conn.close()
        flash('Pais editado')
        return redirect (url_for('unidades'))
    return redirect (url_for('unidades'))

#----------------------------FIN UBDATE UNIDADE-----------------------------------------------------------------

    
         
@app.route('/papelera')
def papelera():
     return render_template('papelera.html')
    

def pagina_no_encontrada(error):
    return render_template('error404.html')

if __name__ =='__main__':
    csrf.init_app(app)
    app.register_error_handler(404, pagina_no_encontrada)
    app.run(debug=True, port = 5000)