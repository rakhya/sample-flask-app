import os
import subprocess
import ast
import requests
import ollama

OLLAMA_URL = "http://localhost:11434/api/tags"  # Adjust if running remotely

def is_ollama_running():
    """Check if Ollama is running to avoid unnecessary failures."""
    try:
        response = requests.get(OLLAMA_URL, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def get_changed_files():
    """Get list of changed Python files in the pull request."""
    if os.environ.get("GITHUB_BASE_REF"):
        cmd = f"git diff --name-only origin/{os.environ.get('GITHUB_BASE_REF')}...HEAD | grep '\\.py$'"
    else:
        cmd = "git diff --name-only HEAD~1 HEAD | grep '\\.py$'"
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    changed_files = result.stdout.strip().split('\n')
    return [f for f in changed_files if f and f.startswith('app/')]

def extract_function_info(file_path):
    """Extract information about functions and classes in a Python file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
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
        return None

def generate_test_for_file(file_info):
    """Generate test cases for a file using DeepSeek-R1."""
    content_summary = file_info['content']
    
    if len(content_summary) > 6000:
        content_summary = content_summary[:3000] + "\n...[content truncated]...\n" + content_summary[-3000:]
    
    prompt = f"""
Generate pytest test cases for the following Python Flask file:

**File Path:** {file_info['filepath']}

**File Content Summary:**
```python
{content_summary}
```

**Requirements:**
1. Generate pytest tests for all functions and methods.
2. Include edge cases and invalid inputs.
3. Use pytest fixtures if needed.
4. Follow pytest best practices.
5. Ensure tests are isolated and independent.

Output only the test file content.
"""

    try:
        response = ollama.chat(
            model="deepseek-r1",
            messages=[{"role": "user", "content": prompt}],
            timeout=30  # Prevent infinite hanging
        )
        test_content = response['message']['content']
        return {
            'original_file': file_info['filepath'],
            'test_content': test_content,
            'test_file': determine_test_filename(file_info['filepath'])
        }
    except Exception as e:
        print(f"Error generating tests: {e}")
        return None

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
    
    if not is_ollama_running():
        print("❌ Ollama is not running. Exiting test generation.")
        exit(1)
    
    changed_files = get_changed_files()
    print(f"🔍 Found {len(changed_files)} changed Python files")
    
    updates_made = False
    
    for file_path in changed_files:
        print(f"📂 Analyzing {file_path}...")
        file_info = extract_function_info(file_path)
        
        if not file_info:
            print(f"⚠️ Skipping {file_path} due to syntax errors.")
            continue

        if not file_info['functions'] and not file_info['classes']:
            print(f"ℹ️ No functions or classes found in {file_path}, skipping.")
            continue
        
        print(f"📝 Generating tests for {file_path}...")
        test_info = generate_test_for_file(file_info)
        
        if not test_info:
            print(f"⚠️ Failed to generate tests for {file_path}.")
            continue
        
        print(f"📄 Updating/creating test file {test_info['test_file']}...")
        if update_or_create_test_file(test_info):
            updates_made = True
    
    if updates_made:
        print("✅ Tests generated successfully!")
    else:
        print("ℹ️ No new tests were generated.")

if __name__ == "__main__":
    main()
