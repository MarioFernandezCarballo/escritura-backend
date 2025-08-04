from pydantic import BaseModel, EmailStr, Field, constr
from typing import List, Optional
from datetime import datetime

class NewsletterBase(BaseModel):
    subject: str
    content: str
    scheduled_for: datetime

class NewsletterCreate(NewsletterBase):
    pass

class Newsletter(NewsletterBase):
    id: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = None
    status: str = 'scheduled'

    class Config:
        from_attributes = True

class AdminLogin(BaseModel):
    username: constr(min_length=1)
    password: constr(min_length=6)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class CommentBase(BaseModel):
    content: str
    author: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: int
    post_id: int

    class Config:
        from_attributes = True

class SubscriberBase(BaseModel):
    email: EmailStr

class SubscriberCreate(SubscriberBase):
    pass

class Subscriber(SubscriberBase):
    id: int
    subscribed_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True

class BlogPostBase(BaseModel):
    title: str
    content: str
    tags: list[str]
    image_url: str
    is_secret: bool = False

class BlogPostCreate(BlogPostBase):
    pass

class BlogPost(BlogPostBase):
    id: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    secret_token: Optional[str] = None
    comments: List[Comment] = []

    class Config:
        from_attributes = True
    
    # Custom validator to convert tags from string to list
    @classmethod
    def model_validate(cls, obj, *args, **kwargs):
        # If obj is a database model instance
        if hasattr(obj, '__table__'):
            # Create a dictionary from the model
            data = {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
            # Convert tags from string to list if it's a string
            if isinstance(data.get('tags'), str):
                data['tags'] = data['tags'].split(',') if data['tags'] else []
            # Add relationships
            if hasattr(obj, 'comments'):
                data['comments'] = obj.comments
            return super().model_validate(data, *args, **kwargs)
        return super().model_validate(obj, *args, **kwargs)
