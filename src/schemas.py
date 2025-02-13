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
    tags: Optional[str] = None
    image_url: Optional[str] = None

class BlogPostCreate(BlogPostBase):
    pass

class BlogPost(BlogPostBase):
    id: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    comments: List[Comment] = []

    class Config:
        from_attributes = True
