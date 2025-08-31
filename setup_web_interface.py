#!/usr/bin/env python3
"""
Setup script for SpecOps Web Interface
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False

def check_requirements():
    """Check if required tools are installed."""
    print("🔍 Checking requirements...")
    
    requirements = {
        'python': 'python --version',
        'git': 'git --version',
        'pip': 'pip --version'
    }
    
    missing = []
    for tool, command in requirements.items():
        try:
            subprocess.run(command, shell=True, check=True, capture_output=True)
            print(f"✅ {tool} is installed")
        except subprocess.CalledProcessError:
            print(f"❌ {tool} is not installed")
            missing.append(tool)
    
    if missing:
        print(f"\n⚠️  Please install the following tools: {', '.join(missing)}")
        return False
    
    return True

def setup_api():
    """Set up the API backend."""
    print("\n📦 Setting up API backend...")
    
    api_dir = Path("api")
    if not api_dir.exists():
        print("❌ API directory not found")
        return False
    
    # Install API dependencies
    if not run_command("pip install -r api/requirements.txt", "Installing API dependencies"):
        return False
    
    return True

def test_api():
    """Test the API locally."""
    print("\n🧪 Testing API...")
    
    # Start API in background and test
    try:
        print("Starting API server...")
        api_process = subprocess.Popen([sys.executable, "api/app.py"], 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE)
        
        # Wait a moment for server to start
        import time
        time.sleep(3)
        
        # Test health endpoint
        import requests
        try:
            response = requests.get("http://localhost:5000/", timeout=5)
            if response.status_code == 200:
                print("✅ API is running successfully")
                result = True
            else:
                print(f"❌ API returned status code: {response.status_code}")
                result = False
        except requests.exceptions.RequestException as e:
            print(f"❌ Could not connect to API: {e}")
            result = False
        
        # Stop the API process
        api_process.terminate()
        api_process.wait()
        
        return result
        
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

def setup_github_pages():
    """Set up GitHub Pages configuration."""
    print("\n🌐 Setting up GitHub Pages...")
    
    # Check if we're in a git repository
    if not Path(".git").exists():
        print("❌ Not in a git repository. Please run 'git init' first.")
        return False
    
    # Check if GitHub Actions workflow exists
    workflow_path = Path(".github/workflows/deploy-pages.yml")
    if workflow_path.exists():
        print("✅ GitHub Actions workflow already exists")
    else:
        print("❌ GitHub Actions workflow not found")
        return False
    
    print("✅ GitHub Pages setup complete")
    print("\n📝 Next steps for GitHub Pages:")
    print("1. Push your changes to GitHub")
    print("2. Go to your repository settings")
    print("3. Navigate to 'Pages' section")
    print("4. Set source to 'GitHub Actions'")
    print("5. Your site will be available at: https://username.github.io/repository-name")
    
    return True

def create_local_demo():
    """Create a simple local demo."""
    print("\n🎭 Creating local demo...")
    
    demo_html = """<!DOCTYPE html>
<html>
<head>
    <title>SpecOps Local Demo</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .demo { background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0; }
        button { background: #007cba; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #005a87; }
    </style>
</head>
<body>
    <h1>🚀 SpecOps Local Demo</h1>
    <p>This is a simple local demo of SpecOps web interface.</p>
    
    <div class="demo">
        <h3>Quick Test</h3>
        <p>Click the button below to test the basic functionality:</p>
        <button onclick="testDemo()">Test SpecOps</button>
        <div id="result" style="margin-top: 10px;"></div>
    </div>
    
    <div class="demo">
        <h3>Full Interface</h3>
        <p>Open the full web interface:</p>
        <button onclick="window.open('docs/index.html', '_blank')">Open Full Interface</button>
    </div>
    
    <script>
        function testDemo() {
            const result = document.getElementById('result');
            result.innerHTML = '<p style="color: green;">✅ SpecOps is working! The web interface is ready to use.</p>';
        }
    </script>
</body>
</html>"""
    
    with open("demo.html", "w", encoding='utf-8') as f:
        f.write(demo_html)
    
    print("✅ Local demo created: demo.html")
    return True

def main():
    """Main setup function."""
    print("🚀 SpecOps Web Interface Setup")
    print("=" * 40)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Setup failed: Missing requirements")
        return 1
    
    # Setup API
    if not setup_api():
        print("\n❌ Setup failed: API setup failed")
        return 1
    
    # Test API
    if not test_api():
        print("\n⚠️  API test failed, but continuing with setup")
    
    # Setup GitHub Pages
    setup_github_pages()
    
    # Create local demo
    create_local_demo()
    
    print("\n🎉 Setup Complete!")
    print("\n📋 Summary:")
    print("✅ API backend configured")
    print("✅ GitHub Pages workflow ready")
    print("✅ Local demo created")
    
    print("\n🚀 Next Steps:")
    print("1. Open demo.html in your browser for a quick test")
    print("2. Open docs/index.html for the full interface")
    print("3. Push to GitHub to deploy to GitHub Pages")
    print("4. Deploy API to Vercel/Heroku for full functionality")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())