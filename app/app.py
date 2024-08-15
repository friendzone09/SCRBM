from flask import Flask, render_template, url_for, redirect, request, flash, Blueprint, jsonify
import os
import uuid
import psycopg2

from  flask_wtf.csrf import CSRFProtect
from psycopg2.extras import RealDictCursor

from werkzeug.security import generate_password_hash
from flask_login import LoginManager, login_user,logout_user,login_required, current_user
from werkzeug.utils import secure_filename

from Models.ModelUser import ModuleUser
from Models.entities.user import User

import logging ### IMPORT LOGIN AÑADIDO PARA REALIZAR EL INSERT DE 
# ################ CONCEPTO Y EL INSERT DE BASICOS

app = Flask(__name__)
csrf = CSRFProtect()

#LLAMAR A LA BASE DE DATOS

def get_db_conection():
    try:
        conn=psycopg2.connect(host='localhost',
                              dbname='SCRBM2',
                              user = os.environ['username2'],
                              password =os.environ['password2'],
                              )
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
        password = request.form['contraseña_usuario']
        user = User(0, None, None, correo, password, None, None)
        loged_user = ModuleUser.login(get_db_conection(), user)

        if loged_user != None:
            if loged_user.password:
                login_user(loged_user)
                return redirect(url_for('dashboard'))
            else:
                flash('¡Advertencia: Contraseña incorrecta!')
                return redirect(url_for('index'))
        else:
            flash('¡Advertencia: Correo no resgitrado!')
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
        password = request.form['contraseña_usuario']

        password = generate_password_hash(password)

        activo = 'activo' in request.form and request.form.get('activo') == 'on'
        print(f"Valor de activo: {activo}")  # Depuración

        conn = get_db_conection()
        cur = conn.cursor()
        cur.execute('INSERT INTO public.usuarios (nombre, apellidos, correo_usuario, password, activo) '
                    'VALUES (%s, %s, %s, %s, %s)',
                    (nombre, apellidos, correo_usuario, password, activo))
        conn.commit()
        cur.close()
        conn.close()
        flash('!Usuario registrado correctamente!')
        return redirect(url_for('index'))
    return render_template('registrar_usuario.html')


#=========================================FIN INICIO DE SESION==================================================

def my_random_string(string_length=10):
    """Regresa una cadena aleatoria de la longitud de string_length."""
    random = str(uuid.uuid4()) # Conviente el formato UUID a una cadena de Python.
    random = random.upper() # Hace todos los caracteres mayusculas.
    random = random.replace("-","") # remueve el separador UUID '-'.
    return random[0:string_length] # regresa la cadena aleatoria.

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
fotos_ruta=app.config['UPLOAD FOLDER']='./app/static/img/uploads/'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#--------------------------------------------------DETALLES USUARIO---------------------------------------------

@app.route('/dashboard/usuarios/<string:id_usuario>')
@login_required
def usuarios_detalles(id_usuario):

    if str(current_user.id_usuario) != id_usuario:
        flash('¡Advertencia: No tienes permiso para ver los detalles de otro usuario.!')
        return redirect(url_for('usuarios_detalles', id_usuario=current_user.id_usuario))

    conn = get_db_conection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM usuarios WHERE id_usuario = %s', (id_usuario,))
    usuario = cur.fetchone()
    cur.close()
    conn.close()

    if usuario:
        return render_template('usuarios_detalles.html', usuario=usuario)
    else:
        flash('¡Error: Usuario no encontrado.!')
        return redirect(url_for('dashboard'))

#-----------------------------------------------EDITAR USUARIO--------------------------------------------------

@app.route('/editar/usuario/<int:id_usuario>', methods=['GET', 'POST'])
@login_required
def editar_usuario(id_usuario):
    # Verifica si el usuario actual es el mismo que el solicitado
    if current_user.id_usuario != id_usuario:
        flash('No tienes permiso para editar el perfil de otro usuario.')
        return redirect(url_for('editar_usuario', id_usuario=current_user.id_usuario))

    titulo = "Editar usuario" 
    conn = get_db_conection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM usuarios WHERE id_usuario=%s', (id_usuario,))
    usuario = cur.fetchone()
    cur.close()
    conn.close()

    if request.method == 'POST':
        return redirect(url_for('usuarios_actualizar', id_usuario=id_usuario))
    
    return render_template('editar_usuario.html', titulo=titulo, usuario=usuario)

@app.route('/dashboard/confirmar_contraseña/<int:id_usuario>', methods=['GET', 'POST'])
@login_required
def confirmar_contraseña(id_usuario):
    if current_user.id_usuario != id_usuario:
        return redirect(url_for('editar_usuario', id_usuario=current_user.id_usuario))

    conn = get_db_conection()
    cur = conn.cursor()

    cur.execute('SELECT nombre, apellidos FROM usuarios WHERE id_usuario = %s', (id_usuario,))
    usuario = cur.fetchone()

    if request.method == 'POST':
        password = request.form['password']
        confirmar_password = request.form['confirmar_password']

        if password != confirmar_password:
            flash('Las contraseñas no coinciden. Inténtalo de nuevo.')
            return redirect(url_for('confirmar_contraseña', id_usuario=id_usuario))

        password_hash = generate_password_hash(password)

        cur.execute('UPDATE usuarios SET password=%s WHERE id_usuario=%s', 
                    (password_hash, id_usuario))
        conn.commit()

        flash('¡Contraseña actualizada exitosamente!')
        return redirect(url_for('usuarios_detalles', id_usuario=id_usuario))

    cur.close()
    conn.close()

    return render_template('confirmar_contraseña.html', usuario=usuario)



@app.route('/dashboard/actualizar/<int:id_usuario>', methods=['POST'])
@login_required
def usuarios_actualizar(id_usuario):
    if current_user.id_usuario != id_usuario:
        return redirect(url_for('editar_usuario', id_usuario=current_user.id_usuario))

    nombre = request.form.get('nombre')
    apellidos = request.form.get('apellidos')
    password = request.form.get('password')
    imagen = request.files.get('foto')

    if password:  # Si se proporcionó una nueva contraseña, redirige a la confirmación
        return redirect(url_for('confirmar_contraseña', id_usuario=id_usuario))

    conn = get_db_conection()
    cur = conn.cursor()

    if imagen and allowed_file(imagen.filename):
        cadena_aleatoria = my_random_string(10)
        filename = apellidos + "_" + nombre + "_" + cadena_aleatoria + "_" + secure_filename(imagen.filename)
        file_path = os.path.join(fotos_ruta, filename)
        if os.path.exists(file_path):
            flash('Error: ¡Un archivo con el mismo nombre ya existe! Intente renombrar su archivo.')
            return redirect(url_for('editar_usuario', id_usuario=id_usuario))

        imagen.save(file_path)

        cur.execute('SELECT foto FROM usuarios WHERE id_usuario = %s', (id_usuario,))
        old_filename = cur.fetchone()[0]
        if old_filename:
            old_file_path = os.path.join(fotos_ruta, old_filename)
            if os.path.exists(old_file_path):
                os.remove(old_file_path)

        cur.execute('UPDATE usuarios SET nombre=%s, apellidos=%s, foto=%s WHERE id_usuario=%s',
                    (nombre, apellidos, filename, id_usuario))
    else:
        cur.execute('UPDATE usuarios SET nombre=%s, apellidos=%s WHERE id_usuario=%s',
                    (nombre, apellidos, id_usuario))

    conn.commit()
    cur.close()
    conn.close()

    flash('¡Perfil modificado exitosamente!')
    return redirect(url_for('usuarios_detalles', id_usuario=id_usuario))



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

#==========================================LISTAR OfICIOS=============================================================

def listar_oficios():
    conn = get_db_conection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM oficios WHERE visibilidad IS true')
    oficios= cur.fetchall()
    cur.close()
    conn.close()
    return oficios
  
#==========================================FIN LISTAR OfICIOS=============================================================

#================================================LISTAR MAQUINAS======================================================

def listar_maquinas():
    conn = get_db_conection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM maquinaria WHERE visibilidad IS true')
    maquinas = cur.fetchall()
    cur.close()
    conn.close()
    return maquinas

#============================================FIN LISTAR MAQUINAS=====================================================

#===============================================LISTAR PROYECTOS=====================================================

def listar_proyectos():
    conn = get_db_conection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM public.proyectos WHERE visible_proyecto=true LIMIT 3;')
    proyectos = cur.fetchall()
    cur.close()
    conn.close()
    return proyectos


#-=============================================FIN DASHBOARD===========================================================

#=========================================== Inicio Create Proyecto ==============================================

@app.route('/proyecto/registrar/proceso', methods=('GET', 'POST'))
def registrar_proyecto_proceso():
    if request.method == 'POST':
        fk_creador_proyecto = request.form['fk_creador_proyecto']
        nombre_proyecto = request.form['nombre_proyecto']
        titulo_proyecto = request.form['titulo_proyecto']
        colonia_proyecto = request.form['colonia_proyecto']
        municipio_proyecto = request.form['municipio_proyecto']
        estado_proyecto = request.form['estado_proyecto']
        nombrecliente_proyecto = request.form['nombrecliente_proyecto']
        gubernamental_proyecto = 'gubernamental_proyecto' in request.form

        conn = get_db_conection()
        cur = conn.cursor()
        cur.execute('INSERT INTO proyectos(fk_creador_proyecto, nombre_proyecto, titulo_proyecto, colonia_proyecto, municipio_proyecto, estado_proyecto, nombrecliente_proyecto, gubernamental_proyecto) '
                    'VALUES (%s,%s,%s,%s,%s,%s,%s,%s);',
                    (fk_creador_proyecto, nombre_proyecto, titulo_proyecto, colonia_proyecto, municipio_proyecto, estado_proyecto, nombrecliente_proyecto, gubernamental_proyecto,))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('dashboard'))
    return redirect(url_for('dashboard'))

#=========================================== Fin Create Proyecto ==============================================

#=========================================== Inicio Editar Proyecto ==============================================

@app.route('/proyecto/editar/<string:id_proyecto>', methods =['POST'] )
def editar_proyecto_proceso(id_proyecto):
    if request.method == 'POST':
        nombre_proyecto = request.form['nombre_proyecto']
        titulo_proyecto = request.form['titulo_proyecto']
        colonia_proyecto = request.form['colonia_proyecto']
        municipio_proyecto = request.form['municipio_proyecto']
        estado_proyecto = request.form['estado_proyecto']
        nombrecliente_proyecto = request.form['nombrecliente_proyecto']
        gubernamental_proyecto = request.form['gubernamental_proyecto']
        conn = get_db_conection()
        cur = conn.cursor()
        valores = (nombre_proyecto, titulo_proyecto, colonia_proyecto, municipio_proyecto, estado_proyecto, nombrecliente_proyecto, gubernamental_proyecto, id_proyecto)
        sql = 'UPDATE proyectos SET nombre_proyecto=%s, titulo_proyecto=%s, colonia_proyecto=%s, municipio_proyecto=%s, estado_proyecto=%s, nombrecliente_proyecto=%s, gubernamental_proyecto=%s WHERE id_proyecto=%s;'
        cur.execute(sql, valores)
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('detalles_proyecto', id_proyecto=id_proyecto))
    return redirect(url_for('detalles_proyecto', id_proyecto=id_proyecto))

#=========================================== Fin Editar Proyecto ==============================================

#=========================================== Inicio Eliminar Proyecto ==============================================

@app.route('/proyecto/eliminar/<string:id_proyecto>')
def eliminar_proyecto(id_proyecto):
    conn = get_db_conection()
    cur = conn.cursor()
    sql = "UPDATE proyectos SET visible_proyecto=false WHERE id_proyecto=%s;"
    cur.execute(sql, id_proyecto)
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('dashboard'))

#=========================================== Fin Eliminar Proyecto ==============================================

#=========================================== Inicio LEER DETALLES Proyecto (CONCEPTOS DE PROYECTO) ==============================================

@app.route('/proyecto/detalles/<string:id_proyecto>')
def detalles_proyecto(id_proyecto):
    conn = get_db_conection()
    cur = conn.cursor() ####### ESTA CONSULTA CAMBIOOOOOOOO PARA PODER VER AL CREADOR DEL PROYECTO #########################
    cur.execute('SELECT id_proyecto, fk_creador_proyecto, nombre_proyecto, titulo_proyecto, colonia_proyecto, municipio_proyecto, estado_proyecto, nombrecliente_proyecto, visible_proyecto, gubernamental_proyecto, usu.nombre, usu.apellidos FROM proyectos pro LEFT JOIN usuarios usu ON pro.fk_creador_proyecto = usu.id_usuario WHERE id_proyecto=%s;', (id_proyecto,))
    proyectaso = cur.fetchall()
    conn.commit()
    cur.execute('SELECT * FROM vista_conceptos WHERE fk_proy_con=%s;', (id_proyecto,))
    conceptos=cur.fetchall()
    conn.commit()
    cur.execute('SELECT id_unidad, nombre_unidad FROM public.unidades WHERE visibilidad_unidad=true;')
    unidades=cur.fetchall()
    conn.commit()
    cur.execute('SELECT * FROM vista_costo_proyectos WHERE fk_proy_con = %s;', (id_proyecto,))
    result = cur.fetchone()
    if result is None:
        costo_total_de_proyecto = 0
    else:
        costo_total_de_proyecto = result[1]
    conn.commit()   
    cur.close()
    conn.close()
    return render_template('detalles_proyecto.html', proyectaso=proyectaso[0], conceptos=conceptos,
                           unidades=unidades, costo_total_de_proyecto=costo_total_de_proyecto
                           )

#=========================================== Fin LEER DETALLES Proyecto (CONCEPTOS DE PROYECTO) ==============================================

#=========================================== Inicio REGISTRAR CONCEPTO DETALLES Proyecto (CONCEPTOS DE PROYECTO) ==============================================
@app.route('/proyecto/detalles/<string:id_proyecto>/registrarconcepto')
def registrar_concepto(id_proyecto):
    conn = get_db_conection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM unidades;')
    unidades = cur.fetchall()
    conn.commit()
    proyectaso = id_proyecto
    cur.close()
    conn.close()
    return render_template('registrar_concepto.html', unidades=unidades, proyectaso=proyectaso)

@app.route('/proyecto/detalles/<string:id_proyecto>/registrarconceptoproceso', methods=('GET', 'POST'))
def registrar_concepto_proceso(id_proyecto):
    nombre_concepto = request.form['nombre_concepto']
    fk_proy_con = int(request.form['fk_proy_con'])
    fk_unid_con = int(request.form['fk_unid_con'])
    cantidad_concepto = float(request.form['cantidad_concepto'])
    porcentajemaqyeq_con = float(request.form['porcentajemaqyeq_con'])
    indirectos_con = float(request.form['indirectos_con'])
    financiamiento_con = float(request.form['financiamiento_con'])
    utilidad_con = float(request.form['utilidad_con'])
    tratamiento_con = float(request.form['tratamiento_con'])
    if request.method == 'POST':
        try:
            conn = get_db_conection()
            cur = conn.cursor()

            cur.execute('CALL insert_concepto(%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                        (nombre_concepto, fk_proy_con, fk_unid_con, cantidad_concepto, porcentajemaqyeq_con, indirectos_con, financiamiento_con, utilidad_con, tratamiento_con))
            conn.commit()

            cur.close()
            conn.close()

            return redirect(url_for('detalles_proyecto', id_proyecto=id_proyecto))
        except Exception as e:
            logging.error(f"Error al registrar concepto: {e}")
            return f"Error al registrar concepto: {e}", 500
    return redirect(url_for('detalles_proyecto', id_proyecto=id_proyecto))

#=========================================== Fin REGISTRAR CONCEPTO DETALLES Proyecto (CONCEPTOS DE PROYECTO) ==============================================

@app.route('/proyecto/detalles/editarconcepto/<string:id_concepto>', methods=('GET', 'POST'))
def editar_concepto(id_concepto):
    nombre_concepto = request.form['nombre_concepto']
    fk_unid_con = request.form['fk_unid_con']
    cantidad_concepto = request.form['cantidad_concepto']
    indirectos_con = request.form['indirectos_con']
    financiamiento_con = request.form['financiamiento_con']
    utilidad_con = request.form['utilidad_con']
    tratamiento_con = request.form['tratamiento_con']
    if request.method == 'POST':
        conn = get_db_conection()
        cur = conn.cursor()
        cur.execute('UPDATE conceptos SET nombre_concepto=%s, fk_unid_con=%s, cantidad_concepto=%s, indirectos_con=%s, financiamiento_con=%s, utilidad_con=%s, tratamiento_con=%s WHERE id_concepto=%s;',
                    (nombre_concepto, fk_unid_con, cantidad_concepto, indirectos_con, financiamiento_con, utilidad_con, tratamiento_con, id_concepto,))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('detalles_concepto', id_concepto=id_concepto))
    return redirect(url_for('detalles_concepto', id_concepto=id_concepto))

#=========================================== Inicio ELIMINAR CONCEPTO DETALLES Proyecto (CONCEPTOS DE PROYECTO) ==============================================

@app.route('/proyecto/detalles/<string:id_proyecto>/eliminarconcepto/<string:id_concepto>')
def eliminar_concepto(id_proyecto, id_concepto):
    conn = get_db_conection()
    cur = conn.cursor()
    activo = False
    sql = 'UPDATE public.conceptos SET visible_con=%s WHERE id_concepto=%s;'
    cur.execute(sql, (activo, id_concepto))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('detalles_proyecto', id_proyecto=id_proyecto))

#=========================================== Fin ELIMINAR CONCEPTO DETALLES Proyecto (CONCEPTOS DE PROYECTO) ==============================================

#=========================================== Inicio DETALLES CONCEPTO Proyecto (CONCEPTOS) =====================================
@app.route('/proyecto/detalles/concepto/<string:id_concepto>/detalles/')
def detalles_concepto(id_concepto):
    conn = get_db_conection()
    cur = conn.cursor()

    cur.execute('SELECT * FROM vista_unidades;')
    unidades = cur.fetchall()

    cur.execute('SELECT costo_total_concepto FROM vista_conceptos WHERE id_concepto = %s;', (id_concepto,))
    result = cur.fetchone()
    if result is None:
        costo_concepto_total = 0
    else:
        costo_concepto_total = result[0]

    cur.execute('SELECT costo_completo_individual FROM vista_conceptos WHERE id_concepto = %s;', (id_concepto,))
    result = cur.fetchone()
    if result is None:
        costo_concepto_individual = 0
    else:
        costo_concepto_individual = result[0]

    sqlconceptos = "SELECT id_concepto, nombre_concepto, pr.nombre_proyecto, un.nombre_unidad, co.porcentaje_con, co.indirectos_con, financiamiento_con, utilidad_con, fk_proy_con, fk_unid_con, cantidad_concepto, fk_cuadrilla_con, cant_cuadrilla_con, porcentaje_con, indirectos_con, financiamiento_con, utilidad_con, visible_con, tratamiento_con FROM conceptos co INNER JOIN unidades un ON co.fk_unid_con = un.id_unidad INNER JOIN proyectos pr ON co.fk_proy_con = pr.id_proyecto WHERE visible_con = true AND id_concepto = %s;"
    cur.execute(sqlconceptos, (id_concepto,))
    concepton = cur.fetchone()
    conn.commit()
    id_de_cuadrilla_concepton = int(concepton[11])

    cur.execute('SELECT * FROM vista_costos_oficios_cuadrilla WHERE id_cuadrilla=%s;',
                (id_de_cuadrilla_concepton,))
    resultado = cur.fetchone()
    if resultado is not None:
        conteo_oficios_basico = tuple(resultado)
    else:
        conteo_oficios_basico = (0, 0, 0, 0)

    sqlmaterialesconcepto = "SELECT ma.id_material, ma.nombre_material, cm.costo_mat, cm.cant_conmat, (cm.cant_conmat * cm.costo_mat) AS importe, ma.visibilidad_material, un.nombre_unidad, cm.id_conmat, cm.fk_id_con FROM materiales ma INNER JOIN unidades un ON ma.fk_unidad = un.id_unidad INNER JOIN conceptosmateriales cm ON ma.id_material = cm.fk_id_mat WHERE cm.fk_id_con = %s;"
    cur.execute(sqlmaterialesconcepto, (id_concepto,))
    materialon = cur.fetchall()
    conn.commit()

    sqlmateriales = "SELECT id_material, nombre_material, costo_material, visibilidad_material, nombre_unidad FROM materiales INNER JOIN unidades ON materiales.fk_unidad = unidades.id_unidad WHERE visibilidad_material = true;"
    cur.execute (sqlmateriales)
    materiales = cur.fetchall()
    conn.commit()

    cur.execute('SELECT "coalesce" FROM public.vista_costo_materiales_concepto WHERE fk_id_con=%s;', (id_concepto,))
    result = cur.fetchone()
    if result is None:
        costo_total_materiales_concepto = 0
    else:
        costo_total_materiales_concepto = result[0]

    sqlmaquinariaconcepto = "SELECT mq.id_maquina, mq.nombre_maquina, cq.costo_maq, cq.cant_conmaq, (cq.costo_maq*cq.cant_conmaq) AS importe, mq.vida_util, mq.visibilidad, un.nombre_unidad, cq.id_conmaq, cq.fk_id_con, (mq.costo_maquina / mq.vida_util) FROM maquinaria mq INNER JOIN unidades un ON mq.fk_unidad = un.id_unidad INNER JOIN conceptosmaquinaria cq ON mq.id_maquina = cq.fk_id_maq WHERE cq.fk_id_con = %s;"
    cur.execute(sqlmaquinariaconcepto, (id_concepto,))
    maquinon = cur.fetchall()
    conn.commit()

    sqlmaquinaria = "SELECT id_maquina, nombre_maquina, costo_maquina, vida_util, visibilidad, nombre_unidad FROM maquinaria INNER JOIN unidades ON maquinaria.fk_unidad = unidades.id_unidad WHERE maquinaria.visibilidad = true;"
    cur.execute(sqlmaquinaria)
    maquinaria = cur.fetchall()

    cur.execute('SELECT xd FROM vista_costo_maquinaria_concepto WHERE fk_id_con = %s;', (id_concepto,))
    result = cur.fetchone()
    if result is None:
        costo_total_maquinaria_concepto = 0
    else:
        costo_total_maquinaria_concepto = result[0]

    sqlbasicon = "SELECT id_conbas, nombre_basico, uni.nombre_unidad, cb.costo_basico, cb.cantidad_conbas, (cb.costo_basico * cb.cantidad_conbas) AS importe FROM conceptosbasicos cb INNER JOIN basicos bas ON cb.fk_id_basico = bas.id_basico INNER JOIN conceptos con ON cb.fk_id_concepto = con.id_concepto INNER JOIN unidades uni ON bas.fk_unidad_basico = uni.id_unidad WHERE cb.fk_id_concepto = %s;"
    cur.execute(sqlbasicon, (id_concepto,))
    basicon = cur.fetchall()

    sqlbasicos = "SELECT * FROM vista_basicos;"
    cur.execute(sqlbasicos)
    basicos = cur.fetchall()

    cur.execute('SELECT total_basicos FROM vista_costo_basicos_concepto WHERE fk_id_concepto=%s;', (id_concepto,))
    result = cur.fetchone()
    if result is None:
        costo_total_basicos_concepto = 0
    else:
        costo_total_basicos_concepto = result[0]

    sqloficion = "SELECT ofi.id_oficio, ofi.nombre_oficio, uni.nombre_unidad, cuof.costo_oficio, cuof.cant_cuadofi, (cuof.costo_oficio * cuof.cant_cuadofi) AS importeoficio, cuof.id_cuadofi, con.fk_cuadrilla_con, con.id_concepto FROM cuadrillasoficios cuof INNER JOIN oficios ofi ON cuof.fk_id_oficio = ofi.id_oficio INNER JOIN cuadrillas cuad ON cuof.fk_id_cuadrilla = cuad.id_cuadrilla INNER JOIN conceptos con ON cuof.fk_id_cuadrilla = con.fk_cuadrilla_con INNER JOIN unidades uni ON ofi.fk_unidad = uni.id_unidad WHERE con.fk_cuadrilla_con = %s ORDER BY cuof.id_cuadofi;"
    cur.execute(sqloficion, (id_de_cuadrilla_concepton,))
    oficion = cur.fetchall()

    sqloficios = 'SELECT id_oficio, nombre_oficio, costo_oficio, uni.nombre_unidad, visibilidad FROM oficios ofi INNER JOIN unidades uni ON ofi.fk_unidad = uni.id_unidad;'
    cur.execute(sqloficios)
    oficios = cur.fetchall()

    cur.close()
    conn.close()
    return render_template('detalles_concepto.html', concepton=concepton,
                           materialon=materialon, materiales=materiales,
                           maquinon=maquinon, maquinaria=maquinaria,
                           basicon=basicon, basicos=basicos,
                           oficion=oficion ,oficios=oficios,
                           unidades=unidades, conteo_oficios_basico=conteo_oficios_basico,
                           costo_total_materiales_concepto=costo_total_materiales_concepto,
                           costo_total_maquinaria_concepto=costo_total_maquinaria_concepto,
                           costo_total_basicos_concepto=costo_total_basicos_concepto,
                           costo_concepto_total=costo_concepto_total,
                           costo_concepto_individual=costo_concepto_individual
                           )
#=========================================== Fin DETALLES CONCEPTO Proyecto (CONCEPTOS) ========================================



#=========================================== Inicio DETALLES CONCEPTO Proyecto - REGISTRAR MATERIAL A CONCEPTO =====================================
@app.route('/concepto/<string:fk_id_con>/detalles/material/<string:fk_id_mat>-costo-<string:costo_mat>/registrar')
def registrar_material_concepto(fk_id_con, fk_id_mat, costo_mat):
    conn = get_db_conection()
    cur = conn.cursor()
    sql = "INSERT INTO public.conceptosmateriales(fk_id_con, fk_id_mat, cant_conmat, costo_mat) VALUES (%s, %s, 1, %s);"
    cur.execute(sql, (fk_id_con, fk_id_mat, costo_mat,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('detalles_concepto', id_concepto=fk_id_con))
#=========================================== Fin DETALLES CONCEPTO Proyecto - REGISTRAR MATERIAL A CONCEPTO =====================================

#=========================================== Inicio DETALLES CONCEPTO Proyecto - EDITAR MATERIAL A CONCEPTO =====================================
@app.route('/concepto/<string:id_concepto>/detalles/material/editar/', methods=('GET', 'POST'))
def editar_material_concepto(id_concepto):
    id_conmat = request.form['id_conmat']
    cant_conmat = request.form['cant_conmat']
    if request.method == 'POST':
        conn = get_db_conection()
        cur = conn.cursor()
        cur.execute('UPDATE public.conceptosmateriales SET cant_conmat=%s WHERE id_conmat=%s;', (cant_conmat, id_conmat,))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('detalles_concepto', id_concepto=id_concepto))
    return redirect(url_for('detalles_concepto', id_concepto=id_concepto))
#=========================================== Fin DETALLES CONCEPTO Proyecto - EDITAR MATERIAL A CONCEPTO =====================================

#=========================================== Inicio DETALLES CONCEPTO Proyecto - ELIMINAR MATERIAL A CONCEPTO =====================================
@app.route('/concepto/<string:id_concepto>/detalles/material/eliminar/<string:id_conmat>')
def eliminar_material_concepto(id_conmat, id_concepto):
    conn = get_db_conection()
    cur = conn.cursor()
    sql = "DELETE FROM public.conceptosmateriales WHERE id_conmat=%s;"
    cur.execute(sql, (id_conmat,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('detalles_concepto', id_concepto=id_concepto))
#=========================================== Inicio DETALLES CONCEPTO Proyecto - ELIMINAR MATERIAL A CONCEPTO =====================================

#=========================================== Inicio DETALLES CONCEPTO Proyecto - Registrar MAQUINARIA A CONCEPTO =====================================
@app.route('/concepto/<string:fk_id_con>/detalles/maquinaria/<string:fk_id_maq>-costo-<string:costo_maq>/registrar')
def registrar_maquinaria_concepto(fk_id_con, fk_id_maq, costo_maq):
    conn = get_db_conection()
    cur = conn.cursor()
    sql = "INSERT INTO public.conceptosmaquinaria(fk_id_con, fk_id_maq, cant_conmaq, costo_maq) VALUES (%s, %s, 1, %s);"
    cur.execute(sql, (fk_id_con, fk_id_maq, costo_maq,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('detalles_concepto', id_concepto=fk_id_con))
#=========================================== Fin DETALLES CONCEPTO Proyecto - Registrar MAQUINARIA A CONCEPTO =====================================

#=========================================== Inicio DETALLES CONCEPTO Proyecto - EDITAR MAQUINARIA A CONCEPTO =====================================
@app.route('/concepto/<string:id_concepto>/detalles/maquinaria/editar/', methods=('GET', 'POST'))
def editar_maquinaria_concepto(id_concepto):
    id_conmaq = request.form['id_conmaq']
    cant_conmaq = request.form['cant_conmaq']
    if request.method == 'POST':
        conn = get_db_conection()
        cur = conn.cursor()
        cur.execute('UPDATE public.conceptosmaquinaria SET cant_conmaq=%s WHERE id_conmaq=%s;', (cant_conmaq, id_conmaq,))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('detalles_concepto', id_concepto=id_concepto))
    return redirect(url_for('detalles_concepto', id_concepto=id_concepto))
#=========================================== Fin DETALLES CONCEPTO Proyecto - EDITAR MAQUINARIA A CONCEPTO =====================================

#=========================================== Inicio DETALLES CONCEPTO Proyecto - ELIMINAR MAQUINARIA A CONCEPTO =====================================
@app.route('/concepto/<string:id_concepto>/detalles/maquinaria/eliminar/<string:id_conmaq>')
def eliminar_maquinaria_concepto(id_conmaq, id_concepto):
    conn = get_db_conection()
    cur = conn.cursor()
    sql = "DELETE FROM public.conceptosmaquinaria WHERE id_conmaq=%s;"
    cur.execute(sql, (id_conmaq,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('detalles_concepto', id_concepto=id_concepto))
#=========================================== Inicio DETALLES CONCEPTO Proyecto - ELIMINAR MAQUINARIA A CONCEPTO =====================================

#=========================================== Inicio DETALLES CONCEPTO Proyecto - REGISTRAR BASICO A CONCEPTO =====================================
@app.route('/concepto/<string:fk_id_concepto>/detalles/basico/<string:fk_id_basico>-costo-<string:costo_basico>/registrar')
def registrar_basico_concepto(fk_id_concepto, fk_id_basico, costo_basico):
    conn = get_db_conection()
    cur = conn.cursor()
    cur.execute('INSERT INTO conceptosbasicos(fk_id_concepto, fk_id_basico, cantidad_conbas, costo_basico) VALUES (%s, %s, 1, %s);',
                (fk_id_concepto, fk_id_basico, costo_basico))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('detalles_concepto', id_concepto=fk_id_concepto))
#=========================================== Fin DETALLES CONCEPTO Proyecto - REGISTRAR BASICO A CONCEPTO =====================================

#=========================================== Inicio DETALLES CONCEPTO Proyecto - EDITAR BASICO A CONCEPTO =====================================
@app.route('/concepto/<string:id_concepto>/detalles/basico/editar/', methods=('GET', 'POST'))
def editar_basico_concepto(id_concepto):
    id_conbas = request.form['id_conbas']
    cantidad_conbas = request.form['cantidad_conbas']
    if request.method == 'POST':
        conn = get_db_conection()
        cur = conn.cursor()
        cur.execute('UPDATE conceptosbasicos SET cantidad_conbas=%s WHERE id_conbas=%s;', (cantidad_conbas, id_conbas,))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('detalles_concepto', id_concepto=id_concepto))
    return redirect(url_for('detalles_concepto', id_concepto=id_concepto))
#=========================================== Fin DETALLES CONCEPTO Proyecto - EDITAR BASICO A CONCEPTO =====================================

#=========================================== Inicio DETALLES CONCEPTO Proyecto - ELIMINAR BASICO A CONCEPTO =====================================
@app.route('/concepto/<string:id_concepto>/detalles/basico/eliminar/<string:id_conbas>')
def eliminar_basico_concepto(id_conbas, id_concepto):
    conn = get_db_conection()
    cur = conn.cursor()
    sql = "DELETE FROM conceptosbasicos WHERE id_conbas=%s;"
    cur.execute(sql, (id_conbas,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('detalles_concepto', id_concepto=id_concepto))
#=========================================== Fin DETALLES CONCEPTO Proyecto - ELIMINAR BASICO A CONCEPTO =====================================

#=========================================== Inicio DETALLES CONCEPTO Proyecto - REGISTRAR OFICIO (a cuadrilla) =====================================
@app.route('/concepto/<string:id_concepto>/detalles/oficio/registrar')
def registrar_oficio_concepto(id_concepto):
    fk_id_cuadrilla = request.args.get('fk_id_cuadrilla')
    fk_id_oficio = request.args.get('fk_id_oficio')
    costo_oficio = request.args.get('costo_oficio')
    conn = get_db_conection()
    cur = conn.cursor()
    cur.execute('INSERT INTO cuadrillasoficios(fk_id_cuadrilla, fk_id_oficio, cant_cuadofi, costo_oficio) VALUES (%s, %s, 1, %s);',
                (fk_id_cuadrilla, fk_id_oficio, costo_oficio,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('detalles_concepto', id_concepto=id_concepto))
#=========================================== Fin DETALLES CONCEPTO Proyecto - REGISTRAR OFICIO (a cuadrilla) =====================================

#=========================================== Inicio DETALLES CONCEPTO Proyecto - EDITAR OFICIO A CONCEPTO =====================================
@app.route('/concepto/<string:id_concepto>/detalles/oficio/editar/', methods=('GET', 'POST'))
def editar_oficio_concepto(id_concepto):
    id_cuadofi = request.form['id_cuadofi']
    cant_cuadofi = request.form['cant_cuadofi']
    if request.method == 'POST':
        conn = get_db_conection()
        cur = conn.cursor()
        cur.execute('UPDATE cuadrillasoficios SET cant_cuadofi=%s WHERE id_cuadofi=%s;', (cant_cuadofi, id_cuadofi,))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('detalles_concepto', id_concepto=id_concepto))
    return redirect(url_for('detalles_concepto', id_concepto=id_concepto))
#=========================================== Fin DETALLES CONCEPTO Proyecto - EDITAR OFICIO A CONCEPTO =====================================

#=========================================== Inicio DETALLES CONCEPTO Proyecto - EDITAR CUADRILLA A CONCEPTO =====================================
@app.route('/concepto/<string:id_concepto>/detalles/cuadrilla/editar', methods=('GET', 'POST'))
def editar_cuadrilla_concepto(id_concepto):
    id_cuadrilla = request.form['id_cuadrilla']
    porcentaje_cuadrilla = request.form['porcentaje_cuadrilla']
    if request.method == 'POST':
        conn = get_db_conection()
        cur = conn.cursor()
        cur.execute('UPDATE cuadrillas SET porcentaje_cuadrilla=%s WHERE id_cuadrilla=%s;',
                    (porcentaje_cuadrilla, id_cuadrilla,))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('detalles_concepto', id_concepto=id_concepto))
    return redirect(url_for('detalles_concepto', id_concepto=id_concepto))
#=========================================== Fin DETALLES CONCEPTO Proyecto - EDITAR CUADRILLA A CONCEPTO =====================================

#===================================INICIO DETALLES BASICO - EDITAR CANTIDAD CUADRILLA DE BASICO====================================================
@app.route('/concepto/<string:id_concepto>/detalles/editar/cantidad_cuadrilla', methods=('GET', 'POST'))
def editar_cantidad_cuadrilla_concepto(id_concepto):
    cant_cuadrilla_con = request.form['cant_cuadrilla_con']
    if request.method == 'POST':
        conn = get_db_conection()
        cur = conn.cursor()
        cur.execute('UPDATE conceptos SET cant_cuadrilla_con=%s WHERE id_concepto=%s;',
                    (cant_cuadrilla_con, id_concepto,))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('detalles_concepto', id_concepto=id_concepto))
    return redirect(url_for('detalles_concepto', id_concepto=id_concepto))
#===================================FIN DETALLES BASICO - EDITAR CANTIDAD CUADRILLA DE BASICO====================================================

#=========================================== Inicio DETALLES CONCEPTO Proyecto - ELIMINAR OFICIO A CONCEPTO =====================================
@app.route('/concepto/<string:id_concepto>/detalles/oficio/editar/<string:id_cuadofi>', methods=('GET', 'POST'))
def eliminar_oficio_concepto(id_concepto, id_cuadofi):
    conn = get_db_conection()
    cur = conn.cursor()
    cur.execute('DELETE FROM cuadrillasoficios WHERE id_cuadofi=%s;', (id_cuadofi,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('detalles_concepto', id_concepto=id_concepto))
#=========================================== Fin DETALLES CONCEPTO Proyecto - ELIMINAR OFICIO A CONCEPTO =====================================

#-=============================================DASHBOARD===========================================================

@app.route ("/dashboard")
@login_required
def dashboard():
    sql_count = 'SELECT COUNT(*) FROM proyectos WHERE visible_proyecto = true' 
    sql_lim = 'SELECT * FROM public.proyectos WHERE visible_proyecto=true LIMIT %s OFFSET %s;'
    paginado = paginador(sql_count, sql_lim,1,8)
    
    return render_template('dashboard.html',
                           proyectos= paginado[0],
                           page = paginado[1],
                           per_page = paginado[2],
                           total_items = paginado[3],
                           total_pages = paginado[4],
                           listar_proyecto = listar_proyectos())


#-----------------------------------------------INICIO READ UNIDAD------------------------------------------------------

@app.route("/unidades")
@login_required
def unidades():
    sql_count= 'SELECT COUNT(*) FROM unidades WHERE visibilidad_unidad=true'
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
        flash('¡Unidad registrada correctamente!')
        return redirect(url_for('unidades'))
    return redirect(url_for('unidades'))

#-------------------------FIN REGISTRO UNIDAD------------------------------------------------------------------
         
#----------------------------INICIO UBDATE UNIDADE-----------------------------------------------------------------

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
        flash('¡Unidad editada!')
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
    flash('¡Se elimino la unidad!')
    return redirect (url_for('unidades'))

#========================================= FIN ELIMINAR UNIDADES ============================================

#===========================================INICIO READ MATERIALES=============================================

@app.route('/materiales')
@login_required
def materiales():
    sql_count= 'SELECT COUNT(*) FROM materiales where visibilidad_material=true'
    sql_lim = 'SELECT materiales.id_material, materiales.nombre_material, materiales.costo_material, unidades.nombre_unidad, fk_unidad FROM materiales INNER JOIN unidades ON materiales.fk_unidad = unidades.id_unidad WHERE visibilidad_material = true ORDER BY nombre_material ASC LIMIT %s OFFSET %s'     
    paginado = paginador(sql_count, sql_lim,1,7) 
    
   
    return render_template('materiales.html', 
                           materiales = paginado[0],
                           page = paginado[1],
                           per_page = paginado[2], 
                           total_items = paginado[3],
                           total_pages = paginado[4],
                           unidades = listar_unidad())


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
        flash('¡Material registrado correctamente!')
        return redirect(url_for('materiales'))
    return redirect(url_for('materiales'))

#-------------------------FIN REGISTRO MATERIAL------------------------------------------------------------------
    
#===============================INICIO UPDATE MATERIAL-============================================================

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
        flash('¡Material editado!')
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
    flash('!Se elimino el material¡')
    return redirect (url_for('materiales'))
    
    

#=======================================FIN ELIMINAR MATERIAL===================================================


#=======================================MAQUINARIA==============================================================

#---------------------------------------------READ MAQUINARIA---------------------------------------------------

@app.route("/maquinaria")
@login_required
def maquinaria():
    sql_count='SELECT COUNT(*) FROM maquinaria where visibilidad=true'
    sql_lim='SELECT maquinaria.id_maquina, maquinaria.nombre_maquina, maquinaria.costo_maquina, maquinaria.vida_util, unidades.nombre_unidad, fk_unidad FROM public.maquinaria INNER JOIN unidades ON fk_unidad = id_unidad WHERE  visibilidad IS true LIMIT %s OFFsET %s'
    paginado = paginador(sql_count,sql_lim, 1, 7)
    return render_template('maquinaria.html', maquinaria = paginado[0],
                           page = paginado[1],
                           per_page = paginado[2], 
                           total_items = paginado[3],
                           total_pages = paginado[4],
                           unidades = listar_unidad())

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
        flash('¡Maquina registrada correctamente!')
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
        flash('¡Maquina editada!')
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
    flash('¡Se elimino la maquina!')
    return redirect (url_for('maquinaria'))

#---------------------------------------------------------------------------------------------------------------------

#======================================= OFICIOS ===================================================

#=======================================INICIO READ OFICIOS==========================================================

@app.route('/oficios')
@login_required
def oficios():
    sql_count= 'SELECT COUNT(*) FROM oficios where visibilidad=true'
    sql_lim= 'SELECT id_oficio, nombre_oficio, unidades.nombre_unidad, costo_oficio, visibilidad, fk_unidad FROM oficios INNER JOIN unidades ON oficios.fk_unidad = unidades.id_unidad WHERE visibilidad = true ORDER BY nombre_oficio ASC LIMIT %s OFFSET %s'
    paginado = paginador(sql_count, sql_lim, 1, 7)
    return render_template('oficios.html', oficios = paginado[0],
                           page = paginado[1],
                           per_page = paginado[2], 
                           total_items = paginado[3],
                           total_pages = paginado[4],
                           unidades = listar_unidad())

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
        flash('¡Oficio registrado correctamente!')
        return redirect(url_for('oficios'))
    return redirect(url_for('oficios'))

#-------------------------FIN REGISTRO OFICIO------------------------------------------------------------------

#===============================INICIO UPDATE OFICIO-============================================================

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
        flash('¡Oficio editado!')
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
    flash('¡Se elimino el oficio!')
    return redirect (url_for('oficios'))

#=======================================FIN ELIMINAR OFICIO===================================================


#==================================================INICIO CRUD PROYECTOS/PROCESOS=================================================

#------------------------INICIO LEER BASICO-------------------
@app.route('/basicos')
def basicos():
    conn = get_db_conection()
    cur = conn.cursor()
    cur.execute('SELECT id_unidad, nombre_unidad FROM unidades WHERE visibilidad_unidad=true;')
    unidades = cur.fetchall()
    cur.close()
    conn.close()

    sql_count = 'SELECT COUNT(*) FROM vista_basicos' 
    sql_lim = 'SELECT * FROM vista_basicos LIMIT %s OFFSET %s;' # VISTA INSERTADA VISTA INSERTADA VISTA INSERTADA VISTA INSERTADA VISTA INSERTADA VISTA INSERTADA VISTA INSERTADA
    paginado = paginador(sql_count, sql_lim,1,8)
    return render_template('basicos.html', basicos = paginado[0],
                           page = paginado[1],
                           per_page = paginado[2],
                           total_items = paginado[3],
                           total_pages = paginado[4],
                           unidades=unidades)
#------------------------FIN LEER BASICO-------------------

#------------------------INICIO REGISTRAR BASICO-------------------
@app.route('/basico/registrar')
def registrar_basico():
    conn = get_db_conection()
    cur = conn.cursor()
    cur.execute('SELECt * FROM unidades;')
    unidades = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return render_template('registrar_basico.html', unidades=unidades)

@app.route('/basico/registrar/proceso', methods=('GET', 'POST'))
def registrar_basico_proceso():
    if request.method == 'POST':
        nombre_basico = request.form['nombre_basico']
        fk_unid_basico = int(request.form['fk_unid_basico'])
        porcentmaqyeq_bas = float(request.form['porcentmaqyeq_bas'])  # Asegúrate de que sea un float

        conn = get_db_conection()
        cur = conn.cursor()

        # Ejecutar el procedimiento almacenado
        cur.execute('CALL insert_basico(%s, %s, %s)', (nombre_basico, fk_unid_basico, porcentmaqyeq_bas))
        conn.commit()

        cur.close()
        conn.close()
        
        flash("¡Basico registrado correctamente!")
        return redirect(url_for('basicos'))
    return redirect(url_for('basicos'))
#------------------------FIN REGISTRAR BASICO-------------------

#------------------------INICIO EDITAR BASICO-------------------
@app.route('/basico/editar/<string:id_basico>', methods=('GET', 'POST'))
def editar_basico(id_basico):
    if request.method == 'POST':
        nombre_basico = request.form['nombre_basico']
        fk_unid_basico = request.form['fk_unid_basico']
        porcentmaqyeq_bas = request.form['porcentmaqyeq_bas']
        conn = get_db_conection()
        cur = conn.cursor()
        cur.execute('UPDATE basicos SET nombre_basico=%s, fk_unidad_basico=%s, porcentaje_basico=%s WHERE id_basico=%s;',
                    (nombre_basico, fk_unid_basico, porcentmaqyeq_bas, id_basico,))
        conn.commit()
        cur.close()
        conn.close()
        flash("¡Basico editado correctamente!")
        return redirect(url_for('detalles_basico', id_basico=id_basico))
    return redirect(url_for('detalles_basico', id_basico=id_basico))
#------------------------FIN EDITAR BASICO-------------------

#------------------------INICIO ELIMINAR BASICO-------------------
@app.route('/basico/eliminar/<string:id_basico>')
def eliminar_basico(id_basico):
    conn = get_db_conection()
    cur = conn.cursor()
    cur.execute('UPDATE basicos SET visible_basico=false WHERE id_basico=%s;',
                (id_basico,))
    conn.commit()
    cur.close()
    conn.close()
    flash('¡Basico eliminado correctamente!')
    return redirect(url_for('basicos'))
#------------------------FIN ELIMINAR BASICO-------------------

#------------------------INICIO DETALLES BASICO-------------------
@app.route('/basico/detalles/<string:id_basico>')
def detalles_basico(id_basico):
    conn = get_db_conection()
    cur = conn.cursor()

    ############### UNIDADES Y BASICON ##############

    cur.execute('SELECT * FROM vista_unidades;')
    unidades = cur.fetchall()

    cur.execute('SELECT * FROM vista_basicos WHERE id_basico = %s;',
                (id_basico,))
    basicon = cur.fetchone()
    fk_cuadrilla_basico_concepton = int(basicon[4])

    ########## SUMAS / CONTADORES PARA COSTES

    cur.execute('SELECT * FROM vista_costo_materiales_basico WHERE fk_id_basico = %s',
                (id_basico,))
    resultado = cur.fetchone()
    if resultado is not None:
        conteo_materiales_basico = resultado[1] if resultado[1] is not None else 0
    else:
        conteo_materiales_basico = 0

    cur.execute('SELECT * FROM vista_costos_oficios_cuadrilla WHERE id_cuadrilla=%s;',
                (fk_cuadrilla_basico_concepton,))
    resultado = cur.fetchone()
    if resultado is not None:
        conteo_oficios_basico = tuple(resultado)
    else:
        conteo_oficios_basico = (0, 0, 0, 0)

    ########## SELECTS DE MATERIALES

    cur.execute('SELECT id_material, nombre_material, un.nombre_unidad, costo_material FROM materiales ma INNER JOIN unidades un ON ma.fk_unidad = un.id_unidad WHERE visibilidad_material=true;')
    materiales = cur.fetchall()

    cur.execute('SELECT id_basmat, ma.nombre_material, un.nombre_unidad, bm.costo_material, bm.cant_basmat, (cant_basmat * bm.costo_material) AS importe FROM basicosmateriales bm INNER JOIN materiales ma ON bm.fk_id_material = ma.id_material INNER JOIN basicos ba ON bm.fk_id_basico = ba.id_basico INNER JOIN unidades un ON ma.fk_unidad = un.id_unidad WHERE fk_id_basico=%s ORDER BY bm.id_basmat;',
                (id_basico,))
    materialones = cur.fetchall()

    ########## SELECTS DE OFICIOS y CUADRILLAS

    cur.execute('SELECT id_oficio, nombre_oficio, uni.nombre_unidad, costo_oficio, visibilidad FROM oficios ofi INNER JOIN unidades uni ON ofi.fk_unidad = uni.id_unidad;')
    oficios = cur.fetchall()

    cur.execute('SELECT ofi.id_oficio, ofi.nombre_oficio, uni.nombre_unidad, cuof.costo_oficio, cuof.cant_cuadofi, (cuof.costo_oficio * cuof.cant_cuadofi) AS importeoficio, cuof.id_cuadofi FROM cuadrillasoficios cuof INNER JOIN oficios ofi ON cuof.fk_id_oficio = ofi.id_oficio INNER JOIN cuadrillas cuad ON cuof.fk_id_cuadrilla = cuad.id_cuadrilla INNER JOIN basicos bas ON cuof.fk_id_cuadrilla = bas.fk_cuadrilla_basico INNER JOIN unidades uni ON ofi.fk_unidad = uni.id_unidad WHERE bas.fk_cuadrilla_basico = %s ORDER BY cuof.id_cuadofi;',
                (fk_cuadrilla_basico_concepton,))
    oficiones = cur.fetchall()

    ##########

    cur.close()
    conn.close()
    return render_template('detalles_basico.html',
                           basicon=basicon, materiales=materiales,
                           oficios=oficios, unidades=unidades,
                           materialones=materialones,
                           oficiones=oficiones,
                           fk_cuadrilla_basico_concepton=fk_cuadrilla_basico_concepton,
                           conteo_materiales_basico=conteo_materiales_basico,
                           conteo_oficios_basico=conteo_oficios_basico
                           )
#------------------------FIN DETALLES BASICO-------------------

#------------------------INICIO DETALLES BASICO - EDITAR MATERIAL-------------------
@app.route('/basico/detalles/<string:id_basico>/registrarmaterial')
def registrar_material_basico(id_basico):
    fk_id_basico = request.args.get('fk_id_basico')
    fk_id_material = request.args.get('fk_id_material')
    costo_material = request.args.get('costo_material')
    conn = get_db_conection()
    cur = conn.cursor()
    cur.execute('INSERT INTO public.basicosmateriales(fk_id_basico, fk_id_material, cant_basmat, costo_material) VALUES (%s, %s, 1, %s);',(fk_id_basico, fk_id_material, costo_material,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('detalles_basico', id_basico=id_basico))
#------------------------FIN DETALLES BASICO - REGISTRAR MATERIAL-------------------

#------------------------INICIO DETALLES BASICO - EDITAR MATERIAL-------------------
@app.route('/basico/detalles/<string:id_basico>/editarmaterial', methods=('GET', 'POST'))
def editar_material_basico(id_basico):
    id_basmat= request.form['id_basmat']
    cant_basmat = request.form['cant_basmat']
    if request.method == 'POST':
        conn = get_db_conection()
        cur = conn.cursor()
        cur.execute('UPDATE basicosmateriales SET cant_basmat=%s WHERE id_basmat=%s;', (cant_basmat, id_basmat))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('detalles_basico', id_basico=id_basico))
    return redirect(url_for('detalles_basico', id_basico=id_basico))
#------------------------FIN DETALLES BASICO - EDITAR MATERIALES-------------------

#------------------------INICIO DETALLES BASICO - ELIMINAR MATERIAL-------------------
@app.route('/basico/detalles/<string:id_basico>/eliminarmaterial/<string:id_basmat>', methods=('GET', 'POST'))
def eliminar_material_basico(id_basico, id_basmat):
    conn = get_db_conection()
    cur = conn.cursor()
    cur.execute('DELETE FROM basicosmateriales WHERE id_basmat=%s;', (id_basmat,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('detalles_basico', id_basico=id_basico))
#------------------------FIN DETALLES BASICO - ELIMINAR MATERIAL-------------------

#------------------------INICIO DETALLES BASICO - REGISTRAR OFICIO (a cuadrilla)-------------------
@app.route('/basico/detalles/<string:id_basico>/registraroficio')
def registrar_oficio_basico(id_basico):
    fk_id_cuadrilla = request.args.get('fk_id_cuadrilla')
    fk_id_oficio = request.args.get('fk_id_oficio')
    costo_oficio = request.args.get('costo_oficio')
    conn = get_db_conection()
    cur = conn.cursor()
    cur.execute('INSERT INTO public.cuadrillasoficios(fk_id_cuadrilla, fk_id_oficio, cant_cuadofi, costo_oficio) VALUES (%s, %s, 1, %s);',
                (fk_id_cuadrilla, fk_id_oficio, costo_oficio))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('detalles_basico', id_basico=id_basico))
#------------------------FIN DETALLES BASICO - REGISTRAR OFICIO (a cuadrilla)-------------------

#------------------------INICIO DETALLES BASICO - EDITAR OFICIO-------------------
@app.route('/basico/detalles/<string:id_basico>/editaroficio', methods=('GET', 'POST'))
def editar_oficio_basico(id_basico):
    id_cuadofi = request.form['id_cuadofi']
    cant_cuadofi = request.form['cant_cuadofi']
    if request.method == 'POST':
        conn = get_db_conection()
        cur = conn.cursor()
        cur.execute('UPDATE public.cuadrillasoficios SET cant_cuadofi=%s WHERE id_cuadofi=%s;',
                    (cant_cuadofi, id_cuadofi,))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('detalles_basico', id_basico=id_basico))
    return redirect(url_for('detalles_basico', id_basico=id_basico))
#------------------------FIN DETALLES BASICO - EDITAR OFICIO-------------------

#------------------------INICIO DETALLES BASICO - EDITAR MATERIALES-------------------
@app.route('/basico/detalles/<string:id_basico>/editar_cuadrilla', methods=('GET', 'POST'))
def editar_cuadrilla_basico(id_basico):
    id_cuadrilla = request.form['id_cuadrilla']
    porcentaje_cuadrilla = request.form['porcentaje_cuadrilla']
    if request.method == 'POST':
        conn = get_db_conection()
        cur = conn.cursor()
        cur.execute('UPDATE cuadrillas SET porcentaje_cuadrilla=%s WHERE id_cuadrilla=%s;',
                    (porcentaje_cuadrilla, id_cuadrilla,))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('detalles_basico', id_basico=id_basico))
    return redirect(url_for('detalles_basico', id_basico=id_basico))
#------------------------FIN DETALLES BASICO - EDITAR MATERIALES-------------------

#------------------------INICIO DETALLES BASICO - EDITAR CANTIDAD CUADRILLA DE BASICO-------------------
@app.route('/basico/detalles/<string:id_basico>/editar_cantidad_cuad_basico', methods=('GET', 'POST'))
def editar_cantidad_cuadrilla_basico(id_basico):
    cantidad_cuad_basico = request.form['cantidad_cuad_basico']
    if request.method == 'POST':
        conn = get_db_conection()
        cur = conn.cursor()
        cur.execute('UPDATE basicos SET cantidad_cuad_basico=%s WHERE id_basico=%s;',
                    (cantidad_cuad_basico, id_basico,))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('detalles_basico', id_basico=id_basico))
    return redirect(url_for('detalles_basico', id_basico=id_basico))
#------------------------FIN DETALLES BASICO - EDITAR CANTIDAD CUADRILLA DE BASICO-------------------

#------------------------INICIO DETALLES BASICO - ELIMINAR OFICIO-------------------
@app.route('/basico/detalles/<string:id_basico>/eliminaroficio/<string:id_cuadofi>', methods=('GET', 'POST'))
def eliminar_oficio_basico(id_basico, id_cuadofi):
    conn = get_db_conection()
    cur = conn.cursor()
    cur.execute('DELETE FROM cuadrillasoficios WHERE id_cuadofi=%s;', (id_cuadofi,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('detalles_basico', id_basico=id_basico))
#------------------------FIN DETALLES BASICO - ELIMINAR OFICIO-------------------

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

@app.route('/papelera/eliminar/<string:id_unidad>')
@login_required
def papelera_eliminar_unidad(id_unidad):
    conn = get_db_conection()
    cur = conn.cursor()
    cur.execute('DELETE FROM public.unidades WHERE id_unidad=%s;',(id_unidad,))
    conn.commit()
    cur.close()
    conn.close()
    flash('¡Se elimino la unidad!')
    return redirect (url_for('papelera'))

@app.route('/unidad/restaurar/<string:id_unidad>')
@login_required
def restaurar_unidad(id_unidad):
    activo = True
    conn = get_db_conection()
    cur = conn.cursor()
    sql = 'UPDATE public.unidades SET visibilidad_unidad=%s WHERE id_unidad=%s'
    valores = (activo, id_unidad) 
    cur.execute(sql, valores)
    conn.commit()
    cur.close()
    conn.close()
    flash('¡Se restauro la unidad!')
    return redirect (url_for('papelera'))

@app.route('/papelera/eliminar/material/<string:id_material>')
@login_required
def eliminar_material_papelera(id_material):
    conn = get_db_conection()
    cur = conn.cursor()
    cur.execute('DELETE FROM public.materiales WHERE id_material = %s;', (id_material,))
    conn.commit()
    cur.close()
    conn.close()
    flash('¡Se elimino el material!')
    return redirect(url_for('papelera'))

@app.route('/material/restaurar/<string:id_material>')
@login_required
def restaurar_material(id_material):
    activo = True
    conn = get_db_conection()
    cur = conn.cursor()
    sql = 'UPDATE public.materiales SET visibilidad_material=%s WHERE id_material=%s'
    valores = (activo, id_material) 
    cur.execute(sql, valores)
    conn.commit()
    cur.close()
    conn.close()
    flash('¡Se restauro el material!')
    return redirect (url_for('papelera'))

@app.route('/papelera/oficio/eliminar/<string:id_oficio>')
@login_required
def eliminar_oficio_papelera(id_oficio):
    conn = get_db_conection()
    cur = conn.cursor()
    cur.execute('DELETE FROM public.oficios WHERE id_oficio = %s', (id_oficio,))
    conn.commit()
    cur.close()
    conn.close()
    flash('¡Material eliminado correctamente!')
    return redirect (url_for('papelera'))

@app.route('/oficio/restaurar/<string:id_oficio>')
@login_required
def restaurar_oficio(id_oficio):
    activo = True
    conn = get_db_conection()
    cur = conn.cursor()
    sql = 'UPDATE public.oficios SET visibilidad=%s WHERE id_oficio=%s'
    valores = (activo, id_oficio) 
    cur.execute(sql, valores)
    conn.commit()
    cur.close()
    conn.close()
    flash('¡Se restauro el oficio!')
    return redirect (url_for('papelera'))

@app.route('/papelera/maquina/eliminar/<string:id_maquina>')
@login_required
def eliminar_maquina_papelera(id_maquina):
    conn = get_db_conection()
    cur = conn.cursor()
    cur.execute('DELETE FROM public.maquinaria WHERE id_maquina = %s', (id_maquina,))
    conn.commit()
    cur.close()
    conn.close()
    flash('¡Maquina eliminada correctamente!')
    return redirect (url_for('papelera'))

@app.route('/maquina/restaurar/<string:id_maquina>')
@login_required
def restaurar_maquina(id_maquina):
    activo = True
    conn = get_db_conection()
    cur = conn.cursor()
    sql = 'UPDATE public.maquinaria SET visibilidad=%s WHERE id_maquina=%s'
    valores = (activo, id_maquina) 
    cur.execute(sql, valores)
    conn.commit()
    cur.close()
    conn.close()
    flash('¡Se restauro la maquina!')
    return redirect (url_for('papelera'))
    
#====================================FIN PAPELERA==================================================================    

def pagina_no_encontrada(error):
    return render_template('error404.html')


def acceso_no_autorizado(error):
    return render_template('error_401.html')


if __name__ =='__main__':
    csrf.init_app(app)
    app.register_error_handler(404, pagina_no_encontrada)
    app.register_error_handler(401, acceso_no_autorizado)
    app.run(debug=True, port = 5000)