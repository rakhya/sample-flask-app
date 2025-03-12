from flask import Blueprint, request, jsonify
from app.services import TaskService

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/tasks', methods=['GET'])
def get_tasks():
    """Retrieve all tasks."""
    tasks = TaskService.get_all_tasks()
    return jsonify({"tasks": tasks, "count": len(tasks)})

@api_bp.route('/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    """Retrieve a specific task by ID."""
    task = TaskService.get_task_by_id(task_id)
    if task:
        return jsonify(task)
    return jsonify({"error": "Task not found"}), 404

@api_bp.route('/tasks', methods=['POST'])
def create_task():
    """Create a new task."""
    data = request.json
    
    # Validate required fields
    if not data or not data.get("title"):
        return jsonify({"error": "Title is required"}), 400
    
    task = TaskService.create_task(data)
    return jsonify(task), 201

@api_bp.route('/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    """Update an existing task."""
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    task = TaskService.update_task(task_id, data)
    if task:
        return jsonify(task)
    return jsonify({"error": "Task not found"}), 404

@api_bp.route('/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task."""
    success = TaskService.delete_task(task_id)
    if success:
        return jsonify({"message": "Task deleted successfully"}), 200
    return jsonify({"error": "Task not found"}), 404

@api_bp.route('/tasks/search', methods=['GET'])
def search_tasks():
    """Search tasks by status."""
    status = request.args.get('status')
    if not status:
        return jsonify({"error": "Status parameter is required"}), 400
    
    matching_tasks = TaskService.search_tasks_by_status(status)
    return jsonify({"tasks": matching_tasks, "count": len(matching_tasks)})

@api_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get statistics about tasks."""
    stats = TaskService.get_stats()
    return jsonify(stats)