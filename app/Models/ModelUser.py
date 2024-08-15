from .entities.user import User

class ModuleUser():
    @classmethod
    def login(self, db, user):
        try:
            cur = db.cursor()
            sql = "SELECT id_usuario, nombre, apellidos, correo_usuario, password, foto, activo FROM usuarios WHERE correo_usuario = '{}'".format(user.correo_usuario)
            cur.execute(sql)
            row = cur.fetchone()
            if row != None:
                user = User(row[0],row[1],row[2],row[3],user.check_password(row[4],user.password),row[5],row[6])
                return user
            else:
                return None
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def get_by_id(self, db, id_usuario):
        try:
            cur = db.cursor()
            sql = "SELECT id_usuario, nombre, apellidos, correo_usuario, foto, activo FROM usuarios WHERE id_usuario = '{}'".format(id_usuario)
            cur.execute(sql)
            row = cur.fetchone()
            if row is not None:
                return User(row[0],row[1],row[2], row[3],None,row[4],row[5])
            else:
                return None
        except Exception as ex:
            raise Exception(ex)
