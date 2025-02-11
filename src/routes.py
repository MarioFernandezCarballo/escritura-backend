from flask import Blueprint, request, jsonify
from . import db
from .models import BlogPost, Subscriber, Comment, Admin
from .schemas import BlogPostCreate, BlogPost as BlogPostSchema
from .schemas import SubscriberCreate, Subscriber as SubscriberSchema
from .schemas import CommentCreate, Comment as CommentSchema
from .schemas import AdminLogin, AdminCreate, TokenResponse
from .auth import create_access_token, admin_required
import os

api = Blueprint('api', __name__)

@api.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "ok Mackey",
        "message": "API is running"
    }), 200

# Rutas para el blog
@api.route('/blog/posts', methods=['GET'])
def get_posts():
    posts = BlogPost.query.all()
    return jsonify([BlogPostSchema.model_validate(post).model_dump() for post in posts])

# Authentication routes
@api.route('/auth/register', methods=['POST'])
def register_admin():
    admin_data = AdminCreate.model_validate(request.json)
    if Admin.query.filter_by(username=admin_data.username).first():
        return jsonify({"error": "Username already registered"}), 400
    
    new_admin = Admin(username=admin_data.username)
    new_admin.set_password(admin_data.password)
    db.session.add(new_admin)
    db.session.commit()
    
    access_token = create_access_token({"sub": new_admin.username})
    return jsonify(TokenResponse(access_token=access_token).model_dump())

@api.route('/auth/login', methods=['POST'])
def login():
    login_data = AdminLogin.model_validate(request.json)
    admin = Admin.query.filter_by(username=login_data.username).first()
    
    if not admin or not admin.check_password(login_data.password):
        return jsonify({"error": "Invalid credentials"}), 401
    
    access_token = create_access_token({"sub": admin.username})
    return jsonify(TokenResponse(access_token=access_token).model_dump())

@api.route('/blog/posts', methods=['POST'])
@admin_required
def create_post():
    post_data = BlogPostCreate.model_validate(request.json)
    new_post = BlogPost(
        title=post_data.title,
        content=post_data.content,
        tags=post_data.tags,
        image_url=post_data.image_url
    )
    db.session.add(new_post)
    db.session.commit()
    return jsonify(BlogPostSchema.model_validate(new_post).model_dump())

# Rutas para mailing
@api.route('/mailing/subscribers', methods=['GET'])
def get_subscribers():
    subscribers = Subscriber.query.all()
    return jsonify([SubscriberSchema.model_validate(sub).model_dump() for sub in subscribers])

@api.route('/mailing/subscribers', methods=['POST'])
def add_subscriber():
    subscriber_data = SubscriberCreate.model_validate(request.json)
    new_subscriber = Subscriber(email=subscriber_data.email)
    db.session.add(new_subscriber)
    db.session.commit()
    return jsonify(SubscriberSchema.model_validate(new_subscriber).model_dump())

# Rutas para comentarios
@api.route('/blog/posts/<int:post_id>/comments', methods=['POST'])
def add_comment(post_id):
    comment_data = CommentCreate.model_validate(request.json)
    post = BlogPost.query.get_or_404(post_id)  # Verifica que el post exista
    new_comment = Comment(
        content=comment_data.content,
        author=comment_data.author,
        post_id=post.id
    )
    db.session.add(new_comment)
    db.session.commit()
    return jsonify(CommentSchema.model_validate(new_comment).model_dump())


# Rutas CICD
@api.route('/update_server', methods=['POST'])
def webhook():
    if request.method == 'POST':
        os.system('bash /home/MarioCarballo/mysite/command-pull-event.sh')
        return 'Updated PythonAnywhere successfully', 200
    else:
        return 'Wrong event type', 400
