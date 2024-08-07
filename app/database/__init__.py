from .base import Base


from .models import *


from .session import engine

Base.metadata.create_all(bind=engine)
