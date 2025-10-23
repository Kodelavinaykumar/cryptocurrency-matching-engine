# GoQuant Matching Engine - VS Code Setup Guide

## 🚀 **How to Run the Application in VS Code**

### **Method 1: Using VS Code Debugger (Recommended)**

1. **Open the project in VS Code**:
   ```bash
   code E:\GoQuant
   ```

2. **Install dependencies** (if not already done):
   - Press `Ctrl+Shift+P`
   - Type "Tasks: Run Task"
   - Select "Install Dependencies"

3. **Start the server**:
   - Press `F5` or go to Run → Start Debugging
   - Select "Start Matching Engine Server"
   - The server will start on http://localhost:8000

4. **Run the demo client** (in a new terminal):
   - Press `Ctrl+Shift+P`
   - Type "Tasks: Run Task"
   - Select "Run Demo Client"

### **Method 2: Using VS Code Tasks**

1. **Open Command Palette**: `Ctrl+Shift+P`

2. **Run tasks**:
   - "Tasks: Run Task" → "Install Dependencies"
   - "Tasks: Run Task" → "Start Server (Uvicorn)"
   - "Tasks: Run Task" → "Run Demo Client"

### **Method 3: Using Integrated Terminal**

1. **Open Terminal**: `Ctrl+`` (backtick)

2. **Run commands**:
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   
   # Start server
   python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   
   # In another terminal, run demo
   python test_client.py
   ```

## 🔧 **VS Code Configuration**

### **Debug Configurations**
- **Start Matching Engine Server**: Runs the main server
- **Run Test Client**: Runs the demonstration client
- **Run Tests**: Executes all unit tests
- **Run Performance Benchmarks**: Runs performance tests

### **Tasks Available**
- **Install Dependencies**: Installs required packages
- **Start Server (Uvicorn)**: Starts the server with auto-reload
- **Run Tests**: Executes the test suite
- **Run Demo Client**: Runs the demonstration

### **Settings Applied**
- Python linting enabled
- Pytest testing framework configured
- File exclusions for cache files
- PowerShell as default terminal

## 📁 **Project Structure in VS Code**

```
GoQuant/
├── .vscode/                 # VS Code configuration
│   ├── launch.json         # Debug configurations
│   ├── tasks.json          # Task definitions
│   └── settings.json       # Workspace settings
├── src/                    # Source code
│   ├── api/               # REST and WebSocket APIs
│   ├── matching_engine/   # Core matching logic
│   └── models/            # Data models
├── tests/                 # Test suite
├── docs/                  # Documentation
├── main.py                # Application entry point
├── test_client.py         # Demonstration client
└── requirements.txt       # Dependencies
```

## 🎯 **Quick Start Steps**

1. **Open VS Code**:
   ```bash
   code E:\GoQuant
   ```

2. **Install Dependencies**:
   - `Ctrl+Shift+P` → "Tasks: Run Task" → "Install Dependencies"

3. **Start Server**:
   - Press `F5` → Select "Start Matching Engine Server"

4. **View API Documentation**:
   - Open browser to http://localhost:8000/docs

5. **Run Demo**:
   - `Ctrl+Shift+P` → "Tasks: Run Task" → "Run Demo Client"

## 🔍 **Debugging Features**

### **Breakpoints**
- Set breakpoints in any Python file
- Debug through order processing logic
- Inspect order book state
- Monitor trade executions

### **Variable Inspection**
- Watch order objects during processing
- Inspect order book data structures
- Monitor WebSocket connections
- Debug matching algorithms

### **Logging**
- View real-time logs in terminal
- Filter by log level
- Monitor performance metrics
- Track error conditions

## 🧪 **Testing in VS Code**

### **Run All Tests**
- Press `F5` → Select "Run Tests"
- Or use Command Palette: "Tasks: Run Task" → "Run Tests"

### **Run Specific Tests**
- Open test files
- Click "Run Test" above test functions
- Use pytest discovery

### **Performance Testing**
- Press `F5` → Select "Run Performance Benchmarks"
- View benchmark results in terminal

## 🌐 **API Testing**

### **Interactive API Documentation**
- Start server
- Open http://localhost:8000/docs
- Test endpoints directly in browser

### **REST Client**
- Use VS Code REST Client extension
- Create `.http` files for API testing
- Test order submission and management

### **WebSocket Testing**
- Use WebSocket extensions
- Connect to ws://localhost:8000/api/v1/ws/market-data/BTC-USDT
- Monitor real-time data streams

## 📊 **Monitoring and Logs**

### **Real-time Logs**
- View logs in integrated terminal
- Filter by component (api, matching_engine, etc.)
- Monitor performance metrics

### **Health Checks**
- GET http://localhost:8000/health
- Monitor system status
- Check active orders count

## 🚨 **Troubleshooting**

### **Common Issues**

1. **Port Already in Use**:
   ```bash
   # Find process using port 8000
   netstat -ano | findstr :8000
   # Kill process
   taskkill /PID <PID> /F
   ```

2. **Module Not Found**:
   - Run "Install Dependencies" task
   - Check Python interpreter path

3. **Import Errors**:
   - Verify all dependencies installed
   - Check Python path configuration

### **Debug Steps**

1. Check server logs in terminal
2. Verify all dependencies installed
3. Test API endpoints manually
4. Check WebSocket connections
5. Review error messages in logs

## 🎉 **Success Indicators**

When everything is working correctly, you should see:

- ✅ Server starts without errors
- ✅ Health check returns "healthy"
- ✅ API documentation accessible
- ✅ Demo client runs successfully
- ✅ Orders are processed and matched
- ✅ WebSocket connections established
- ✅ Trade executions generated

The GoQuant Matching Engine is now ready to use in VS Code with full debugging, testing, and monitoring capabilities!
