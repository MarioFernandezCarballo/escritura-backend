from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields
from .models import BlogPost, Subscriber, Comment


class SubscriberSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Subscriber
        load_instance = True

class CommentSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Comment
        load_instance = True

class BlogPostSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = BlogPost
        load_instance = True

    comments = fields.Nested(CommentSchema, many=True)  # Incluye los comentarios en el esquema