from . import db
from werkzeug.security import generate_password_hash, check_password_hash

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)  # Título del post
    content = db.Column(db.Text, nullable=False)  # Texto estructurado o en HTML
    tags = db.Column(db.String(200), nullable=True)  # Tags separados por comas
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())  # Fecha de creación
    image_url = db.Column(db.String(300), nullable=True)  # URL de la imagen asociada
    comments = db.relationship('Comment', backref='post', lazy=True)

    def __repr__(self):
        return f'<BlogPost {self.title}>'

class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    subscribed_at = db.Column(db.DateTime, default=db.func.current_timestamp())


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)  # Contenido del comentario
    author = db.Column(db.String(100), nullable=False)  # Nombre del autor
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())  # Fecha de creación
    post_id = db.Column(db.Integer, db.ForeignKey('blog_post.id'), nullable=False)  # Relación con BlogPost

    def __repr__(self):
        return f'<Comment {self.content[:20]}>'  # Muestra los primeros 20 caracteres del comentario
