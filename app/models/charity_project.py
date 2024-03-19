from sqlalchemy import Column, String, Text

from .base import BaseCharityProject


class CharityProject(BaseCharityProject):
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=False)
