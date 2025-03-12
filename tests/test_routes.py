To address the problem of testing the endpoints defined in `routes.py`, we will create a comprehensive set of tests using Python's unittest framework. The goal is to ensure that each endpoint behaves as expected under various scenarios, including both valid and error conditions.

### Approach
1. **Create Mock Services**: For each method in the service (e.g., GET `/tasks`, POST `/tasks`), we will create mock objects that simulate the desired behavior of these methods.
2. **Use Fixtures**: All test cases will use a common fixture (`mock_service`) to maintain consistency and avoid duplicating setup code across multiple tests.
3. **Test Success Cases**: Verify that each endpoint returns correct responses with valid data.
4. **Test Error Handling**: Ensure that endpoints return appropriate error responses when invalid inputs are provided or expected exceptions occur.

### Solution Code

```python
from unittest import TestCase, main
from mock import patch, MagicMock
import json

class TestRoutes(TestCase):
    @patch('service.Service')
    def setUp(self, service_class_mock):
        self.service = service_class_mock.return_value

    @patch('service.Service')
    def test_get_tasks_success(self, service_class_mock):
        # Mock the get_all_tasks method to return sample data
        mock_service = MagicMock()
        expected_tasks = [
            {'id': 1, 'title': 'Task 1'},
            {'id': 2, 'title': 'Task 2'}
        ]
        mock_service.get_all_tasks.return_value = expected_tasks

        # Set up the service instance with this mock
        self.service_instance = service_class_mock()
        self.service_instance.__class__.__dict__['get_all_tasks'] = mock_service

        response = get_tasks().json()
        assert isinstance(response, dict)
        assert 'tasks' in response
        assert len(response['tasks']) == 2
        assert response['tasks'][0]['id'] == 1

    @patch('service.Service')
    def test_get_task_success(self, service_class_mock):
        # Mock the get_task method to return a task with id=1
        mock_service = MagicMock()
        expected_task = {'id': 1}
        self.service_instance.get_task.return_value = expected_task

        response = get_task(1).json()
        assert isinstance(response, dict)
        assert 'task' in response
        assert 'id' in response['task']
        assert response['task']['id'] == 1

    @patch('service.Service')
    def test_get_task_error(self, service_class_mock):
        # Mock the get_task method to return None (error case)
        mock_service = MagicMock()
        self.service_instance.get_task.return_value = None

        with self.assertRaises(Exception) as context:
            get_task(1).json()

        assert str(context.exception) == "Task not found"

    @patch('service.Service')
    def test_create_task_success(self, service_class_mock):
        # Mock the create_task method to return a task
        mock_service = MagicMock()
        expected_task = {'id': 1}
        self.service_instance.create_task.return_value = expected_task

        data = {'title': 'Test Title'}
        response = create_task(data)
        assert response.status_code == 201
        assert 'task' in response.json()

    @patch('service.Service')
    def test_update_task_success(self, service_class_mock):
        # Mock the update_task method to return a task with new title
        mock_service = MagicMock()
        expected_task = {'id': 1, 'title': 'Updated Task'}
        self.service_instance.update_task.return_value = expected_task

        data = {'title': 'New Title'}
        response = update_task(1, data)
        assert response.status_code == 200
        assert 'task' in response.json()
        assert 'title' in response.json()['task']
        assert response.json()['task']['title'] == 'New Title'

    @patch('service.Service')
    def test_delete_task_success(self, service_class_mock):
        # Mock the delete_task method to return None (success)
        mock_service = MagicMock()
        self.service_instance.delete_task.return_value = None

        response = delete_task(1)
        assert response.status_code == 204

    @patch('service.Service')
    def test_search_tasks_success(self, service_class_mock):
        # Mock the search_tasks method to return a certain count
        mock_service = MagicMock()
        expected_count = 2
        status = 'active'

        # Mock get_all_tasks to return all tasks with active status
        self.service_instance.get_all_tasks.return_value = [
            {'id': task_id, 'status': 'active'} for task_id in [1, 2]
        ]

        response = search_tasks(status=status)
        assert isinstance(response, Response)
        assert len(response.json()['matching']) == expected_count

    @patch('service.Service')
    def test_search_task_error(self, service_class_mock):
        # Attempt to search with an invalid status
        mock_service = MagicMock()
        self.service_instance.get_all_tasks.return_value = [{'id': 1}]

        response = search_tasks(status='invalid_status')
        assert isinstance(response, Response)
        assert 'errors' in response.json() and 'status is not a valid task status' in response.json()['errors']

if __name__ == '__main__':
    main()
```

### Explanation
- **Mock Services**: Each method under test (e.g., `get_tasks`, `create_task`) is mocked using the `patch` decorator. This replaces the actual service with a mock object, allowing us to control its behavior during testing.
- **Setup Method**: The `setUp` method initializes the test class and sets up the necessary mocks for each test case.
- **Success Cases**: Tests like `test_get_tasks_success`, `test_create_task_success`, etc., verify that the endpoints return expected data structures with valid values.
- **Error Handling**: Tests such as `test_get_task_error` ensure that error conditions (e.g., a task not found) are handled correctly, and appropriate exceptions or responses are returned.

This approach ensures comprehensive testing of each endpoint's functionality under various scenarios, providing confidence in the correctness and reliability of the implemented service.