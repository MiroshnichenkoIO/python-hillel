from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from database import SessionLocal
from models import User, Post


def create_user_with_posts(username: str, email: str, post_titles: list[str]):
    with SessionLocal() as session:
        try:
            user = User(username=username, email=email)
            for title in post_titles:
                user.posts.append(Post(title=title, content=f"Зміст для {title}"))

            session.add(user)
            session.commit()
            print(f"Created new user with id: {user.id}")
            return user

        except Exception as ex:
            session.rollback()
            print(f"Error: {ex}")
            return None


def get_user_by_id(user_id: int):
    with SessionLocal() as session:
        user = session.get(User, user_id)
        if user is None:
            print(f"User {user_id} not found")
        else:
            print(f"Found: {user}")
        return user


def get_all_users():
    with SessionLocal() as session:
        stmt = select(User).order_by(User.id)
        return session.scalars(stmt).all()


def get_all_posts():
    with SessionLocal() as session:
        stmt = select(Post).order_by(Post.id)
        posts = session.scalars(stmt).all()
        for post in posts:
            print(f"Post: {post.title} | Author ID: {post.user_id}")
        return posts


def update_user_email(user_id: int, new_email: str):
    with SessionLocal() as session:
        stmt = select(User).where(User.id == user_id)
        user = session.scalar(stmt)
        if user:
            user.email = new_email
            session.commit()
            print(f"Updated user {user.id}: email = {user.email}")
        else:
            print("User is not found")
        return user


def delete_user(user_id: int):
    with SessionLocal() as session:
        user = session.get(User, user_id)
        if user:
            session.delete(user)
            session.commit()
            print(f"Deleted user {user_id} with all posts")
            return True
        print("User is not found")
        return False
