from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, func, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Posts(Base):
    __tablename__ = "Posts"

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, server_default="TRUE")

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # 外键
    owner_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    # ORM关系
    owner = relationship("User")

    votes = relationship(
        "Vote",
        cascade="all, delete",
        passive_deletes=True
    )


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False, index=True)

    email = Column(String, unique=True, nullable=False, index=True)

    password = Column(String, nullable=False)

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # ORM关系
    posts = relationship(
        "Posts",
        back_populates="owner",
        cascade="all, delete"
    )

    votes = relationship(
        "Vote",
        cascade="all, delete",
        passive_deletes=True
    )


class Vote(Base):
    __tablename__ = "votes"

    post_id = Column(
        Integer,
        ForeignKey("Posts.id", ondelete="CASCADE"),
        primary_key=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )

    post = relationship("Posts")
    user = relationship("User")
