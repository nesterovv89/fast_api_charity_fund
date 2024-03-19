from sqlalchemy import Column, String, Text

from .base import BaseCharityProject
from app.core import constants as c


class CharityProject(BaseCharityProject):
    name = Column(String(c.MAX_STR_LENGTH), unique=True, nullable=False)
    description = Column(Text, nullable=False)
