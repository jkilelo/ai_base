# React Development Environment

This directory contains a React.js environment similar to a Python virtual environment (`venv`). All dependencies are isolated within this project's `node_modules` directory.

## Environment Setup

### Current Setup
- **React**: 19.1.0 (latest)
- **Node.js**: 22.16.0 (LTS)
- **TypeScript**: 4.9.5
- **Package Manager**: npm
- **Build Tool**: react-scripts (webpack-based)

### Project Structure
```
frontend/
├── node_modules/          # Dependencies (like Python site-packages)
├── public/                # Static assets
├── src/                   # Source code
├── package.json           # Dependencies & scripts (like requirements.txt)
├── package-lock.json      # Dependency lock file
├── tsconfig.json          # TypeScript configuration
└── .gitignore            # Git ignore rules
```

## Available Commands

### Development
```bash
npm start              # Start development server (http://localhost:3000)
npm test               # Run tests in watch mode
npm run build          # Build for production
npm run eject          # Eject from create-react-app (irreversible)
```

### Package Management
```bash
npm install <package>     # Install a new package
npm install              # Install all dependencies
npm uninstall <package>  # Remove a package
npm list                 # List installed packages
npm outdated            # Check for outdated packages
npm update              # Update packages
```

## Environment Isolation

Similar to Python's virtual environments, this React environment:

1. **Isolated Dependencies**: All packages are installed locally in `node_modules/`
2. **Version Control**: `package.json` and `package-lock.json` ensure consistent installs
3. **Environment Variables**: Can be set via `.env` files
4. **Development Tools**: Integrated linting, testing, and building

## Adding New Dependencies

### Runtime Dependencies
```bash
npm install axios react-router-dom styled-components
```

### Development Dependencies
```bash
npm install -D eslint-plugin-react-hooks @types/styled-components
```

## Environment Variables

Create a `.env` file in the frontend directory:
```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development
```

## TypeScript Support

This environment includes full TypeScript support:
- Type checking during development
- IntelliSense in VS Code
- Compile-time error detection
- Modern ES6+ features

## Production Build

```bash
npm run build
```

Creates optimized production files in the `build/` directory.

## Comparison with Python Virtual Environment

| Python venv               | React Environment      |
| ------------------------- | ---------------------- |
| `python -m venv env`      | `npx create-react-app` |
| `pip install package`     | `npm install package`  |
| `requirements.txt`        | `package.json`         |
| `pip freeze`              | `npm list`             |
| `source env/bin/activate` | `cd frontend`          |
| `site-packages/`          | `node_modules/`        |

## Modern Alternative: Vite

For faster development, consider using Vite instead of create-react-app:
```bash
npm create vite@latest my-react-app -- --template react-ts
```

Vite offers:
- Faster hot reloading
- Quicker builds
- More modern tooling
- Better performance
