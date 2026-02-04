from sqlalchemy.orm import Session
from app.models import models
import datetime

class CollaborationService:
    def __init__(self, db: Session):
        self.db = db

    def add_comment(self, node_id: int, user_id: int, content: str):
        comment = models.NodeComment(
            node_id=node_id,
            user_id=user_id,
            content=content
        )
        self.db.add(comment)
        self.db.commit()
        return comment

    def get_comments(self, node_id: int):
        return self.db.query(models.NodeComment).filter(models.NodeComment.node_id == node_id).all()

    def get_online_collaborators(self, project_id: int):
        """Returns list of online analysts for the project."""
        # Simulation: seeded collaborators
        collabs = self.db.query(models.ProjectCollaborator).filter(
            models.ProjectCollaborator.project_id == project_id
        ).all()

        if not collabs:
            # Seed some dummy collaborators if none exist
            dummy_users = [
                {"user_id": 1, "role": "analyst", "status": "online"},
                {"user_id": 2, "role": "viewer", "status": "offline"}
            ]
            for du in dummy_users:
                c = models.ProjectCollaborator(project_id=project_id, **du)
                self.db.add(c)
            self.db.commit()
            collabs = self.db.query(models.ProjectCollaborator).filter(
                models.ProjectCollaborator.project_id == project_id
            ).all()

        return collabs

    def commit_changes(self, project_id: int, user_id: int, message: str, diff_data: dict):
        commit = models.ProjectCommit(
            project_id=project_id,
            user_id=user_id,
            message=message,
            diff_data=diff_data
        )
        self.db.add(commit)
        self.db.commit()
        return commit
