# AI Base Project - Shared Configuration Templates

This directory contains shared configuration templates that are copied to individual version directories.

## Files

### `tsconfig.template.json`
- **Purpose**: TypeScript configuration template for React frontend projects
- **Usage**: Copy to `{version}/frontend/tsconfig.json`
- **Features**: 
  - Strict TypeScript settings
  - Path aliases for better imports (@components, @utils, etc.)
  - React JSX support
  - ES6+ features

### `craco.config.js`
- **Purpose**: Create React App Configuration Override
- **Usage**: Copy to `{version}/frontend/craco.config.js`
- **Features**:
  - Webpack dev-server deprecation warning fixes
  - Custom path aliases
  - API proxy configuration
  - Development middleware setup

### `pyproject.toml`
- **Purpose**: Python project configuration (Black, isort, mypy, pytest)
- **Usage**: Copy to `{version}/pyproject.toml`
- **Features**:
  - Code formatting with Black
  - Import sorting with isort
  - Type checking with mypy
  - Testing with pytest

## Usage in Setup Scripts

The `setup-environment.bat` script automatically copies these templates to the appropriate locations in each version directory.

## Manual Copy Commands

```bash
# Copy TypeScript config to v1 frontend
copy config\tsconfig.template.json v1\frontend\tsconfig.json

# Copy CRACO config to v1 frontend  
copy config\craco.config.js v1\frontend\craco.config.js

# Copy Python config to v1
copy config\pyproject.toml v1\pyproject.toml
```

## Customization

Each version can customize these files after copying. The shared templates provide sensible defaults that work across all versions.
