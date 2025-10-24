# GoQuant Matching Engine - VS Code Integration Guide

## Overview

This guide explains how to use the GoQuant Matching Engine with VS Code, including debugging, testing, and development workflows.

## Prerequisites

- **VS Code**: Latest version with Python extension
- **Python**: 3.11 or higher
- **Dependencies**: All project dependencies installed

## VS Code Configuration

### Workspace Settings

The project includes optimized VS Code settings in `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "python",
    "python.linting.enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true
    }
}
```

### Launch Configurations

The `.vscode/launch.json` file provides several debug configurations:

#### 1. Start GoQuant Server
- **Name**: "Start GoQuant Server"
- **Purpose**: Debug the main application
- **Usage**: Press F5 or use Debug panel

#### 2. Run Test Client
- **Name**: "Run Test Client"
- **Purpose**: Debug the demo client
- **Usage**: Select from Debug panel

#### 3. Run Tests
- **Name**: "Run Tests"
- **Purpose**: Debug unit tests
- **Usage**: Select from Debug panel

#### 4. Run Performance Tests
- **Name**: "Run Performance Tests"
- **Purpose**: Debug performance benchmarks
- **Usage**: Select from Debug panel

#### 5. Start Server with Uvicorn
- **Name**: "Start Server with Uvicorn"
- **Purpose**: Debug with hot reload
- **Usage**: Select from Debug panel

### Task Definitions

The `.vscode/tasks.json` file provides automated tasks:

#### Available Tasks

1. **Install Dependencies**
   - Installs all required packages
   - Usage: `Ctrl+Shift+P` → "Tasks: Run Task" → "Install Dependencies"

2. **Start Server**
   - Starts the matching engine server
   - Usage: `Ctrl+Shift+P` → "Tasks: Run Task" → "Start Server"

3. **Start Server with Uvicorn**
   - Starts server with hot reload
   - Usage: `Ctrl+Shift+P` → "Tasks: Run Task" → "Start Server with Uvicorn"

4. **Run Demo Client**
   - Runs the demonstration client
   - Usage: `Ctrl+Shift+P` → "Tasks: Run Task" → "Run Demo Client"

5. **Run Tests**
   - Executes unit tests
   - Usage: `Ctrl+Shift+P` → "Tasks: Run Task" → "Run Tests"

6. **Run Performance Tests**
   - Executes performance benchmarks
   - Usage: `Ctrl+Shift+P` → "Tasks: Run Task" → "Run Performance Tests"

7. **Run All Tests**
   - Executes all tests
   - Usage: `Ctrl+Shift+P` → "Tasks: Run Task" → "Run All Tests"

8. **Start with Startup Script**
   - Uses the interactive startup script
   - Usage: `Ctrl+Shift+P` → "Tasks: Run Task" → "Start with Startup Script"

9. **Check Health**
   - Tests server health endpoint
   - Usage: `Ctrl+Shift+P` → "Tasks: Run Task" → "Check Health"

10. **View API Docs**
    - Opens API documentation in browser
    - Usage: `Ctrl+Shift+P` → "Tasks: Run Task" → "View API Docs"

## Development Workflow

### 1. Initial Setup

1. **Open Project**
   ```bash
   code .
   ```

2. **Install Dependencies**
   - Press `Ctrl+Shift+P`
   - Type "Tasks: Run Task"
   - Select "Install Dependencies"

3. **Verify Setup**
   - Press `Ctrl+Shift+P`
   - Type "Tasks: Run Task"
   - Select "Check Health"

### 2. Development Mode

1. **Start Server with Hot Reload**
   - Press `Ctrl+Shift+P`
   - Type "Tasks: Run Task"
   - Select "Start Server with Uvicorn"

2. **Open API Documentation**
   - Press `Ctrl+Shift+P`
   - Type "Tasks: Run Task"
   - Select "View API Docs"

3. **Run Demo Client**
   - Press `Ctrl+Shift+P`
   - Type "Tasks: Run Task"
   - Select "Run Demo Client"

### 3. Debugging

#### Debug Server
1. Set breakpoints in your code
2. Press `F5` or select "Start GoQuant Server" from Debug panel
3. Use debug controls to step through code

#### Debug Tests
1. Set breakpoints in test files
2. Select "Run Tests" from Debug panel
3. Debug test execution

#### Debug Client
1. Set breakpoints in `test_client.py`
2. Select "Run Test Client" from Debug panel
3. Debug client execution

### 4. Testing

#### Run Unit Tests
- Press `Ctrl+Shift+P`
- Type "Tasks: Run Task"
- Select "Run Tests"

#### Run Performance Tests
- Press `Ctrl+Shift+P`
- Type "Tasks: Run Task"
- Select "Run Performance Tests"

#### Run All Tests
- Press `Ctrl+Shift+P`
- Type "Tasks: Run Task"
- Select "Run All Tests"

## VS Code Features

### IntelliSense

The project is configured for full IntelliSense support:

- **Type Hints**: Full type annotations throughout
- **Import Completion**: Automatic import suggestions
- **Code Completion**: Context-aware suggestions
- **Error Detection**: Real-time error highlighting

### Code Formatting

Automatic code formatting is enabled:

- **Black Formatter**: Consistent code style
- **Format on Save**: Automatic formatting
- **Import Organization**: Automatic import sorting

### Linting

Comprehensive linting is configured:

- **Flake8**: Code style and error detection
- **MyPy**: Type checking
- **Real-time**: Live error highlighting

### Testing Integration

VS Code testing integration is configured:

- **Pytest**: Test discovery and execution
- **Test Explorer**: Visual test management
- **Debug Tests**: Debug individual tests
- **Coverage**: Test coverage visualization

## Debugging Tips

### 1. Setting Breakpoints

- Click in the left margin to set breakpoints
- Use conditional breakpoints for specific conditions
- Set logpoints for non-intrusive logging

### 2. Debug Console

- Use the Debug Console to evaluate expressions
- Inspect variables and call functions
- Test code snippets during debugging

### 3. Call Stack

- Use the Call Stack panel to navigate execution
- Click on stack frames to jump to code
- Inspect variables at each level

### 4. Watch Expressions

- Add variables to watch in the Watch panel
- Monitor variable values during execution
- Evaluate complex expressions

## Performance Monitoring

### 1. Built-in Profiler

VS Code includes a built-in profiler:

- **CPU Profiling**: Identify performance bottlenecks
- **Memory Profiling**: Detect memory leaks
- **Call Graph**: Visualize function calls

### 2. Extension Recommendations

Install these extensions for enhanced development:

- **Python**: Official Python extension
- **Pylance**: Fast Python language server
- **Python Test Explorer**: Test management
- **Python Docstring Generator**: Documentation
- **GitLens**: Git integration

## Troubleshooting

### Common Issues

#### 1. Python Interpreter Not Found
```bash
# Check Python installation
python --version

# Set correct interpreter
Ctrl+Shift+P → "Python: Select Interpreter"
```

#### 2. Dependencies Not Installed
```bash
# Install dependencies
pip install -r requirements.txt

# Or use VS Code task
Ctrl+Shift+P → "Tasks: Run Task" → "Install Dependencies"
```

#### 3. Debug Configuration Issues
- Check `.vscode/launch.json` syntax
- Verify Python path in configurations
- Ensure all required files exist

#### 4. Test Discovery Issues
- Check `pytest.ini` configuration
- Verify test file naming conventions
- Ensure test dependencies are installed

### Performance Issues

#### 1. Slow IntelliSense
- Disable unnecessary extensions
- Increase Python analysis memory
- Use Pylance instead of Jedi

#### 2. High Memory Usage
- Close unused files
- Disable auto-save for large files
- Restart VS Code periodically

## Best Practices

### 1. Code Organization

- Use consistent file structure
- Follow Python naming conventions
- Organize imports properly

### 2. Testing

- Write tests before implementing features
- Use descriptive test names
- Keep tests independent and isolated

### 3. Debugging

- Use meaningful variable names
- Add logging for complex operations
- Test edge cases thoroughly

### 4. Performance

- Profile code regularly
- Optimize hot paths
- Monitor memory usage

## Integration with External Tools

### 1. Git Integration

VS Code includes built-in Git support:

- **Source Control Panel**: Visual Git operations
- **Diff Viewer**: Compare file changes
- **Merge Conflict Resolution**: Visual conflict resolution

### 2. Terminal Integration

Use the integrated terminal:

- **Multiple Terminals**: Open multiple terminal instances
- **Task Integration**: Run tasks in terminal
- **Shell Integration**: Use your preferred shell

### 3. Extension Marketplace

Install additional extensions:

- **Docker**: Container management
- **Kubernetes**: K8s resource management
- **REST Client**: API testing
- **Thunder Client**: API testing alternative

## Conclusion

VS Code provides excellent support for developing the GoQuant Matching Engine. The configured settings, launch configurations, and tasks make development efficient and productive.

### Key Benefits

- **Integrated Development**: Everything in one place
- **Powerful Debugging**: Comprehensive debugging tools
- **Automated Tasks**: Streamlined development workflow
- **Extensible**: Rich extension ecosystem
- **Productive**: Optimized for Python development

The VS Code integration makes the GoQuant Matching Engine development experience smooth and efficient, enabling rapid iteration and comprehensive testing.
