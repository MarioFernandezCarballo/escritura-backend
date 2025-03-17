from flask import Blueprint, request, jsonify
from .utils import Contact, Post, Auth, Newsletter, Subscriber
import os

api = Blueprint('api', __name__)

### Contacto ###
################
@api.route('/contact', methods=['POST'])
def handle_contact():
    return Contact.handleContact(request)
    
#### Blog ###
#############
@api.route('/blog/posts', methods=['GET'])
def get_posts():
    return Post.getAll()

@api.route('/blog/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    return Post.get(post_id)

@api.route('/blog/posts', methods=['POST'])
@Auth.adminRequired
def create_post():
    return Post.post(request)

@api.route('/blog/posts/<int:post_id>/comments', methods=['POST'])
def add_comment(post_id):
    return Post.addComment(post_id, request)

### Auth ###
############
@api.route('/auth/login', methods=['POST'])
def login():
    return Auth.login(request)

### Newsletter ###
##################
@api.route('/newsletters', methods=['GET'])
@Auth.adminRequired
def get_newsletters():
    return Newsletter.get()

@api.route('/newsletters', methods=['POST'])
@Auth.adminRequired
def create_newsletter():
    return Newsletter.post(request)

@api.route('/newsletters/<int:newsletter_id>', methods=['DELETE'])
@Auth.adminRequired
def delete_newsletter(newsletter_id):
    return Newsletter.delete(newsletter_id)

@api.route('/newsletters/<int:newsletter_id>/send', methods=['POST'])
@Auth.adminRequired
def send_newsletter_now(newsletter_id):
    return Newsletter.send(newsletter_id)

### Subscribers ###
###################
@api.route('/subscriber', methods=['GET'])
@Auth.adminRequired
def get_subscribers():
    return Subscriber.get()

@api.route('/subscriber', methods=['POST'])
def add_subscriber():
    return Subscriber.add(request)

@api.route('/subscriber/<string:sub_id>', methods=['DELETE'])
def delete_subscriber(sub_id):
    return Subscriber.delete(sub_id)

@api.route('/subscriber/email/<string:sub_email>', methods=['DELETE'])
def delete_subscriber_by_email(sub_email):
    return Subscriber.deleteByEmail(sub_email)

### CI / CD - System ###
########################
@api.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "ok",
        "message": "API is running"
    }), 200

@api.route('/update_server', methods=['POST'])
def webhook():
    if request.method == 'POST':
        os.system('bash /home/MarioCarballo/mysite/command-pull-event.sh')
        return 'Updated PythonAnywhere successfully', 200
    else:
        return 'Wrong event type', 400
