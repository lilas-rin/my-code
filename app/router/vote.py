from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models, schemas, oauth2
from app.database import get_db

router = APIRouter(
    prefix="/vote",
    tags=["Vote"]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(
        vote: schemas.Vote,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(oauth2.get_current_user)
):
    # 查询当前用户是否已经给该帖子投过票
    vote_query = db.query(models.Vote).filter(
        models.Vote.post_id == vote.post_id,
        models.Vote.user_id == current_user.id
    )

    found_vote = vote_query.first()

    # 点赞
    if vote.dir == 1:

        if found_vote:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You have already voted on this post"
            )

        new_vote = models.Vote(
            post_id=vote.post_id,
            user_id=current_user.id
        )

        db.add(new_vote)
        db.commit()

        return {"message": "Successfully added vote"}

    # 取消点赞
    else:

        if not found_vote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vote does not exist"
            )

        vote_query.delete(synchronize_session=False)
        db.commit()

        return {"message": "Successfully deleted vote"}