from datetime import datetime

from sqlalchemy import Column, DateTime, Boolean


class Removable(object):
    created_at = Column(DateTime(), default=datetime.now, nullable=False)
    is_enabled = Column(Boolean, default=True, nullable=False)
    removed_at = Column(DateTime())

    def remove(self):
        self.is_enabled = False
        self.removed_at = datetime.now()

    @property
    def created_at_str(self):
        return self.created_at.strftime("%Y-%m-%d %H:%M:%S")