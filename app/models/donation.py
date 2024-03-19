from sqlalchemy import Column, ForeignKey, Integer, Text

from .base import BaseCharityProject


class Donation(BaseCharityProject):
    user_id = Column(Integer, ForeignKey('user.id'))
    comment = Column(Text, nullable=True)
