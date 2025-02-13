from flask import Blueprint, request, jsonify
import schedule
import time
import threading
import resend
from . import db
from datetime import datetime
from .models import BlogPost, Subscriber, Comment, Admin, Newsletter
from .schemas import BlogPostCreate, BlogPost as BlogPostSchema
from .schemas import SubscriberCreate, Subscriber as SubscriberSchema
from .schemas import CommentCreate, Comment as CommentSchema
from .schemas import AdminLogin, TokenResponse, NewsletterCreate, Newsletter as NewsletterSchema
from .auth import create_access_token, admin_required
import os

api = Blueprint('api', __name__)

# Configuración de Resend
resend.api_key = 're_2X64sqGS_6Zdn8rTiStRRWCBt76gPWr21'

@api.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "ok",
        "message": "API is running"
    }), 200

# Rutas para el blog
@api.route('/blog/posts', methods=['GET'])
def get_posts():
    posts = BlogPost.query.all()
    return jsonify([BlogPostSchema.model_validate(post).model_dump() for post in posts])

@api.route('/blog/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    return jsonify(BlogPostSchema.model_validate(post).model_dump())

# Authentication route
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

# Newsletter routes
@api.route('/newsletters', methods=['GET'])
@admin_required
def get_newsletters():
    newsletters = Newsletter.query.all()
    return jsonify([NewsletterSchema.model_validate(n).model_dump() for n in newsletters])

@api.route('/newsletters', methods=['POST'])
@admin_required
def create_newsletter():
    newsletter_data = NewsletterCreate.model_validate(request.json)
    new_newsletter = Newsletter(
        subject=newsletter_data.subject,
        content=newsletter_data.content,
        scheduled_for=newsletter_data.scheduled_for,
        status='scheduled'
    )
    db.session.add(new_newsletter)
    db.session.commit()
    return jsonify(NewsletterSchema.model_validate(new_newsletter).model_dump())

@api.route('/newsletters/<int:newsletter_id>', methods=['DELETE'])
@admin_required
def delete_newsletter(newsletter_id):
    newsletter = Newsletter.query.get_or_404(newsletter_id)
    db.session.delete(newsletter)
    db.session.commit()
    return '', 204

@api.route('/newsletters/<int:newsletter_id>/send', methods=['POST'])
@admin_required
def send_newsletter_now(newsletter_id):
    newsletter = Newsletter.query.get_or_404(newsletter_id)
    subscribers = Subscriber.query.all()
    
    for subscriber in subscribers:
        resend.Emails.send({
            "from": "Mario Carballo <newsletter@mariocarballo.com>",
            "to": subscriber.email,
            "subject": newsletter.subject,
            "html": newsletter.content
        })
    
    newsletter.status = 'sent'
    newsletter.sent_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({"message": "Newsletter sent successfully"})

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

def send_scheduled_newsletters():
    current_time = datetime.utcnow()
    scheduled_newsletters = Newsletter.query.filter_by(status='scheduled').all()
    
    for newsletter in scheduled_newsletters:
        if newsletter.scheduled_for <= current_time:
            subscribers = Subscriber.query.all()
            for subscriber in subscribers:
                resend.Emails.send({
                    "from": "Mario Carballo <newsletter@mariocarballo.com>",
                    "to": subscriber.email,
                    "subject": newsletter.subject,
                    "html": newsletter.content
                })
            
            newsletter.status = 'sent'
            newsletter.sent_at = current_time
            db.session.commit()

def run_scheduler():
    schedule.every(1).minutes.do(send_scheduled_newsletters)
    while True:
        schedule.run_pending()
        time.sleep(1)

threading.Thread(target=run_scheduler).start()

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
