Here is the *SEARCH/REPLACE* block containing the test file:

```python

import pytest
from app.models.task import Task
from app.services.task_service import TaskService
from app.routes import api_bp
import json
import requests

@pytest.fixture
def task_service():
    return TaskService()

@pytest.mark.usefixtures("task_service")
class TestTaskApi:
    def test_get_tasks(self):
        """Test GET /tasks endpoint."""
        # Prepare sample data
        tasks = [
            {"title": "Task 1", "status": "active"},
            {"title": "Task 2", "status": "inactive"},
        ]
        
        # Simulate getting all tasks without any filters
        response = requests.get(api_bp.url_prefix + '/tasks')
        assert response.status_code == 200
        response_data = response.json()
        assert isinstance(response_data["tasks"], list)
        assert len(response_data["tasks"]) >= 1
        
        # Test with empty request should return all tasks
        task_service.get_all_tasks.return_value = []
        response = requests.get(api_bp.url_prefix + '/tasks')
        response_data = response.json()
        assert "tasks" in response_data and isinstance(response_data["tasks"], list)
        
        # Test invalid JSON input returns error
        response = requests.post(api_bp.url_prefix + '/tasks', json="invalid")
        response.raise_for_status()
        
    def test_get_task_by_id(self, task_service):
        """Test GET /tasks/<task_id> endpoint."""
        sample_task = Task(
            id=1,
            title="Sample Task",
            description="Sample Description",
            status="active"
        )
        task_service.get_task_by_id.return_value = sample_task
        
        # Test with valid ID
        response = requests.get(api_bp.url_prefix + '/tasks/1')
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["id"] == 1
        assert "title" in response_data and response_data["title"] == "Sample Task"
        
        # Test with invalid ID returns 404
        response = requests.get(api_bp.url_prefix + '/tasks/99')
        assert response.status_code == 404
        
    def test_create_task(self, task_service):
        """Test POST /tasks endpoint."""
        # Prepare sample data with required fields
        data = {
            "title": "New Task",
            "description": "Sample Description"
        }
        
        # Test valid data
        response = requests.post(api_bp.url_prefix + '/tasks', json=data)
        assert response.status_code == 201
        
        task_service.create_task.assert_called_once_with(data)
        
        # Test missing title
        response = requests.post(api_bp.url_prefix + '/tasks', json={"description": "test"})
        assert response.status_code == 400
        assert "Title is required" in str(response.json())
        
    def test_update_task(self, task_service):
        """Test PUT /tasks/<task_id> endpoint."""
        sample_task = Task(
            id=1,
            title="Sample Task",
            description="Sample Description",
            status="active"
        )
        task_service.get_task_by_id.return_value = sample_task
        
        # Test updating task with valid data
        new_data = {
            "title": "Updated Task",
            "description": "New Description"
        }
        
        response = requests.put(api_bp.url_prefix + '/tasks/1', json=new_data)
        assert response.status_code == 200
        
        task_service.update_task.assert_called_once_with(1, new_data)
        
        # Test invalid data
        response = requests.put(api_bp.url_prefix + '/tasks/1', json={"invalid": "data"})
        assert response.status_code == 400
        assert "No data provided" in str(response.json())
        
    def test_delete_task(self, task_service):
        """Test DELETE /tasks/<task_id> endpoint."""
        sample_task = Task(
            id=1,
            title="Sample Task",
            description="Sample Description"
        )
        task_service.delete_task.return_value = True
        
        # Test deleting task with valid ID
        response = requests.delete(api_bp.url_prefix + '/tasks/1')
        assert response.status_code == 200
        
        # Test invalid ID returns 404
        response = requests.delete(api_bp.url_prefix + '/tasks/99')
        assert response.status_code == 404
        
    def test_get_task_status(self, task_service):
        """Test GET /tasks/<task_id> with status endpoint."""
        sample_task = Task(
            id=1,
            title="Sample Task",
            description="Sample Description",
            status="active"
        )
        
        # Test fetching task with active status
        response = requests.get(api_bp.url_prefix + '/tasks/1')
        assert response.status_code == 200
        response_data = response.json()
        assert "status" in response_data and response_data["status"] == "active"
        
        # Test changing status to inactive
        task_service.get_task_by_id.return_value.status = "inactive"
        response = requests.get(api_bp.url_prefix + '/tasks/1')
        response_data = response.json()
        assert "status" in response_data and response_data["status"] == "inactive"

@pytest.mark integration
def test_get_task_status_with_url_params(task_service):
    """Test GET /tasks/<task_id> with query params."""
    sample_task = Task(
        id=1,
        title="Sample Task",
        description="Sample Description",
        status="active"
    )
    
    response = requests.get(api_bp.url_prefix + '/tasks/1?status=inactive')
    assert response.status_code == 200
    response_data = response.json()
    assert "status" in response_data and response_data["status"] == "inactive"

@pytest.mark integration
def test_get_task_with_filter(task_service):
    """Test GET /tasks with status filter."""
    sample_tasks = [
        Task(id=1, title="Active", status="active"),
        Task(id=2, title="Inactive", status="inactive")
    ]
    
    task_service.get_all_tasks.return_value = sample_tasks
    
    response = requests.get(api_bp.url_prefix + '/tasks?status=active')
    assert response.status_code == 200
    response_data = response.json()
    assert "tasks" in response_data and all(task["status"] == "active" for task in response_data["tasks"])
 REPLACE
```

To run the tests, use these commands:

```bash
pytest app/tests/test_routes.py -v
```

Note: Make sure you have requests installed. If not:
```bash
pip install requests pytest
```