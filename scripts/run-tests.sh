#!/bin/bash

# Enable debug output
set -x

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if Docker is installed
if ! command_exists docker; then
    echo "❌ Error: Docker is not installed. Please install Docker Desktop from https://www.docker.com/products/docker-desktop/"
    exit 1
fi

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi

# Clean up any existing test container
echo "🧹 Cleaning up any existing containers..."
docker rm -f para-bank-tests 2>/dev/null || true

# Create test results directory with full permissions
echo "📁 Creating test results directory..."
mkdir -p test-results
chmod -R 777 test-results

# Build the test image first to see any build errors
echo "🔨 Building test container..."
if docker compose version &>/dev/null; then
    echo "Using 'docker compose' (new syntax)"
    COMPOSE_CMD="docker compose"
else
    echo "Using 'docker-compose' (legacy syntax)"
    COMPOSE_CMD="docker-compose"
fi

# Build without running
$COMPOSE_CMD build test

# Run the tests with full output
echo "🚀 Starting tests..."
$COMPOSE_CMD run --rm test /bin/bash -c "
    echo '=== Python Environment ===' &&
    python3 --version &&
    pip3 --version &&
    echo '\n=== Installed Packages ===' &&
    pip3 list &&
    echo '\n=== Creating Test Results Directory ===' &&
    mkdir -p /workspace/test-results &&
    chown -R root:root /workspace/test-results &&
    chmod -R 777 /workspace/test-results &&
    echo '\n=== Running Tests ===' &&
    cd /workspace && \
    PLAYWRIGHT_HEADLESS=1 python3 -m pytest tests/ -v \
        --html=test-results/report.html \
        --self-contained-html \
        --browser=chromium || exit 1
"
test_status=$?

# Check if tests passed
if [ $test_status -eq 0 ]; then
    echo "✅ All tests passed!"
    # Only open the report if on macOS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if [ -f "test-results/report.html" ]; then
            echo "📊 Opening test report..."
            open test-results/report.html
        else
            echo "⚠️  Test report not found at test-results/report.html"
            echo "Checking directory contents:"
            ls -la test-results/ || echo "No test-results directory found"
        fi
    fi
else
    echo "❌ Some tests failed. Check the output above for details."
    echo "Checking for test report..."
    if [ -f "test-results/report.html" ]; then
        echo "📊 Test report is available at test-results/report.html"
        if [[ "$OSTYPE" == "darwin"* ]]; then
            open test-results/report.html
        fi
    else
        echo "⚠️  No test report was generated."
    fi
fi

exit $test_status
