# AI Base Project

A full-stack development environment with isolated environments for different technologies.

## Project Structure

```
ai_base/
├── frontend/                    # React.js Environment (like Python venv)
│   ├── node_modules/           # Dependencies (isolated)
│   ├── src/                    # React source code
│   ├── craco.config.js         # Webpack configuration override
│   ├── package.json            # Dependency management
│   ├── .env                    # Environment variables
│   └── README.md               # Frontend documentation
├── test-webpack-fix.bat        # Webpack fix verification script
├── main.py                     # Python entry point (future)
└── README.md                   # This file
```

## Quick Start

### Prerequisites
- ✅ Node.js 22.16.0 LTS (installed)
- ✅ npm 9.4.1 (included with Node.js)
- ✅ Git (for version control)

### Get Started in 30 Seconds
```bash
cd frontend
npm start
```
Open http://localhost:3000 - your React app is running! 🚀

## React Frontend Environment

This project includes a complete React.js development environment that works similarly to Python's virtual environments:

### Features
- ✅ **React 19.1.0 with TypeScript support**
- ✅ **Node.js 22.16.0 LTS**
- ✅ **CRACO configuration for advanced webpack customization**
- ✅ **Webpack-dev-server deprecation warnings FIXED**
- ✅ **Isolated dependencies in `node_modules/`**
- ✅ **Development server on http://localhost:3000**
- ✅ **Hot reloading and fast refresh**
- ✅ **Built-in testing framework**
- ✅ **Production build optimization**
- ✅ **ESLint and TypeScript configuration**

### Available Commands
```bash
npm start              # Start development server (http://localhost:3000)
npm test               # Run tests in watch mode
npm run build          # Build for production
npm install <package>  # Add new packages
```

### Python Environment (Future)
Space reserved for Python backend environment.

## Environment Comparison

| Feature                   | Python venv                | React Environment     |
| ------------------------- | -------------------------- | --------------------- |
| **Activation**            | `source venv/bin/activate` | `cd frontend`         |
| **Package Install**       | `pip install package`      | `npm install package` |
| **Dependency File**       | `requirements.txt`         | `package.json`        |
| **Dependencies Folder**   | `site-packages/`           | `node_modules/`       |
| **Environment Isolation** | ✅                          | ✅                     |
| **Version Lock**          | `pip freeze`               | `package-lock.json`   |

## Webpack Deprecation Warnings - FIXED ✅

This project includes a complete fix for webpack-dev-server deprecation warnings that commonly appear in Create React App projects.

### What was Fixed

- Eliminated `onAfterSetupMiddleware` and `onBeforeSetupMiddleware` deprecation warnings
- Implemented modern `setupMiddlewares` API using CRACO configuration
- Maintained all React development features (hot reload, TypeScript, etc.)

### Technical Details

- **CRACO Configuration**: Uses `@craco/craco` to override webpack-dev-server config
- **Modern API**: Implements `setupMiddlewares` instead of deprecated middleware options
- **Environment Variables**: Added `.env` file for additional configuration
- **Non-Intrusive**: No need to eject from Create React App

### Files Involved

- `frontend/craco.config.js` - Main webpack configuration override
- `frontend/.env` - Environment variables and Node.js options
- `frontend/package.json` - Scripts updated to use CRACO
- `test-webpack-fix.bat` - Verification script

For detailed technical implementation, see [`frontend/README.md`](frontend/README.md).

## Development Workflow

### Adding Dependencies

```bash
# Runtime dependencies
npm install axios react-router-dom styled-components

# Development dependencies  
npm install -D @types/styled-components eslint-plugin-react-hooks
```

### Environment Variables

Create `.env` files for environment-specific configuration:

**Frontend (.env):**

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development
NODE_OPTIONS=--no-deprecation
```

## Git Integration

The repository is initialized with appropriate `.gitignore` files:

- `node_modules/` excluded from version control
- Build artifacts ignored
- Environment files template included

## Next Steps

1. **Backend Setup:** Add Python/Django or Node.js backend
2. **Database:** Configure database connection
3. **API Integration:** Connect frontend to backend APIs
4. **Deployment:** Set up CI/CD pipeline
5. **Testing:** Expand test coverage

## Support

For detailed development information, see:

- [Frontend Development Guide](frontend/README.md)

## Version History

- **v0.1.0** - Initial React environment setup with TypeScript
- **v0.1.1** - Fixed webpack-dev-server deprecation warnings using CRACO
- Node.js 22.16.0 LTS, React 19.1.0, TypeScript support, CRACO configuration
