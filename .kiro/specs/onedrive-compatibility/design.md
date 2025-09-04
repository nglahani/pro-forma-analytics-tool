# OneDrive Compatibility Solution - Design Specification

**Feature**: Docker Compose-based development environment for complete OneDrive isolation  
**Architecture**: Containerized frontend + backend with volume mounting for hot reload  
**Implementation Strategy**: Repository relocation + Docker Compose orchestration

## Solution Architecture

### High-Level Architecture

```
Host Machine (Windows + OneDrive)
├── C:\Development\pro-forma-analytics-tool\    # Relocated repository (outside OneDrive)
│   ├── docker-compose.dev.yml                  # Development orchestration
│   ├── frontend/                               # Next.js source code
│   ├── backend/src/                           # FastAPI source code  
│   └── data/                                  # Database files
│
└── Docker Environment (Linux containers)
    ├── proforma-frontend:dev                   # Next.js dev container
    │   ├── /app/src -> volume mount            # Hot reload source
    │   ├── /app/node_modules -> container      # Isolated dependencies
    │   └── /app/.next -> container             # Build artifacts in container
    │
    ├── proforma-backend:dev                    # FastAPI dev container  
    │   ├── /app/src -> volume mount            # Hot reload source
    │   ├── /app/venv -> container              # Python virtual env
    │   └── /app/data -> host volume            # Database persistence
    │
    └── Docker Networks
        └── proforma-dev-network                # Internal service communication
```

### Component Design

#### 1. Repository Structure (Post-Migration)
```
C:\Development\pro-forma-analytics-tool\
├── docker-compose.dev.yml                     # Development environment
├── docker-compose.yml -> docker-compose.dev.yml  # Default symlink
├── Dockerfile.frontend.dev                    # Frontend development image
├── Dockerfile.backend.dev                     # Backend development image (modified existing)
├── frontend/
│   ├── .dockerignore                          # Exclude node_modules, .next
│   ├── package.json
│   └── [existing Next.js files]
├── src/                                       # Backend source (existing)
├── data/                                      # Database files (existing)
├── scripts/
│   ├── dev-setup.sh                          # Cross-platform dev setup
│   ├── dev-setup.bat                         # Windows dev setup
│   └── migrate-from-onedrive.sh              # Migration helper
└── README.md                                 # Updated with Docker instructions
```

#### 2. Docker Compose Service Definitions

**Frontend Service (`proforma-frontend-dev`):**
- Base Image: `node:18-alpine` (matches existing Node.js 18+ requirement)
- Working Directory: `/app`
- Volume Mounts:
  - `./frontend:/app:cached` (source code with cached mount for performance)
  - `/app/node_modules` (anonymous volume to prevent host conflicts)
  - `/app/.next` (anonymous volume to isolate build artifacts)
- Port Mapping: `3000:3000` (host:container)
- Environment Variables:
  - `NODE_ENV=development`
  - `NEXT_TELEMETRY_DISABLED=1`
  - `WATCHPACK_POLLING=false` (not needed in container)
- Health Check: `curl -f http://localhost:3000 || exit 1`
- Restart Policy: `unless-stopped`

**Backend Service (`proforma-backend-dev`):**
- Base Image: `python:3.11-slim` (existing requirement)
- Working Directory: `/app`
- Volume Mounts:
  - `./src:/app/src:cached` (source code)
  - `./data:/app/data` (database persistence)
  - `./config:/app/config:cached` (configuration files)
- Port Mapping: `8000:8000` (host:container)  
- Environment Variables:
  - `PYTHONPATH=/app`
  - `PRO_FORMA_ENV=development`
  - `PYTHONUNBUFFERED=1`
- Health Check: `curl -f http://localhost:8000/api/v1/health || exit 1`
- Depends On: None (can start independently)
- Restart Policy: `unless-stopped`

**Network Configuration:**
- Custom Bridge Network: `proforma-dev-network`
- Internal DNS resolution between services
- Frontend can call backend via `http://proforma-backend-dev:8000`

#### 3. Container Image Specifications

**Frontend Development Image:**
```dockerfile
FROM node:18-alpine
WORKDIR /app

# Install system dependencies for better performance
RUN apk add --no-cache curl git

# Copy package files for dependency caching
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci --only=development

# Copy source code (via volume mount in compose)
# Build artifacts will be in anonymous volume

# Expose port
EXPOSE 3000

# Development command with hot reload
CMD ["npm", "run", "dev"]
```

**Backend Development Image (Modified Existing):**
```dockerfile
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies (existing from Dockerfile.test)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements for dependency caching
COPY requirements.txt .

# Install Python dependencies (existing logic)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy source code (via volume mount in compose)
# Set Python path
ENV PYTHONPATH=/app

# Expose port  
EXPOSE 8000

# Development command with auto-reload
CMD ["python", "-m", "uvicorn", "src.presentation.api.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
```

### Data Flow Architecture

#### Development Workflow
1. **Developer starts services**: `docker-compose up`
2. **Source code changes** are immediately reflected via volume mounts
3. **Frontend hot reload** works within container (no OneDrive interaction)
4. **Backend auto-reload** works via uvicorn's file watching
5. **Database persistence** maintained via host volume mount
6. **Build artifacts** remain isolated in anonymous container volumes

#### Service Communication
- **Frontend → Backend**: HTTP calls to `http://localhost:8000` (exposed port)
- **Backend → Database**: Direct SQLite file access via volume mount
- **Browser → Frontend**: Direct access to `http://localhost:3000`
- **Development Tools**: All containerized (no host tool conflicts)

### Security Considerations

#### Container Security
- **Non-root user**: Both containers run as non-root users for security
- **Minimal base images**: Alpine/slim variants to reduce attack surface
- **No privileged containers**: Standard user-mode containers only
- **Read-only root filesystem**: Where possible, mount application directories as read-only

#### Development vs Production Isolation
- **Separate configurations**: `docker-compose.dev.yml` vs `docker-compose.yml`
- **Development-only features**: Debug ports, volume mounts, auto-reload
- **Environment separation**: Clear distinction between dev/prod environments

#### Network Security
- **Internal network**: Services communicate via internal Docker network
- **Minimal port exposure**: Only necessary ports exposed to host
- **No external network access**: Unless required for package installations

### Performance Optimization

#### File System Performance
- **Cached volume mounts**: Use `cached` flag for source code volumes
- **Anonymous volumes**: Prevent node_modules/build artifacts from crossing container boundary
- **Native file watching**: Container-native file watching (no OneDrive polling)

#### Container Resource Management
- **Memory limits**: Set appropriate memory limits for development containers
- **CPU allocation**: Allow sufficient CPU for hot reload and build processes
- **Disk I/O optimization**: Use local Docker volumes for build artifacts

#### Hot Reload Performance
- **Container-native watching**: Leverage Linux inotify (faster than Windows file watching)
- **Optimized webpack config**: Container-specific webpack optimizations
- **Reduced polling**: No need for aggressive polling in container environment

### Error Handling Strategy

#### Container Health Monitoring
- **Health check endpoints**: Both services expose health check endpoints
- **Automatic restart**: `unless-stopped` policy for automatic recovery
- **Dependency management**: Proper service startup ordering

#### Development Error Recovery
- **Volume mount failures**: Clear error messages and recovery instructions
- **Port conflicts**: Automatic port detection and alternative suggestions
- **Container build failures**: Detailed build logs and troubleshooting guide

#### OneDrive Migration Errors
- **Repository detection**: Verify successful migration from OneDrive location
- **Permission issues**: Handle Windows file permission edge cases during migration
- **Symlink validation**: Ensure any remaining symlinks work correctly

### Migration Strategy

#### Phase 1: Repository Relocation
1. **Create target directory**: `C:\Development\pro-forma-analytics-tool`
2. **Stop existing services**: Kill current dev servers to release file locks
3. **Copy repository**: `xcopy /E /I /H` to preserve all files and attributes
4. **Verify migration**: Ensure all files copied correctly and no OneDrive sync conflicts
5. **Update git remotes**: Ensure git configuration intact after move

#### Phase 2: Docker Environment Setup
1. **Build development images**: `docker-compose build`
2. **Initialize volumes**: Create and test volume mounts
3. **Start services**: `docker-compose up -d`
4. **Verify functionality**: Test frontend, backend, and inter-service communication
5. **Performance validation**: Ensure hot reload and development features work

#### Phase 3: Workflow Validation
1. **Hot reload testing**: Verify code changes trigger appropriate reloads
2. **Database persistence**: Ensure data survives container restarts
3. **Port accessibility**: Confirm services accessible from host browser
4. **Development tool integration**: Test debugging, logging, etc.

### Testing Strategy

#### Development Environment Tests
- **Container build tests**: Verify both frontend and backend images build successfully
- **Service startup tests**: Ensure all services start in correct order
- **Health check tests**: Validate health check endpoints respond correctly
- **Volume mount tests**: Verify file changes propagate correctly

#### Integration Tests
- **Frontend → Backend communication**: API calls work correctly
- **Database persistence**: Data survives container recreation
- **Hot reload functionality**: Code changes trigger recompilation
- **Port forwarding**: Services accessible from host machine

#### Performance Tests
- **Startup time**: Measure `docker-compose up` to ready state
- **Hot reload speed**: Measure file change to browser reload time
- **Resource usage**: Monitor container CPU/memory consumption
- **Build performance**: Compare container vs native build times

#### OneDrive Isolation Tests
- **File lock elimination**: Verify zero EBUSY errors in container logs
- **Sync conflict prevention**: Ensure no OneDrive sync issues with relocated repo
- **Cross-environment consistency**: Test on OneDrive and non-OneDrive machines

### Documentation Requirements

#### Updated README.md
- **Docker prerequisites**: Docker Desktop installation requirements
- **Quick start guide**: Single-command setup instructions
- **Development workflow**: How to use containerized environment
- **Troubleshooting section**: Common issues and solutions

#### Developer Setup Guide
- **Migration instructions**: How to move existing development environment
- **IDE integration**: How to configure VS Code/other IDEs with containers
- **Debugging setup**: How to debug applications in containers
- **Performance tuning**: Container resource allocation recommendations

#### Architecture Documentation
- **Service overview**: Description of each container service
- **Volume strategy**: Explanation of volume mount approach
- **Network configuration**: How services communicate
- **Security considerations**: Development vs production differences

### Rollback Strategy

#### Immediate Rollback (if Docker setup fails)
1. **Return to OneDrive location**: Move repository back to original OneDrive path
2. **Restore native environment**: Use existing `npm run dev` commands
3. **Clean up Docker artifacts**: Remove created containers and images
4. **Document failures**: Record issues for future resolution

#### Partial Rollback (if only one service fails)
- **Frontend failure**: Keep backend containerized, run frontend natively
- **Backend failure**: Keep frontend containerized, run backend natively
- **Mixed environment**: Support hybrid container/native development temporarily

---

**Implementation Priority**: High (blocking critical development workflow)  
**Risk Level**: Medium (involves repository migration and new tooling)  
**Estimated Implementation Time**: 2-3 hours  
**Testing Time**: 1 hour  
**Documentation Time**: 30 minutes

**Next Phase**: Task implementation following this design specification