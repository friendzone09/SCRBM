from flask import Flask, render_template, url_for, redirect, request, flash
import os
import uuid
import psycopg2

from  flask_wtf.csrf import CSRFProtect
from psycopg2.extras import RealDictCursor

from werkzeug.security import generate_password_hash
from flask_login import LoginManager, login_user,logout_user,login_required, current_user

from Models.ModelUser import ModuleUser
from Models.entities.user import User




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

#================================================INICIO DE SESION=============================================

login_manager_app=LoginManager(app)

@login_manager_app.user_loader
def load_user(id_usuarios):
    return ModuleUser.get_by_id(get_db_conection(),id_usuarios)
    
app.secret_key='mysecretkey'



@app.route('/loguear', methods=('GET', 'POST'))
def loguear():
    if request.method == 'POST':
        correo = request.form['correo_usuario']
        contrasenhia = request.form['contraseña_usuario']

        user = User(0, None, None, correo, contrasenhia, None, None)
        loged_user = ModuleUser.login(get_db_conection(), user)

        if loged_user != None:
            if loged_user.contrasenhia_usuario:
                login_user(loged_user)
                return redirect(url_for('dashboard'))
            else:
                flash('Correo de usuario y/o Contraseña incorrecta.')
                return redirect(url_for('index'))
        else:
            flash('Correo de usuario y/o Contraseña incorrecta.')
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('index.html')



#------------------------------------------------REGISTRAR USUARIO---------------------------------------------------

@app.route("/usuarios/registrar", methods=('GET', 'POST'))
def registrar_usuario():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellidos = request.form['apellidos']
        correo_usuario = request.form['correo_usuario']
        contrasenhia_usuario = request.form['contraseña_usuario']

        contrasenhia_usuario = generate_password_hash(contrasenhia_usuario)
        
        

        activo = 'activo' in request.form and request.form.get('activo') == 'on'
        print(f"Valor de activo: {activo}")  # Depuración

        conn = get_db_conection()
        cur = conn.cursor()
        cur.execute('INSERT INTO public.usuarios (nombre, apellidos, correo_usuario, contrasenhia_usuario, activo) '
                    'VALUES (%s, %s, %s, %s, %s)',
                    (nombre, apellidos, correo_usuario, contrasenhia_usuario, activo))
        conn.commit()
        cur.close()
        conn.close()
        flash('Usuario registrado correctamente')
        return redirect(url_for('index'))
    return render_template('registrar_usuario.html')


#=========================================FIN INICIO DE SESION==================================================

@app.route ("/dashboard")
@login_required
def dashboard():
    return render_template('dashboard.html')




#=======================================================PAGINADOR=================================================
def paginador(sql_count,sql_lim,in_page,per_pages):
    page = request.args.get('page',in_page,type=int)
    per_page = request.args.get('per_page',per_pages, type=int)
    
    offset= (page - 1) * per_page
    
    conn = get_db_conection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute(sql_count)
    total_items = cursor.fetchone()['count']
    
    cursor.execute(sql_lim,(per_page, offset))
    items = cursor.fetchall()
    
    cursor.close()
    conn.close()    
    
    total_pages = (total_items + per_page - 1) // per_page
    
    return items, page, per_page, total_items, total_pages 

#=======================================FIN PAGINADOR=============================================================

#=============================================LISTAR MATERIAL=================================================
def  listar_materiales():
    conn= get_db_conection()
    cur=conn.cursor()
    cur.execute('SELECT * FROM materiales WHERE visibilidad_material = true ORDER BY nombre_material ASC')
    materiales=cur.fetchall()
    cur.close
    conn.close
    return materiales
#=========================================FIN LISTAR UNIDADES=====================================================

#=====================================================LISTAR UNIDAD=============================================
def listar_unidad():
    conn = get_db_conection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM unidades WHERE visibilidad_unidad IS true ORDER BY nombre_unidad ASC')
    unidades= cur.fetchall()
    cur.close()
    conn.close()
    return unidades

#=======================================FIN LISTAR UNIDAD===========================================================

#-----------------------------------------------INICIO READ UNIDAD------------------------------------------------------

@app.route("/unidades")
@login_required
def unidades():
    sql_count= 'SELECT COUNT(*) FROM unidades where visibilidad_unidad=true'
    sql_lim = 'SELECT * FROM public.unidades WHERE visibilidad_unidad = true ORDER BY id_unidad ASC LIMIT %s OFFSET %s'     
    paginado = paginador(sql_count, sql_lim,1,7) 
    
    return render_template('unidades.html',
                           unidades = paginado[0],
                           page = paginado[1],
                           per_page = paginado[2], 
                           total_items = paginado[3],
                           total_pages = paginado[4])

#-----------------------------------------------FIN READ UNIDAD ------------------------------------------------------




#-------------------------INICIO REGISTRO UNIDAD------------------------------------------------------------------


@app.route("/unidades/registrar")
@login_required
def form_regis_unidad():
    return render_template('registrar_unidad.html')


@app.route("/unidades/registrar/regitrando", methods=('GET', 'POST'))
@login_required
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
@login_required
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
@login_required
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
        flash('Unidad editada')
        return redirect (url_for('unidades'))
    return redirect (url_for('unidades'))

#----------------------------FIN UBDATE UNIDADE-----------------------------------------------------------------

#========================================= INICIO ELIMINAR UNIDADES ============================================

@app.route('/unidad/eliminar/<string:id_unidad>')
@login_required
def eliminar_unidad(id_unidad):
    activo = False
    conn = get_db_conection()
    cur = conn.cursor()
    sql = 'UPDATE unidades SET visibilidad_unidad=%s WHERE id_unidad=%s'
    valores = (activo, id_unidad) 
    cur.execute(sql, valores)
    conn.commit()
    cur.close()
    conn.close()
    flash('Se elimino la unidad')
    return redirect (url_for('unidades'))

#========================================= FIN ELIMINAR UNIDADES ============================================

#===========================================INICIO READ MATERIALES=============================================

@app.route('/materiales')
@login_required
def materiales():
    sql_count= 'SELECT COUNT(*) FROM materiales where visibilidad_material=true'
    sql_lim = 'SELECT materiales.id_material, materiales.nombre_material, materiales.costo_material, unidades.nombre_unidad FROM materiales INNER JOIN unidades ON materiales.fk_unidad = unidades.id_unidad WHERE visibilidad_material = true ORDER BY nombre_material ASC LIMIT %s OFFSET %s'     
    paginado = paginador(sql_count, sql_lim,1,7) 
   
    return render_template('materiales.html', 
                           materiales = paginado[0],
                           page = paginado[1],
                           per_page = paginado[2], 
                           total_items = paginado[3],
                           total_pages = paginado[4])


#=======================================+FIN READ MATERIALES===================================================


#-------------------------INICIO REGISTRO MATERIAL------------------------------------------------------------------


@app.route("/materiales/registrar")
@login_required
def registrar_material():
    return render_template('registrar_material.html', unidades = listar_unidad())


@app.route("/materiales/registrar/proceso", methods=('GET', 'POST'))
@login_required
def registrar_material_proceso():
    if request.method == 'POST':
        nombre_material = request.form['nombre_material']
        costo_material = request.form['costo_material']
        fk_unidad = request.form['fk_unidad']
        
        conn = get_db_conection()
        cur = conn.cursor()
        cur.execute('INSERT INTO public.materiales(nombre_material, costo_material,  fk_unidad) '
	                'VALUES (%s, %s, %s);',
                    (nombre_material, costo_material, fk_unidad,))
        conn.commit()
        cur.close()
        conn.close()
        flash('Material registrado correctamente')
        return redirect(url_for('materiales'))
    return redirect(url_for('materiales'))

#-------------------------FIN REGISTRO MATERIAL------------------------------------------------------------------
    
#===============================INICIO UPDATE MATERIAL-============================================================
@app.route('/material/editar/<string:id_material>')
@login_required
def editar_material(id_material):
    conn = get_db_conection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM materiales WHERE id_material ={0}'.format(id_material))
    materiales = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return render_template('editar_material.html', materiales = materiales[0], unidades = listar_unidad())

@app.route('/material/editar/proceso/<string:id_material>', methods =['POST'] )
@login_required
def editar_material_proceso(id_material):
    if request.method == 'POST':
        nombre_material = request.form['nombre_material']
        costo_material = request.form['costo_material']
        fk_unidad = request.form['fk_unidad']
        
        conn = get_db_conection()
        cur = conn.cursor()
        sql = "UPDATE materiales SET nombre_material=%s, costo_material=%s, fk_unidad = %s WHERE id_material =%s;"
        valores = (nombre_material, costo_material, fk_unidad, id_material)
        cur.execute(sql, valores)
        conn.commit()
        cur.close()
        conn.close()
        flash('Material editado')
        return redirect (url_for('materiales'))
    return redirect (url_for('materiales'))



#================================FIN UPDATE MATERIAL============================================================

#===================================INICIO ELIMINAR MATERIAL====================================================

@app.route('/material/eliminar/<string:id_material>')
@login_required
def eliminar_material(id_material):
    activo = False
    conn = get_db_conection()
    cur = conn.cursor()
    sql = 'UPDATE materiales SET visibilidad_material=%s WHERE id_material=%s'
    valores = (activo, id_material) 
    cur.execute(sql, valores)
    conn.commit()
    cur.close()
    conn.close()
    flash('Se elimino el material')
    return redirect (url_for('materiales'))
    
    

#=======================================FIN ELIMINAR MATERIAL===================================================


#=======================================MAQUINARIA==============================================================

#---------------------------------------------READ MAQUINARIA---------------------------------------------------

@app.route("/maquinaria")
@login_required
def maquinaria():
    sql_count='SELECT COUNT(*) FROM maquinaria where visibilidad=true'
    sql_lim='SELECT maquinaria.id_maquina, maquinaria.nombre_maquina, maquinaria.costo_maquina, maquinaria.vida_util, unidades.nombre_unidad FROM maquinaria INNER JOIN unidades ON fk_unidad = id_unidad WHERE  visibilidad IS true LIMIT %s OFFsET %s'
    paginado = paginador(sql_count,sql_lim, 1, 7)
    return render_template('maquinaria.html', maquinaria = paginado[0],
                           page = paginado[1],
                           per_page = paginado[2], 
                           total_items = paginado[3],
                           total_pages = paginado[4])

#--------------------------------------------REGISTRO MAQUINARIA----------------------------------------------------

@app.route("/maquinaria/registrar")
@login_required
def registrar_maquinaria():
    return render_template('registrar_maquinaria.html', unidades = listar_unidad())


@app.route("/maquinaria/registrar/proceso", methods=('GET', 'POST'))
@login_required
def registrar_maquinaria_proceso():
    if request.method == 'POST':
        nombre_maquina = request.form['nombre_maquina']
        costo_maquina = request.form['costo_maquina']
        vida_util = request.form['vida_util']
        fk_unidad =  request.form['fk_unidad']
        
        conn = get_db_conection()
        cur = conn.cursor()
        cur.execute('INSERT INTO public.maquinaria(nombre_maquina, costo_maquina, vida_util, fk_unidad) '
	                'VALUES (%s, %s, %s, %s);',
                    (nombre_maquina, costo_maquina, vida_util, fk_unidad,))
        conn.commit()
        cur.close()
        conn.close()
        flash('Maquina registrada correctamente')
        return redirect(url_for('maquinaria'))
    return redirect(url_for('maquinaria'))

#------------------------------------------UPDATE MAQUINARIA---------------------------------------------------------

@app.route('/maquina/editar/<int:id_maquina>')
@login_required
def editar_maquina(id_maquina):
    conn = get_db_conection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM maquinaria WHERE id_maquina = %s;', (id_maquina,))
    maquinaria = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return render_template('editar_maquinaria.html', maquinaria=maquinaria[0], unidades=listar_unidad())

@app.route('/maquina/editar/proceso/<string:id_maquina>', methods =['POST'] )
@login_required
def editar_maquina_proceso(id_maquina):
    if request.method == 'POST':
        nombre_maquina = request.form['nombre_maquina']
        costo_maquina = request.form['costo_maquina']
        vida_util = request.form['vida_util']
        fk_unidad =  request.form['fk_unidad']
        
        conn = get_db_conection()
        cur = conn.cursor()
        sql = "UPDATE maquinaria SET nombre_maquina=%s, costo_maquina=%s, vida_util = %s, fk_unidad=%s WHERE id_maquina =%s;"
        valores = (nombre_maquina, costo_maquina, vida_util, fk_unidad, id_maquina)
        cur.execute(sql, valores)
        conn.commit()
        cur.close()
        conn.close()
        flash('Maquina editada')
        return redirect (url_for('maquinaria'))
    return redirect (url_for('maquinaria'))

#--------------------------------------------------ELIMINAR MAQUINARIA------------------------------------------------

@app.route('/maquinaria/eliminar/<string:id_maquina>')
@login_required
def eliminar_maquinaria(id_maquina):
    activo = False
    conn = get_db_conection()
    cur = conn.cursor()
    sql = 'UPDATE maquinaria SET visibilidad=%s WHERE id_maquina=%s'
    valores = (activo, id_maquina) 
    cur.execute(sql, valores)
    conn.commit()
    cur.close()
    conn.close()
    flash('Se elimino la maquina')
    return redirect (url_for('maquinaria'))

#---------------------------------------------------------------------------------------------------------------------

#======================================= OFICIOS ===================================================

#=======================================INICIO READ OFICIOS==========================================================

@app.route('/oficios')
@login_required
def oficios():
    sql_count= 'SELECT COUNT(*) FROM oficios where visibilidad=true'
    sql_lim= 'SELECT id_oficio, nombre_oficio, unidades.nombre_unidad, costo_oficio, visibilidad  FROM oficios INNER JOIN unidades ON oficios.fk_unidad = unidades.id_unidad WHERE visibilidad = true ORDER BY nombre_oficio ASC LIMIT %s OFFSET %s'
    paginado = paginador(sql_count, sql_lim, 1, 7)
    return render_template('oficios.html', oficios = paginado[0],
                           page = paginado[1],
                           per_page = paginado[2], 
                           total_items = paginado[3],
                           total_pages = paginado[4])

#======================================= FIN READ OFICIOS ===========================================================

#-------------------------INICIO REGISTRO OFICIO------------------------------------------------------------------

@app.route("/oficios/registrar")
@login_required
def registrar_oficio():
    return render_template('registrar_oficio.html', unidades = listar_unidad())


@app.route("/oficios/registrar/proceso", methods=('GET', 'POST'))
@login_required
def registrar_oficio_proceso():
    if request.method == 'POST':
        nombre_oficio = request.form['nombre_oficio']
        costo_oficio = request.form['costo_oficio']
        fk_unidad = request.form['fk_unidad']
        
        conn = get_db_conection()
        cur = conn.cursor()
        cur.execute('INSERT INTO public.oficios(nombre_oficio, costo_oficio, fk_unidad) VALUES (%s, %s, %s)', (nombre_oficio, costo_oficio, fk_unidad))
        conn.commit()
        cur.close()
        conn.close()
        flash('Oficio registrado correctamente')
        return redirect(url_for('oficios'))
    return redirect(url_for('oficios'))

#-------------------------FIN REGISTRO OFICIO------------------------------------------------------------------

#===============================INICIO UPDATE OFICIO-============================================================

@app.route('/oficio/editar/<string:id_oficio>')
@login_required
def editar_oficio(id_oficio):
    conn = get_db_conection()
    cur = conn.cursor()

    cur.execute('SELECT id_oficio, nombre_oficio, unidades.nombre_unidad, costo_oficio, visibilidad '
                'FROM oficios '
                'INNER JOIN unidades '
                'ON oficios.fk_unidad = unidades.id_unidad '
                'WHERE id_oficio ={0}'.format(id_oficio))
    oficios = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return render_template('editar_oficio.html', oficios=oficios[0], unidades = listar_unidad())

@app.route('/oficio/editar/proceso/<string:id_oficio>', methods =['POST'] )
@login_required
def editar_oficio_proceso(id_oficio):
    if request.method == 'POST':
        nombre_oficio = request.form['nombre_oficio']
        costo_oficio = request.form['costo_oficio']
        fk_unidad = request.form['fk_unidad']

        conn = get_db_conection()
        cur = conn.cursor()
        sql = "UPDATE public.oficios SET nombre_oficio=%s, costo_oficio=%s, fk_unidad=%s WHERE id_oficio=%s"
        valores = (nombre_oficio, costo_oficio, fk_unidad, id_oficio)
        cur.execute(sql, valores)
        conn.commit()
        cur.close()
        conn.close()
        flash('Oficio editado')
        return redirect (url_for('oficios'))
    return redirect (url_for('oficios'))

#================================FIN UPDATE OFICIO============================================================

#===================================INICIO ELIMINAR OFICIO====================================================

@app.route('/oficio/eliminar/<string:id_oficio>')
@login_required
def eliminar_oficio(id_oficio):
    activo = False
    conn = get_db_conection()
    cur = conn.cursor()
    sql = 'UPDATE oficios SET visibilidad=%s WHERE id_oficio=%s'
    valores = (activo, id_oficio) 
    cur.execute(sql, valores)
    conn.commit()
    cur.close()
    conn.close()
    flash('Se elimino el oficio')
    return redirect (url_for('oficios'))

#=======================================FIN ELIMINAR OFICIO===================================================





#======================================INICIO PAPELERA============================================================
         
@app.route('/papelera')
@login_required
def papelera():
    conn = get_db_conection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM public.unidades '
	            'WHERE visibilidad_unidad = false '
                'ORDER BY id_unidad ASC')
    unidades = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    
    conn = get_db_conection()
    cur = conn.cursor()
    cur.execute('SELECT materiales.id_material, materiales.nombre_material, materiales.costo_material, unidades.nombre_unidad' 
	            ' FROM materiales INNER JOIN unidades ON materiales.fk_unidad = unidades.id_unidad '
                'WHERE visibilidad_material = false '
                'ORDER BY nombre_material')
    materiales = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    
    conn = get_db_conection()
    cur = conn.cursor()
    cur.execute('SELECT id_oficio, nombre_oficio, unidades.nombre_unidad, costo_oficio, visibilidad '
                'FROM oficios '
                'INNER JOIN unidades '
                'ON oficios.fk_unidad = unidades.id_unidad '
                'WHERE visibilidad = false '
                'ORDER BY nombre_oficio ASC ')
    oficios = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    
    conn = get_db_conection()
    cur = conn.cursor()
    cur.execute('SELECT maquinaria.id_maquina, maquinaria.nombre_maquina, maquinaria.costo_maquina, ' 
	            'maquinaria.vida_util, unidades.nombre_unidad FROM maquinaria INNER JOIN unidades ' 
	            'ON fk_unidad = id_unidad WHERE visibilidad = false ')
    maquinaria = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    
    
    return render_template('papelera.html', unidades = unidades, materiales = materiales, oficios=oficios, maquinaria=maquinaria)

#====================================FIN PAPELERA==================================================================    


#FUNCION TEMPORAL

@app.route('/cotizacion')
def cotizacion():
    conn = get_db_conection()
    cur = conn.cursor()
    cur.execute('SELECT nombre_material, costo_material FROM materiales WHERE visibilidad_material = true')
    materiales = cur.fetchall()
    cur.close()
    conn.close()
    
    total = sum([material[1] for material in materiales])
    
    return render_template('cotizacion.html', materiales=materiales, total=total, listar_materiales=listar_materiales())

def pagina_no_encontrada(error):
    return render_template('error404.html')


def acceso_no_autorizado(error):
    return render_template('error_401.html')


if __name__ =='__main__':
    csrf.init_app(app)
    app.register_error_handler(404, pagina_no_encontrada)
    app.register_error_handler(401, acceso_no_autorizado)
    app.run(debug=True, port = 5000)
    
    
