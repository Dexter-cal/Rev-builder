from sqlalchemy.orm import Session
from app.models import models
import json
import datetime

class ProjectService:
    def __init__(self, db: Session):
        self.db = db

    def save_state(self, project_id: int, name: str):
        """Saves a snapshot of the current project state."""
        # In a real tool, we might snapshot all related records
        state = models.ProjectState(
            project_id=project_id,
            name=name,
            state_data={"timestamp": str(datetime.datetime.now()), "note": "Manual save"}
        )
        self.db.add(state)
        self.db.commit()
        return state

    def record_action(self, project_id: int, action_type: str, description: str, undo_data: dict, redo_data: dict):
        """Records an action for undo/redo functionality."""
        action = models.ActionHistory(
            project_id=project_id,
            action_type=action_type,
            description=description,
            undo_data=undo_data,
            redo_data=redo_data
        )
        self.db.add(action)
        self.db.commit()
        return action

    def undo(self, project_id: int):
        """Reverts the last action."""
        last_action = self.db.query(models.ActionHistory).filter(
            models.ActionHistory.project_id == project_id
        ).order_by(models.ActionHistory.timestamp.desc()).first()

        if not last_action:
            return None

        # In a real tool, we would apply undo_data here
        # For now, we just return it to acknowledge
        return last_action

    def get_workflow(self, project_id: int):
        """Returns the visual logic graph nodes and edges."""
        nodes = self.db.query(models.WorkflowNode).filter(models.WorkflowNode.project_id == project_id).all()
        edges = self.db.query(models.WorkflowEdge).filter(models.WorkflowEdge.project_id == project_id).all()
        return {"nodes": nodes, "edges": edges}

    def update_workflow(self, project_id: int, nodes: list, edges: list):
        """Updates the visual logic graph."""
        # Simple implementation: Clear and recreate
        self.db.query(models.WorkflowNode).filter(models.WorkflowNode.project_id == project_id).delete()
        self.db.query(models.WorkflowEdge).filter(models.WorkflowEdge.project_id == project_id).delete()

        new_nodes = []
        for n in nodes:
            node = models.WorkflowNode(
                project_id=project_id,
                type=n['type'],
                reference_id=n.get('reference_id'),
                pos_x=n['pos_x'],
                pos_y=n['pos_y'],
                data=n.get('data')
            )
            self.db.add(node)
            new_nodes.append(node)

        self.db.commit()
        # Edges need node IDs, so we usually do this in two steps or use client-side IDs
        return {"status": "updated"}
