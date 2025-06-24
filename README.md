# AI Base Project

A full-stack development environment with isolated environments for different technologies.

## Project Structure

```
ai_base/
├── frontend/                    # React.js Environment (like Python venv)
│   ├── node_modules/           # Dependencies (isolated)
│   ├── src/                    # React source code
│   ├── package.json            # Dependency management
│   └── DEVELOPMENT.md          # Environment documentation
├── activate-react-env.bat      # Windows activation script
├── activate-react-env.ps1      # PowerShell activation script
├── main.py                     # Python entry point (future)
└── README.md                   # This file
```

## Environment Setup

### React.js Frontend Environment
This project includes a complete React.js development environment that works similarly to Python's virtual environments:

**Activation:**
```bash
# Windows Command Prompt
activate-react-env.bat

# PowerShell
.\activate-react-env.ps1

# Manual activation
cd frontend
npm start
```

**Features:**
- ✅ React 19.1.0 with TypeScript support
- ✅ Node.js 22.16.0 LTS
- ✅ Isolated dependencies in `node_modules/`
- ✅ Development server on http://localhost:3000
- ✅ Hot reloading and fast refresh
- ✅ Built-in testing framework
- ✅ Production build optimization
- ✅ ESLint and TypeScript configuration

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

## Getting Started

### Prerequisites
- Node.js 22.16.0 LTS (installed ✅)
- npm 9.4.1 (included with Node.js ✅)
- Git (for version control ✅)

### Quick Start
1. **Activate React Environment:**
   ```bash
   cd frontend
   npm start
   ```

2. **Install New Packages:**
   ```bash
   npm install axios react-router-dom
   ```

3. **Run Tests:**
   ```bash
   npm test
   ```

4. **Build for Production:**
   ```bash
   npm run build
   ```

## Development Workflow

### React Development
1. Navigate to frontend directory
2. Start development server: `npm start`
3. Open http://localhost:3000 in browser
4. Edit files in `src/` directory
5. Changes auto-reload in browser

### Adding Dependencies
```bash
# Runtime dependencies
npm install axios react-router-dom styled-components

# Development dependencies  
npm install -D @types/styled-components eslint-plugin-react-hooks
```

## Environment Variables

Create `.env` files for environment-specific configuration:

**Frontend (.env):**
```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development
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

See individual environment documentation:
- [React Development Guide](frontend/DEVELOPMENT.md)

## Version History

- **v0.1.0** - Initial React environment setup with TypeScript
- Node.js 22.16.0 LTS, React 19.1.0, TypeScript support
