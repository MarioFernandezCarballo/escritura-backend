from flask import Blueprint, request, jsonify
from . import db
from .models import BlogPost, Subscriber, Comment
from .schemas import BlogPostSchema, SubscriberSchema, CommentSchema

api = Blueprint('api', __name__)

# Esquemas
blog_post_schema = BlogPostSchema()
blog_posts_schema = BlogPostSchema(many=True)
subscriber_schema = SubscriberSchema()
subscribers_schema = SubscriberSchema(many=True)
comment_schema = CommentSchema()
comments_schema = CommentSchema(many=True)


# Ruta diagnóstico


# Rutas para el blog
@api.route('/blog/posts', methods=['GET'])
def get_posts():
    posts = BlogPost.query.all()
    return jsonify(blog_posts_schema.dump(posts))

@api.route('/blog/posts', methods=['POST'])
def create_post():
    data = request.json
    new_post = BlogPost(
        title=data['title'],
        content=data['content'],
        tags=data.get('tags', ''),  # Tags son opcionales
        image_url=data.get('image_url', None)  # La imagen es opcional
    )
    db.session.add(new_post)
    db.session.commit()
    return blog_post_schema.jsonify(new_post)

# Rutas para mailing
@api.route('/mailing/subscribers', methods=['GET'])
def get_subscribers():
    subscribers = Subscriber.query.all()
    return jsonify(subscribers_schema.dump(subscribers))

@api.route('/mailing/subscribers', methods=['POST'])
def add_subscriber():
    data = request.json
    new_subscriber = Subscriber(email=data['email'])
    db.session.add(new_subscriber)
    db.session.commit()
    return subscriber_schema.jsonify(new_subscriber)

# Rutas para comentarios
@api.route('/blog/posts/<int:post_id>/comments', methods=['POST'])
def add_comment(post_id):
    data = request.json
    post = BlogPost.query.get_or_404(post_id)  # Verifica que el post exista
    new_comment = Comment(
        content=data['content'],
        author=data['author'],
        post_id=post.id
    )
    db.session.add(new_comment)
    db.session.commit()
    return comments_schema.jsonify(new_comment)