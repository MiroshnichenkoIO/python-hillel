from crud import create_user_with_posts, get_user_by_id, get_all_posts, update_user_email, delete_user


if __name__ == '__main__':
    print("1. Create User")
    user = create_user_with_posts(
        username="admin",
        email='admin@example.com',
        post_titles=["First post in 2026", "Lesson with SQLAlchemy"]
    )
    if user is None:
        print("Користувач admin уже є — видали його в pgAdmin і запусти знову")
        raise SystemExit(1)

    print("2. Get User")
    get_user_by_id(user.id)
    get_user_by_id(999)

    print("3. Get All Posts")
    get_all_posts()

    print("4. Update User")
    update_user_email(user.id, "admin@new.com")
    get_user_by_id(user.id)

    print("5. Delete User")
    delete_user(user.id)
    get_user_by_id(user.id)
