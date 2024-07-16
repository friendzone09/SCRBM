from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin

class User(UserMixin):

    def get_id(self):
        return self.id_usuario

    def __init__(self, id_usuario, nombre, apellidos, correo_usuario, contrasenhia_usuario, img_usuario, activo) -> None:
        self.id_usuario = id_usuario
        self.nombre = nombre
        self.apellidos = apellidos
        self.correo_usuario = correo_usuario
        self.contrasenhia_usuario = contrasenhia_usuario
        self.img_usuario = img_usuario
        self.activo = activo

    @classmethod
    def check_password(cls, hashed_password, password):
        return check_password_hash(hashed_password, password)
