from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from flask_login import LoginManager

# Initialize the LoginManager
login_manager = LoginManager()


# Initialize the SQLAlchemy engine and session factory
db_url = "mysql+mysqlconnector://root:AjithRavi!25@localhost/healthyfit" 
engine = create_engine(db_url, echo=True)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

# Define the user loader here to avoid circular imports
@login_manager.user_loader
def load_user(user_id):
    from .models import User
    with Session() as session:
        return session.get(User, int(user_id))
