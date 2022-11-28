from enum import Enum
from functools import wraps

from core.db import db_session, session


class Propagation(Enum):
    REQUIRED = "required"
    REQUIRED_NEW = "required_new"


class Transactional:
    def __call__(self, function):
        @wraps(function)
        async def decorator(*args, **kwargs):
            try:
                result = await function(*args, **kwargs)
                await db_session.commit()
            except Exception as e:
                await db_session.rollback()
                raise e

            return result

        return decorator
