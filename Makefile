# AI Meal Planner - Poetry Commands

.PHONY: install run dev test clean

# Install dependencies using Poetry (fallback to pip if Poetry fails)
install:
	@echo "Installing dependencies..."
	@if command -v poetry >/dev/null 2>&1; then \
		export PATH="$$HOME/.local/bin:$$PATH" && poetry install --only main || pip install -e .; \
	else \
		pip install -e .; \
	fi

# Run the application
run:
	@echo "Starting AI Meal Planner..."
	gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app

# Development mode
dev:
	@echo "Starting in development mode..."
	FLASK_ENV=development gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app

# Add a new dependency
add:
	@echo "Adding dependency: $(pkg)"
	@if command -v poetry >/dev/null 2>&1; then \
		export PATH="$$HOME/.local/bin:$$PATH" && poetry add $(pkg); \
	else \
		echo "Please add $(pkg) to pyproject.toml dependencies manually"; \
	fi

# Show installed packages
show:
	@echo "Installed packages:"
	@if command -v poetry >/dev/null 2>&1; then \
		export PATH="$$HOME/.local/bin:$$PATH" && poetry show || pip list; \
	else \
		pip list; \
	fi

# Clean cache and temporary files
clean:
	@echo "Cleaning cache..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true