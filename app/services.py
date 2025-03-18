from app.models import db

class TaskService:
    """Service for task-related operations."""
    
    @staticmethod
    def get_all_tasks():
        """Get all tasks."""
        return list(db["tasks"].values())
    
    @staticmethod
    def get_task_by_id(task_id):
        """Get a task by ID."""
        return db["tasks"].get(task_id)
    
    @staticmethod
    def create_task(task_data):
        """Add a task to the database."""
        from app.models import Task
        
        task = Task(
            title=task_data["title"],
            description=task_data.get("description", ""),
            status=task_data.get("status", "pending")
        )
        
        db["tasks"][task.id] = task.to_dict()
        return task.to_dict()
    
    @staticmethod
    def update_task(task_id, task_data):
        """Update an existing task."""
        if task_id not in db["tasks"]:
            return None
        
        from app.models import Task
        
        # Create Task object from dictionary
        task_dict = db["tasks"][task_id]
        task = Task(
            title=task_dict["title"],
            description=task_dict["description"],
            status=task_dict["status"]
        )
        task.id = task_id
        task.created_at = task_dict["created_at"]
        
        # Update the task
        task.update(task_data)
        
        # Save back to database
        db["tasks"][task_id] = task.to_dict()
        return task.to_dict()
    
    @staticmethod
    def delete_task(task_id):
        """Delete a task."""
        if task_id not in db["tasks"]:
            return False
        
        del db["tasks"][task_id]
        return True
    
    @staticmethod
    def search_tasks_by_status(status):
        """Search tasks by status."""
        return [task for task in db["tasks"].values() if task["status"] == status]
    
    @staticmethod
    def get_stats():
        """Get task statistics."""
        total_tasks = len(db["tasks"])
        
        # Count tasks by status
        status_counts = {}
        for task in db["tasks"].values():
            status = task["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "total_tasks": total_tasks,
            "by_status": status_counts
        }