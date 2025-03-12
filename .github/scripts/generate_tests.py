import os
import subprocess
import ast
import re
import ollama

def get_changed_files():
    """Get list of changed Python files in the pull request."""
    if os.environ.get("GITHUB_BASE_REF"):
        cmd = f"git diff --name-only origin/{os.environ.get('GITHUB_BASE_REF')}...HEAD | grep '\\.py$'"
    else:
        cmd = "git diff --name-only HEAD~1 HEAD | grep '\\.py$'"
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    changed_files = result.stdout.strip().split('\n')
    return [f for f in changed_files if f and f.startswith('app/')]
    
def clean_generated_content(content):
    """Remove AI reasoning, <think> sections, and merge conflict markers."""
    content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
    content = re.sub(r'<<<<<<<.*?=======|>>>>>>>.*?', '', content, flags=re.DOTALL)
    return content.strip()
    
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
    """Generate test cases for a file using DeepSeek-R1."""
    content_summary = file_info['content']
    
    if len(content_summary) > 6000:
        content_summary = content_summary[:3000] + "\n...[content truncated]...\n" + content_summary[-3000:]
    
    def generate_test_for_file(file_info):
    """Generate test cases for a file using DeepSeek-R1, ensuring strict output formatting."""
    content_summary = file_info['content']
    
    if len(content_summary) > 6000:
        content_summary = content_summary[:3000] + "\n...[content truncated]...\n" + content_summary[-3000:]
    
    prompt = f"""
You are a code generation assistant. Your task is to generate **only** a valid Python test file using `pytest` for the given Flask application file.

**File Path:** {file_info['filepath']}

**File Content:**
```python
{content_summary}
```

**Instructions:**
- Generate `pytest` test cases for **all** functions and methods in the given file.
- Ensure all necessary imports are included at the top.
- Do **not** include explanations, reasoning, or comments that are not part of the test code.
- Use `pytest` fixtures where needed.
- Ensure each test is isolated and follows `pytest` best practices.
- Strictly output only the valid test code.

**Output Format:** 
```python
# Strictly valid Python test code starts here
<test code>
# Strictly valid Python test code ends here
```
"""

    try:
        response = ollama.chat(model="deepseek-r1", messages=[{"role": "user", "content": prompt}])
        test_content = clean_generated_content(response['message']['content'])
    except Exception as e:
        print(f"Error generating tests: {e}")
        return None
    
    return {
        'original_file': file_info['filepath'],
        'test_content': test_content,
        'test_file': determine_test_filename(file_info['filepath'])
    }

def determine_test_filename(filepath):
    """Determine the appropriate test filename for a given file."""
    filename = os.path.basename(filepath)
    module_name = os.path.splitext(filename)[0]
    return f"tests/test_{module_name}.py"

def update_or_create_test_file(test_info):
    """Update existing test file or create a new one."""
    test_file = test_info['test_file']
    test_content = test_info['test_content']
    
    os.makedirs(os.path.dirname(test_file), exist_ok=True)
    
    new_file = not os.path.exists(test_file)
    
    if new_file:
        print(f"Creating new test file: {test_file}")
        with open(test_file, 'w') as f:
            f.write(test_content)
        return True
    else:
        print(f"Appending tests to {test_file}")
        with open(test_file, 'a') as f:
            f.write("\n\n" + test_content)
        return True

def main():
    """Main function to orchestrate test generation."""
    changed_files = get_changed_files()
    print(f"Found {len(changed_files)} changed Python files")
    
    updates_made = False
    
    for file_path in changed_files:
        print(f"Analyzing {file_path}...")
        file_info = extract_function_info(file_path)
        
        if not file_info['functions'] and not file_info['classes']:
            print(f"No functions or classes found in {file_path}, skipping")
            continue
        
        print(f"Generating tests for {file_path}...")
        test_info = generate_test_for_file(file_info)
        
        if test_info is None:
            continue
        
        print(f"Updating/creating test file {test_info['test_file']}...")
        if update_or_create_test_file(test_info):
            updates_made = True
    
    if updates_made:
        print("Tests generated successfully!")
    else:
        print("No new tests were generated.")

if __name__ == "__main__":
    main()
