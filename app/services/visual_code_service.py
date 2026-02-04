from sqlalchemy.orm import Session
from app.models import models

class VisualCodeService:
    def __init__(self, db: Session):
        self.db = db

    def generate_code_graph(self, binary_id: int):
        """
        Generates nodes and edges for a binary's call graph.
        """
        functions = self.db.query(models.Function).filter(models.Function.binary_id == binary_id).all()
        func_ids = [f.id for f in functions]

        calls = self.db.query(models.FunctionCall).filter(models.FunctionCall.caller_id.in_(func_ids)).all()

        nodes = []
        edges = []

        # Position nodes in a simple grid for now (or circle)
        import math
        radius = 400
        angle_step = (2 * math.pi) / max(1, len(functions))

        for i, func in enumerate(functions):
            nodes.append({
                "id": f"code_{func.id}",
                "type": "code_function",
                "reference_id": func.id,
                "pos_x": 500 + radius * math.cos(i * angle_step),
                "pos_y": 500 + radius * math.sin(i * angle_step),
                "data": {
                    "label": func.name,
                    "danger_score": func.danger_score,
                    "vuln_type": func.vuln_type
                }
            })

        for call in calls:
            target_id = f"code_{call.callee_id}" if call.callee_id else f"ext_{call.callee_name}"

            # If target doesn't exist in internal nodes, add it as an external node if not already added
            if not call.callee_id:
                if not any(n["id"] == target_id for n in nodes):
                    nodes.append({
                        "id": target_id,
                        "type": "code_external",
                        "pos_x": 1000,
                        "pos_y": 500 + (len(nodes) % 10) * 50,
                        "data": {"label": call.callee_name}
                    })

            edges.append({
                "source": f"code_{call.caller_id}",
                "target": target_id,
                "type": "calls",
                "data": {"offset": call.offset}
            })

        return {"nodes": nodes, "edges": edges}

    def touch_node(self, node_id: str):
        """Returns details about a code node."""
        if node_id.startswith("code_"):
            func_id = int(node_id.split("_")[1])
            func = self.db.query(models.Function).filter(models.Function.id == func_id).first()
            if func:
                return {
                    "name": func.name,
                    "assembly": func.assembly_snippet,
                    "python": func.python_like,
                    "danger": func.danger_score
                }
        return None
