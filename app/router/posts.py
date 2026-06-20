from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from app import models, oauth2, schemas
from app.database import get_db


router = APIRouter(
    prefix="/posts",
    tags=["Posts"],
    dependencies=[Depends(oauth2.get_current_user)],
)


def _post_with_votes(post: models.Posts, votes: int) -> schemas.PostWithVotes:
    post_data = schemas.Post.model_validate(post).model_dump()
    return schemas.PostWithVotes(**post_data, votes=votes)


@router.get("/", response_model=list[schemas.PostWithVotes])
def get_posts(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = "",
):
    posts = (
        db.query(
            models.Posts,
            func.count(models.Vote.post_id).label("votes"),
        )
        .outerjoin(models.Vote, models.Vote.post_id == models.Posts.id)
        .filter(
            models.Posts.owner_id == current_user.id,
            models.Posts.title.contains(search),
        )
        .group_by(models.Posts.id)
        .limit(limit)
        .offset(skip)
        .all()
    )

    return [
        _post_with_votes(post, votes)
        for post, votes in posts
    ]


@router.get("/{id}", response_model=schemas.PostWithVotes)
def get_post(id: int, db: Session = Depends(get_db)):
    post = (
        db.query(
            models.Posts,
            func.count(models.Vote.post_id).label("votes"),
        )
        .outerjoin(models.Vote, models.Vote.post_id == models.Posts.id)
        .filter(models.Posts.id == id)
        .group_by(models.Posts.id)
        .first()
    )

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} was not found",
        )

    post_data, votes = post
    return _post_with_votes(post_data, votes)


@router.post("/")
def create_post(
    post: schemas.CreatedPosts,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    new_post = models.Posts(
        **post.model_dump(),
        owner_id=current_user.id,
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    post_query = db.query(models.Posts).filter(
        models.Posts.id == id
    )

    post = post_query.first()

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} was not found",
        )

    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action",
        )

    post_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.Post)
def update_post(
    id: int,
    post: schemas.CreatedPosts,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    post_query = db.query(models.Posts).filter(
        models.Posts.id == id
    )

    db_post = post_query.first()

    if db_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} was not found",
        )

    if db_post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action",
        )

    post_query.update(
        post.model_dump(),
        synchronize_session=False,
    )

    db.commit()

    return post_query.first()
