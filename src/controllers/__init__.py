import os
from sqlalchemy import create_engine


DB_NAME = os.environ.get('DB_NAME')
engine = create_engine("sqlite:///{}".format(DB_NAME))

from .user import *
from .reading import *
from .api import *
from .speaking import *
