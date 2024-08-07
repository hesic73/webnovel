import sys

from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError


from app.enums import UserType
from app import database
from app.database import engine

# Function to change the user_type of a user


def change_user_type(username: str, new_user_type: UserType):
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Query the user by username
        user = session.query(database.User).filter_by(
            username=username).first()

        if user:
            # Change the user_type
            user.user_type = new_user_type
            session.commit()
            print(
                f"User {username}'s type has been changed to {new_user_type.name}.")
        else:
            print(f"User {username} not found.")
    except IntegrityError as e:
        print(f"An error occurred: {e}")
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":

    assert len(sys.argv) == 2, "Please provide the username as an argument"
    username = sys.argv[1]
    # Example usage
    change_user_type(username=username, new_user_type=UserType.ADMIN)
