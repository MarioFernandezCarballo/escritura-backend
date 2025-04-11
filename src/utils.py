import resend
import os
from flask import jsonify, request
from . import db
from .models import BlogPost as BlogPostModel, Subscriber as SubscriberModel, Comment, Admin as AdminModel, Newsletter as NewsletterModel
from .schemas import BlogPostCreate, BlogPost as BlogPostSchema
from .schemas import SubscriberCreate, Subscriber as SubscriberSchema
from .schemas import CommentCreate, Comment as CommentSchema
from .schemas import AdminLogin, TokenResponse, NewsletterCreate, Newsletter as NewsletterSchema
from jose import JWTError, jwt
from datetime import datetime, timedelta
from functools import wraps

resend.api_key = 're_2X64sqGS_6Zdn8rTiStRRWCBt76gPWr21'

class Contact():
    def handleContact(request):
        data = request.json
        try:
            resend.Emails.send({
                "from": "Mario Carballo <developer@mariocarballo.es>",
                "to": "mariofernandezcarballo@gmail.com",
                "subject": f"Nuevo mensaje de contacto de {data.get('name')}",
                "html": f"""
                    <h2>Nuevo mensaje de contacto</h2>
                    <p><strong>Nombre:</strong> {data.get('name')}</p>
                    <p><strong>Email:</strong> {data.get('email')}</p>
                    <p><strong>Asunto:</strong> {data.get('subject')}</p>
                    <p><strong>Mensaje:</strong></p>
                    <p>{data.get('message')}</p>
                """
            })
            return jsonify({"message": "Mensaje enviado correctamente"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

class Post:
    def post(request):
        post_data = BlogPostCreate.model_validate(request.json)
        tags_string = ','.join(post_data.tags) if post_data.tags else ""
        new_post = BlogPostModel(
            title=post_data.title,
            content=post_data.content,
            tags=tags_string,
            image_url=post_data.image_url
        )
        db.session.add(new_post)
        db.session.commit()
        return jsonify(BlogPostSchema.model_validate(new_post).model_dump())
    
    def getAll():
        posts = BlogPostModel.query.all()
        return jsonify([BlogPostSchema.model_validate(post).model_dump() for post in posts])

    def get(id):
        post = BlogPostModel.query.get_or_404(id)
        # The conversion is now handled by the Pydantic model
        return jsonify(BlogPostSchema.model_validate(post).model_dump())
    
    def addComment(postId, request):
        comment_data = CommentCreate.model_validate(request.json)
        post = BlogPostModel.query.get_or_404(postId)
        new_comment = Comment(
            content=comment_data.content,
            author=comment_data.author,
            post_id=post.id
        )
        db.session.add(new_comment)
        db.session.commit()
        return jsonify(CommentSchema.model_validate(new_comment).model_dump())

class Subscriber:
    @classmethod
    def add(cls, request):
        subscriber_data = SubscriberCreate.model_validate(request.json)
        new_subscriber = SubscriberModel(email=subscriber_data.email)
        db.session.add(new_subscriber)
        db.session.commit()
        cls.sendWelcome(new_subscriber)
        return jsonify(SubscriberSchema.model_validate(new_subscriber).model_dump())
    
    def delete(id):
        subscriber = SubscriberModel.query.get_or_404(id)
        db.session.delete(subscriber)
        db.session.commit()
        return '', 204
    
    def deleteByEmail(email):
        subscriber = SubscriberModel.query.filter_by(email=email).first_or_404()
        db.session.delete(subscriber)
        db.session.commit()
        return '', 204
    
    def get():
        subscribers = SubscriberModel.query.all()
        return jsonify([SubscriberSchema.model_validate(sub).model_dump() for sub in subscribers])
    
    def sendWelcome(subscriber):
        content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; max-width: 600px; padding: 20px;">
                <p>¡Bienvenido/a a nuestra comunidad!</p>
                <p>Estoy encantado de que te hayas unido. A partir de ahora, recibirás novedades, relatos exclusivos y contenido especial directamente en tu bandeja de entrada.</p>
                <p>Si en algún momento deseas dejar de recibir nuestros correos, puedes darte de baja entrando en el siguiente enlace:</p>
                <p><a style="cursor: pointer;" href="https://mariocarballo.es/unsubscribe">https://mariocarballo.es/unsubscribe</a></p>
                <p>¡Gracias por unirte y espero que disfrutes de mi contenido!</p>
                <p>Un cordial saludo,</p>
                <p>Mario Carballo</p>
                <p style="font-size: 12px; color: #888888;">*Nota: Este correo electrónico ha sido enviado a {subscriber.email}. Si no te has suscrito a nuestra lista o crees que has recibido este mensaje por error, por favor, ignóralo.*</p>
            </body>
            </html>
        """
        resend.Emails.send({
                "from": "Mario Carballo <developer@mariocarballo.es>",
                "to": subscriber.email,
                "subject": "¡Gracias por unirte a la comunidad!",
                "html": content
            })


class Newsletter:
    def get():
        newsletters = NewsletterModel.query.all()
        return jsonify([NewsletterSchema.model_validate(n).model_dump() for n in newsletters])
    
    def post(request):
        newsletter_data = NewsletterCreate.model_validate(request.json)
        new_newsletter = NewsletterModel(
            subject=newsletter_data.subject,
            content=newsletter_data.content,
            scheduled_for=newsletter_data.scheduled_for,
            status='scheduled'
        )
        db.session.add(new_newsletter)
        db.session.commit()
        return jsonify(NewsletterSchema.model_validate(new_newsletter).model_dump())
    
    def delete(id):
        newsletter = NewsletterModel.query.get_or_404(id)
        db.session.delete(newsletter)
        db.session.commit()
        return '', 204
    
    def send(id):
        newsletter = NewsletterModel.query.get_or_404(id)
        subscribers = SubscriberModel.query.all()
        
        try:
            # Preparar el lote de emails
            batch_emails = [{
                "from": "Mario Carballo <developer@mariocarballo.es>",
                "to": [subscriber.email],
                "subject": newsletter.subject,
                "html": newsletter.content
            } for subscriber in subscribers]
            
            # Enviar todos los emails en una sola llamada API
            resend.Batch.send(batch_emails)
            
            newsletter.status = 'sent'
            newsletter.sent_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                "message": "Newsletter sent successfully",
                "recipients": len(subscribers)
            })
        except Exception as e:
            return jsonify({
                "error": f"Failed to send newsletter: {str(e)}"
            }), 500

class Auth:
    SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-here')  # In production, use environment variable
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

    @classmethod
    def login(cls, request):
        login_data = AdminLogin.model_validate(request.json)
        admin = AdminModel.query.filter_by(username=login_data.username).first()
        if not admin or not admin.check_password(login_data.password):
            return jsonify({"error": "Invalid credentials"}), 401
        access_token = cls.createAccessToken({"sub": admin.username})
        return jsonify(TokenResponse(access_token=access_token).model_dump())

    @classmethod
    def createAccessToken(cls, data):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, cls.SECRET_KEY, algorithm=cls.ALGORITHM)
        return encoded_jwt
    
    @classmethod
    def verifyToken(cls, token):
        try:
            payload = jwt.decode(token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                return None
            return username
        except JWTError:
            return None
    
    @classmethod
    def getCurrentUser(cls):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        token = auth_header.split(' ')[1]
        username = cls.verifyToken(token)
        if not username:
            return None
        return AdminModel.query.filter_by(username=username).first()
    
    @classmethod
    def adminRequired(cls, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            current_user = cls.getCurrentUser()
            if not current_user:
                return jsonify({"error": "Not authenticated"}), 401
            return f(*args, **kwargs)
        return decorated_function
