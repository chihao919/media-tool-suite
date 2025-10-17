# Makefile for 檔案豪幫手 (Media Tool Suite)

APP_NAME := 檔案豪幫手
APP_VERSION := 2.0.0
PYTHON := python3

# Default target
.PHONY: all
all: help

# Help target
.PHONY: help
help:
	@echo "🎬 檔案豪幫手 (Media Tool Suite) Build System"
	@echo "=============================================="
	@echo ""
	@echo "Available targets:"
	@echo "  dev          - Run in development mode"
	@echo "  test         - Run all tests"
	@echo "  clean        - Clean build artifacts"
	@echo "  build        - Build for current platform"
	@echo "  build-mac    - Build macOS application"
	@echo "  build-win    - Build Windows executable"
	@echo "  dist         - Create distribution packages"
	@echo "  install      - Install development dependencies"
	@echo "  format       - Format code with black"
	@echo "  lint         - Run code linting"
	@echo ""

# Development mode
.PHONY: dev
dev:
	@echo "🚀 Starting development mode..."
	$(PYTHON) main.py

# Run tests
.PHONY: test
test:
	@echo "🧪 Running tests..."
	$(PYTHON) -m pytest tests/ -v
	@echo "🧪 Running core conversion tests..."
	$(PYTHON) tests/test_conversion_core.py
	@echo "🧪 Running design pattern tests..."
	$(PYTHON) tests/test_design_patterns.py

# Clean build artifacts
.PHONY: clean
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf builds/
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	rm -rf __pycache__/
	rm -rf src/__pycache__/
	rm -f *.pyc
	rm -f *.pyo
	rm -f *.dmg
	rm -f *.exe
	rm -f installer.nsi
	@echo "✅ Clean completed"

# Install development dependencies
.PHONY: install
install:
	@echo "📥 Installing development dependencies..."
	pip install --upgrade pip
	pip install py2app pyinstaller
	pip install black flake8 pytest
	@echo "✅ Dependencies installed"

# Build for current platform
.PHONY: build
build:
	@echo "📦 Building for current platform..."
	@if [ "$(shell uname)" = "Darwin" ]; then \
		$(MAKE) build-mac; \
	elif [ "$(OS)" = "Windows_NT" ]; then \
		$(MAKE) build-win; \
	else \
		$(MAKE) build-linux; \
	fi

# Build macOS application
.PHONY: build-mac
build-mac:
	@echo "🍎 Building macOS application..."
	@if [ "$(shell uname)" != "Darwin" ]; then \
		echo "❌ macOS build requires macOS system"; \
		exit 1; \
	fi
	pip install py2app
	mkdir -p builds/mac
	cp -r src builds/mac/
	cp main.py builds/mac/
	cp build_mac.py builds/mac/
	cd builds/mac && $(PYTHON) build_mac.py py2app
	@echo "✅ macOS build completed: builds/mac/dist/$(APP_NAME).app"

# Build Windows executable
.PHONY: build-win
build-win:
	@echo "🪟 Building Windows executable..."
	pip install pyinstaller
	mkdir -p builds/windows
	cp -r src builds/windows/
	cp main.py builds/windows/
	cp build_windows.py builds/windows/
	cd builds/windows && $(PYTHON) build_windows.py
	@echo "✅ Windows build completed: builds/windows/dist/$(APP_NAME).exe"

# Build Linux portable version
.PHONY: build-linux
build-linux:
	@echo "🐧 Creating Linux portable version..."
	mkdir -p builds/linux/$(APP_NAME)
	cp -r src builds/linux/$(APP_NAME)/
	cp main.py builds/linux/$(APP_NAME)/
	cp README.md builds/linux/$(APP_NAME)/
	echo '#!/bin/bash\ncd "$$(dirname "$$0")"\npython3 main.py "$$@"' > builds/linux/$(APP_NAME)/launch.sh
	chmod +x builds/linux/$(APP_NAME)/launch.sh
	cd builds/linux && tar -czf $(APP_NAME)_v$(APP_VERSION)_Linux.tar.gz $(APP_NAME)
	@echo "✅ Linux portable version: builds/linux/$(APP_NAME)_v$(APP_VERSION)_Linux.tar.gz"

# Create distribution packages
.PHONY: dist
dist: clean
	@echo "📦 Creating distribution packages..."
	$(MAKE) build
	@echo "✅ Distribution packages created in builds/"

# Format code with black
.PHONY: format
format:
	@echo "🎨 Formatting code..."
	black src/ tests/ *.py
	@echo "✅ Code formatting completed"

# Run code linting
.PHONY: lint
lint:
	@echo "🔍 Running code linting..."
	flake8 src/ tests/ --max-line-length=100 --ignore=E203,W503
	@echo "✅ Linting completed"

# Version information
.PHONY: version
version:
	@echo "📋 Version Information:"
	@echo "   App: $(APP_NAME) v$(APP_VERSION)"
	@echo "   Python: $(shell $(PYTHON) --version)"
	@echo "   System: $(shell uname -s) $(shell uname -r)"