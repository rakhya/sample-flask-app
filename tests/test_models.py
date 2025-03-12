Here is a valid Python test file using pytest to test the Flask application's models.py:

```python
import pytest
from uuid import UUID
from datetime import datetime

@pytest.fixture
def db():
    db = {"tasks": {}}
    return db

class Task:
    def test Initialization(self):
        task = Task("Test title", "test description", "pending")
        assert task.id is not None
        assert isinstance(task.id, str)
    
    def test_to_dict(self):
        task = Task("Test title", "test description", "pending")
        task.to_dict()
        assert type(task.to_dict()) is dict
    
    def test_update_title(self, db, Task):
        original_title = "Original Title"
        new_title = "New Title"
        task = Task(original_title)
        task.update({"title": new_title})
        assert task.title == new_title

    def test_update_all_fields(self, db, Task):
        original_title = "Original Title"
        new_title = "New Title"
        updated_date = datetime.now().isoformat()
        task = Task(original_title)
        task.update({
            "title": new_title,
            "description": "test description",
            "status": "pending",
            "created_at": updated_date
        })
        assert task.title == new_title
        assert task.description == "test description"
        assert task.status == "pending"
    
    def test_add_sample_data(self, db, Task):
        add_sample_data()
        tasks = list(db["tasks"].values())
        for task in tasks:
            assert isinstance(task['id'], UUID)
            assert task.get('created_at') is not None
```