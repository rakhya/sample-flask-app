import uuid
from datetime import datetime

# In-memory database
db = {
    "tasks": {}
}

class Task:
    """Task model representing a task in the system."""
    
    def __init__(self, title, description="", status="pending"):
        """Initialize a new task."""
        self.id = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.status = status
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self):
        """Convert task to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    def update(self, data):
        """Update task with new data."""
        if "title" in data:
            self.title = data["title"]
        if "description" in data:
            self.description = data["description"]
        if "status" in data:
            self.status = data["status"]
        self.updated_at = datetime.now().isoformat()

# Add some sample data
def add_sample_data():
    """Add sample tasks to the database."""
    sample_tasks = [
        {"title": "Complete project proposal", "description": "Draft the initial proposal for the client", "status": "pending"},
        {"title": "Review code", "description": "Review pull requests from the team", "status": "in_progress"},
        {"title": "Update documentation", "description": "Update API documentation with new endpoints", "status": "completed"}
    ]
    
    for task_data in sample_tasks:
        task = Task(
            title=task_data["title"],
            description=task_data["description"],
            status=task_data["status"]
        )
        db["tasks"][task.id] = task.to_dict()