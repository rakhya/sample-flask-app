import os
import subprocess
import ast
import re
from pathlib import Path
import openai

# Initialize the OpenAI client
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def get_changed_files():
    """Get list of changed Python files in the pull request."""
    # For GitHub Actions
    if os.environ.get("GITHUB_BASE_REF"):
        cmd = f"git diff --name-only origin/{os.environ.get('GITHUB_BASE_REF')}...HEAD | grep '\.py$'"
    else:
        # For local development - use last commit
        cmd = "git diff --name-only HEAD~1 HEAD | grep '\\.py$'"
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    changed_files = result.stdout.strip().split('\n')
    return [f for f in changed_files if f and f.startswith('app/')]

def extract_function_info(file_path):
    """Extract information about functions and classes in a Python file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    try:
        tree = ast.parse(content)
        functions = []
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                function_info = {
                    'name': node.name,
                    'args': [arg.arg for arg in node.args.args if arg.arg != 'self'],
                    'docstring': ast.get_docstring(node) or "",
                    'code': content[node.lineno-1:node.end_lineno]
                }
                functions.append(function_info)
            elif isinstance(node, ast.ClassDef):
                class_methods = []
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        method_info = {
                            'name': item.name,
                            'args': [arg.arg for arg in item.args.args if arg.arg != 'self'],
                            'docstring': ast.get_docstring(item) or "",
                            'code': content[item.lineno-1:item.end_lineno]
                        }
                        class_methods.append(method_info)
                
                class_info = {
                    'name': node.name,
                    'docstring': ast.get_docstring(node) or "",
                    'methods': class_methods
                }
                classes.append(class_info)
        
        return {
            'functions': functions,
            'classes': classes,
            'filepath': file_path,
            'content': content
        }
    except SyntaxError:
        print(f"Syntax error in {file_path}")
        return {
            'functions': [],
            'classes': [],
            'filepath': file_path,
            'content': content
        }

def generate_test_for_file(file_info):
    """Generate test cases for a file using AI."""
    content_summary = file_info['content']
    
    # If file is too large, truncate and summarize
    if len(content_summary) > 6000:
        content_summary = content_summary[:3000] + "\n...[content truncated]...\n" + content_summary[-3000:]
    
    # Extract module name for test file name
    module_path = file_info['filepath']
    if module_path.startswith('app/'):
        module_path = module_path[4:]  # Remove 'app/' prefix
    
    module_name = os.path.splitext(module_path)[0].replace('/', '.')
    
    # Create file structure description
    functions_desc = "\n".join([
        f"Function: {f['name']}\nArgs: {', '.join(f['args'])}\nDocstring: {f['docstring']}"
        for f in file_info['functions']
    ])
    
    classes_desc = "\n".join([
        f"Class: {c['name']}\nDocstring: {c['docstring']}\nMethods: " + 
        ", ".join([m['name'] for m in c['methods']])
        for c in file_info['classes']
    ])
    
    # Build the prompt
    prompt = f"""
I need you to generate pytest test cases for the following Python file from a Flask REST API:

File path: {file_info['filepath']}

**File content summary:**
```python
{content_summary}
```

**Functions:**
{functions_desc}

**Classes:**
{classes_desc}

Based on this code, please generate comprehensive pytest test cases that:
1. Test all public functions and methods
2. Include tests for both success cases and edge cases
3. Include proper test fixtures if needed
4. Follow pytest best practices
5. Make sure tests are independent and don't rely on side effects

Please provide ONLY the complete test file content, no explanations or comments outside the code.
The tests should be compatible with the existing test structure in the project.
The test filename should be based on the original filename (e.g., test_routes.py for routes.py).
    """

    # Generate test content using AI
    response = client.chat.completions.create(
        model="claude-3-7-sonnet-20250219",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=3000
    )
    
    test_content = response.choices[0].message.content
    
    # Extract the Python code if it's wrapped in code blocks
    code_pattern = re.compile(r"```python(.*?)```", re.DOTALL)
    code_match = code_pattern.search(test_content)
    if code_match:
        test_content = code_match.group(1).strip()
    
    return {
        'original_file': file_info['filepath'],
        'test_content': test_content,
        'test_file': determine_test_filename(file_info['filepath'])
    }

def determine_test_filename(filepath):
    """Determine the appropriate test filename for a given file."""
    # Extract filename from path
    filename = os.path.basename(filepath)
    # Extract module name without extension
    module_name = os.path.splitext(filename)[0]
    
    if filepath.startswith('app/routes'):
        return f"tests/test_routes.py"
    elif filepath.startswith('app/services'):
        return f"tests/test_services.py"
    elif filepath.startswith('app/models'):
        return f"tests/test_models.py"
    else:
        # Default case
        return f"tests/test_{module_name}.py"

def update_or_create_test_file(test_info):
    """Update existing test file or create a new one."""
    test_file = test_info['test_file']
    test_content = test_info['test_content']
    original_file = test_info['original_file']
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(test_file), exist_ok=True)
    
    existing_content = ""
    new_file = not os.path.exists(test_file)
    
    if not new_file:
        # Read existing test file
        with open(test_file, 'r') as f:
            existing_content = f.read()
    
    if new_file:
        # Create new test file
        print(f"Creating new test file: {test_file}")
        with open(test_file, 'w') as f:
            f.write(test_content)
        return True
    else:
        # Generate a section comment to identify the new tests
        module_name = os.path.basename(original_file).replace('.py', '')
        section_header = f"\n\n# Tests for {module_name} (auto-generated)\n"
        
        # Check if existing content already has tests for this module
        if f"Tests for {module_name}" in existing_content:
            print(f"Tests for {module_name} already exist in {test_file}")
            # TODO: More sophisticated merging of existing tests
            return False
        else:
            # Append new tests to existing file
            print(f"Appending tests for {module_name} to {test_file}")
            with open(test_file, 'a') as f:
                f.write(section_header)
                f.write(test_content)
            return True

def main():
    """Main function to orchestrate test generation."""
    changed_files = get_changed_files()
    print(f"Found {len(changed_files)} changed Python files")
    
    updates_made = False
    
    for file_path in changed_files:
        print(f"Analyzing {file_path}...")
        file_info = extract_function_info(file_path)
        
        # Skip files with no functions or classes
        if not file_info['functions'] and not file_info['classes']:
            print(f"No functions or classes found in {file_path}, skipping")
            continue
        
        print(f"Generating tests for {file_path}...")
        test_info = generate_test_for_file(file_info)
        
        print(f"Updating/creating test file {test_info['test_file']}...")
        if update_or_create_test_file(test_info):
            updates_made = True
    
    if updates_made:
        print("Tests generated successfully!")
    else:
        print("No new tests were generated.")

if __name__ == "__main__":
    main()