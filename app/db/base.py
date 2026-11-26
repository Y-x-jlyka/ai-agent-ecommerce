from sqlalchemy.orm import DeclarativeBase


# SQLAlchemy 声明式基类，所有数据表模型都继承它
class Base(DeclarativeBase):
    """
    所有数据库模型的统一基类 (Base Class)。

    作用：
        1. 继承自 SQLAlchemy 2.0 的 DeclarativeBase。
        2. 后续定义的所有具体数据表（如 User, Order）都需要继承此类。
        3. 它负责将 Python 类与数据库表建立映射关系，并提供元数据 (metadata)。
    """
    pass