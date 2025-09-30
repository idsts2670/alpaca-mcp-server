# Publishing Guide: Alpaca MCP Server Registry Deployment

This guide provides step-by-step instructions for publishing the Alpaca MCP Server to all major MCP registries and platforms.

## Prerequisites

Before publishing to any registry, ensure you have completed the upgrade:

- [x] Modern package structure with `pyproject.toml`
- [x] CLI interface with `alpaca-mcp` commands
- [x] All 31 tools documented in manifest files
- [x] Registry metadata files created
- [x] Clean codebase without emojis in configuration files

## Registry Requirements Overview

| Registry | Primary Requirement | PyPI Required? |
|----------|-------------------|----------------|
| **Docker Hub MCP Registry** | Docker image + server.yaml | No |
| **Cursor Directory** | Install links + transport config | No |
| **GitHub MCP Registry** | Manifest endpoint | Optional |
| **Claude Connector** | HTTP server endpoint | No |
| **PyPI** | Python package | N/A |

**Note**: PyPI publication is optional and provides additional installation methods, but is not required for MCP registry listings.

## 1. PyPI Publication (Optional - Additional Distribution)

### Step 1.1: Prepare for PyPI Upload

```bash
# Install build tools
pip install build twine

# Create distribution packages
python -m build

# Verify the package
twine check dist/*
```

### Step 1.2: Upload to PyPI

```bash
# Upload to PyPI (you'll need PyPI account and API token)
twine upload dist/*
```

### Step 1.3: Verify Installation

```bash
# Test installation from PyPI
uvx alpaca-mcp-server --version
uvx alpaca-mcp-server init --help
```

## 2. Docker Hub MCP Registry

**URL**: https://hub.docker.com/mcp/server/dockerhub/overview
**Requirements**: `server.yaml` configuration file
**Approval Process**: Docker team review

### Step 2.1: Prepare Docker Image

Create `Dockerfile` in project root:

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml requirements.txt ./
COPY src/ ./src/
COPY alpaca_mcp_server.py ./

# Install Python dependencies
RUN pip install --no-cache-dir .

# Create non-root user
RUN useradd --create-home --shell /bin/bash alpaca
RUN chown -R alpaca:alpaca /app
USER alpaca

# Set environment variables
ENV PYTHONPATH=/app
ENV ALPACA_PAPER_TRADE=True

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import alpaca_mcp_server" || exit 1

# Default command
ENTRYPOINT ["python", "-m", "alpaca_mcp_server.cli"]
CMD ["serve"]
```

### Step 2.2: Build and Test Docker Image

```bash
# Build the image
docker build -t alpaca-mcp-server:latest .

# Test the image locally
docker run -e ALPACA_API_KEY=test -e ALPACA_SECRET_KEY=test alpaca-mcp-server:latest --help

# Test with actual credentials (optional)
docker run -e ALPACA_API_KEY=your_key -e ALPACA_SECRET_KEY=your_secret alpaca-mcp-server:latest serve
```

### Step 2.3: Submit to Docker MCP Registry

1. **Fork the repository**: https://github.com/docker/mcp-registry
2. **Add server configuration**:
   ```bash
   # Create directory structure
   mkdir -p servers/alpaca-mcp-server
   cp server.yaml servers/alpaca-mcp-server/
   ```
3. **Create pull request** with:
   - Title: "Add Alpaca MCP Server"
   - Description: Brief description of the 31 tools and capabilities
   - Reference: Link to your GitHub repository

### Step 2.4: Docker Registry Review Process

- **Automated checks**: Ensure all CI/CD tests pass
- **Security scan**: Docker will scan for vulnerabilities
- **Review timeline**: Typically 24-48 hours
- **Publication**: Available on Docker Hub after approval

## 3. Cursor MCP Directory with Deeplink

**URL**: https://cursor.directory/mcp/new
**Requirements**: Install links with transport configuration (no PyPI required)
**Target Audience**: 250K+ monthly active developers
**Documentation**: https://cursor.com/docs/context/mcp/install-links

### Step 3.1: Prepare Install Link Configuration

Cursor uses install links with transport configuration, not PyPI packages. Prepare:

**Option A: uvx-based installation (if PyPI package exists)**
```json
{
  "name": "Alpaca MCP Server",
  "command": "uvx",
  "args": ["alpaca-mcp-server", "serve"],
  "env": {
    "ALPACA_API_KEY": "",
    "ALPACA_SECRET_KEY": ""
  }
}
```

**Option B: Git-based installation (direct from GitHub)**
```json
{
  "name": "Alpaca MCP Server",
  "command": "uvx",
  "args": ["git+https://github.com/idsts2670/alpaca-mcp-server.git", "serve"],
  "env": {
    "ALPACA_API_KEY": "",
    "ALPACA_SECRET_KEY": ""
  }
}
```

**Option C: Local Python installation**
```json
{
  "name": "Alpaca MCP Server",
  "command": "python",
  "args": ["/path/to/alpaca_mcp_server.py"],
  "env": {
    "ALPACA_API_KEY": "",
    "ALPACA_SECRET_KEY": ""
  }
}
```

### Step 3.2: Create GitHub Issue

1. **Visit**: https://github.com/cursor-mcp/registry (or similar submission portal)
2. **Create new issue** with template:

```markdown
# MCP Server Submission: Alpaca MCP Server

## Basic Information
- **Name**: Alpaca MCP Server
- **Description**: Comprehensive Alpaca Trading API integration for Model Context Protocol with 31 specialized tools for natural language trading operations
- **Repository**: https://github.com/idsts2670/alpaca-mcp-server
- **Logo**: https://alpaca.markets/favicon.ico
- **License**: MIT

## Installation
```bash
uvx alpaca-mcp-server
```

## Configuration Example
```json
{
  "mcpServers": {
    "alpaca": {
      "command": "uvx",
      "args": ["alpaca-mcp-server", "serve"],
      "env": {
        "ALPACA_API_KEY": "your_api_key",
        "ALPACA_SECRET_KEY": "your_secret_key"
      }
    }
  }
}
```

## Features (31 Tools)
- Account & Portfolio Management (3 tools)
- Stock Market Data (6 tools)
- Cryptocurrency Trading (2 tools)
- Order Management (5 tools)
- Position Management (3 tools)
- Asset Discovery (2 tools)
- Watchlist Management (3 tools)
- Market Information (2 tools)
- Corporate Actions (1 tool)
- Options Trading (4 tools)

## Verification
- [x] Package published to PyPI
- [x] Installation works with uvx
- [x] All 31 tools tested and functional
- [x] Documentation complete
```

### Step 3.3: Test Deeplink Integration

After submission approval, test the deeplink:
```
cursor://anysphere.cursor-deeplink/mcp/install?package=alpaca-mcp-server
```

## 4. GitHub MCP Registry

**URL**: https://github.com/mcp
**Requirements**: Manifest endpoint and PyPI package
**Authentication**: GitHub OAuth or domain verification

### Step 4.1: Set Up Manifest Endpoint

Ensure your manifest is accessible at:
```
https://github.com/idsts2670/alpaca-mcp-server/.well-known/mcp/manifest.json
```

### Step 4.2: Install MCP Publisher CLI

```bash
# Install the official MCP publisher tool
npm install -g @anthropic-ai/mcp-publisher

# Or use uvx
uvx @anthropic-ai/mcp-publisher
```

### Step 4.3: Submit to GitHub MCP Registry

```bash
# Authenticate with GitHub
mcp-publisher auth login

# Validate your manifest
mcp-publisher validate https://github.com/idsts2670/alpaca-mcp-server/.well-known/mcp/manifest.json

# Submit to registry
mcp-publisher submit \
  --namespace "io.github.idsts2670" \
  --server-name "alpaca-mcp-server" \
  --manifest-url "https://github.com/idsts2670/alpaca-mcp-server/.well-known/mcp/manifest.json" \
  --pypi-package "alpaca-mcp-server"
```

### Step 4.4: Verify Registry Listing

1. **Check submission status**: `mcp-publisher status io.github.idsts2670/alpaca-mcp-server`
2. **Verify in registry**: Visit https://github.com/mcp to see your listing
3. **Test installation**: `uvx alpaca-mcp-server` should work from registry

## 5. Claude Connector Upload

**URL**: https://docs.claude.com/en/docs/agents-and-tools/mcp-connector
**Requirements**: Hosted MCP server endpoint
**Authentication**: Claude account

### Step 5.1: Deploy Server to Cloud (Optional)

For Claude Connector, you can either:
1. **Use existing installation** (uvx/pip on user's machine)
2. **Deploy hosted endpoint** (for remote access)

#### Option A: Hosted Deployment Example (Railway/Heroku)

Create `Procfile`:
```
web: alpaca-mcp serve --transport http --host 0.0.0.0 --port $PORT
```

Create `runtime.txt`:
```
python-3.11.14
```

Deploy to hosting platform with environment variables:
- `ALPACA_API_KEY`
- `ALPACA_SECRET_KEY`
- `ALPACA_PAPER_TRADE=true`

### Step 5.2: Configure Claude Connector

1. **Log in to Claude**: https://claude.ai
2. **Navigate to Connectors**: Settings → MCP Connectors
3. **Add Custom Connector**:

#### For Local Installation:
```json
{
  "name": "Alpaca Trading",
  "command": "uvx",
  "args": ["alpaca-mcp-server", "serve"],
  "env": {
    "ALPACA_API_KEY": "your_api_key",
    "ALPACA_SECRET_KEY": "your_secret_key"
  }
}
```

#### For Remote Server:
```json
{
  "name": "Alpaca Trading",
  "transport": "http",
  "url": "https://your-server.herokuapp.com/mcp",
  "auth": {
    "type": "bearer",
    "token": "your_auth_token"
  }
}
```

### Step 5.3: Test Connection

1. **Verify tools loading**: Check that all 31 tools appear in Claude
2. **Test functionality**: Try commands like "What's my account balance?"
3. **Verify permissions**: Ensure proper API key access

## 6. Post-Publication Checklist

After publishing to all registries:

### Step 6.1: Update Documentation

- [ ] Update README.md with registry installation instructions
- [ ] Add badges for each registry
- [ ] Update UPGRADE_SUMMARY.md with publication status

### Step 6.2: Test All Installation Methods

```bash
# Test uvx installation
uvx alpaca-mcp-server init

# Test pip installation
pip install alpaca-mcp-server

# Test Docker installation
docker run alpaca/mcp-server

# Test registry links
curl https://github.com/idsts2670/alpaca-mcp-server/.well-known/mcp/manifest.json
```

### Step 6.3: Monitor and Maintain

- [ ] Monitor registry approval status
- [ ] Respond to user feedback and issues
- [ ] Update versions across all registries when releasing updates
- [ ] Maintain compatibility with MCP specification updates

## 7. Troubleshooting Common Issues

### PyPI Upload Issues
```bash
# Clear dist folder and rebuild
rm -rf dist/
python -m build
twine check dist/*
```

### Docker Build Issues
```bash
# Build with verbose output
docker build --no-cache --progress=plain -t alpaca-mcp-server .

# Check container logs
docker run alpaca-mcp-server logs
```

### Registry Submission Issues
- **Manifest validation fails**: Check JSON syntax and required fields
- **Package not found**: Ensure PyPI publication completed successfully
- **Authentication errors**: Verify GitHub OAuth tokens and permissions

## 8. Expected Timeline

| Registry | Submission Time | Review Time | Total Time |
|----------|----------------|-------------|------------|
| PyPI | 10 minutes | Immediate | 10 minutes |
| Docker Hub | 30 minutes | 24-48 hours | 1-2 days |
| Cursor Directory | 15 minutes | 1-7 days | 1-7 days |
| GitHub MCP Registry | 20 minutes | 1-3 days | 1-3 days |
| Claude Connector | 5 minutes | Immediate | 5 minutes |

## 9. Success Metrics

After successful publication, you should see:

- **PyPI**: Package installable via `pip install alpaca-mcp-server`
- **Docker Hub**: Image pullable via `docker pull alpaca/mcp-server`
- **Cursor Directory**: Listed in https://cursor.directory/mcp with working deeplink
- **GitHub MCP Registry**: Discoverable at https://github.com/mcp
- **Claude Connector**: Available in Claude's MCP connector settings

## 10. Maintenance and Updates

### Version Updates
1. Update `pyproject.toml` version
2. Rebuild and upload to PyPI
3. Rebuild Docker image with new tag
4. Update registry listings with new version
5. Test all installation methods

### Registry-Specific Updates
- **PyPI**: Automatic with package updates
- **Docker**: Rebuild and push new image tags
- **Cursor**: May require resubmission for major changes
- **GitHub MCP**: Update manifest.json and resubmit
- **Claude**: Update connector configuration if needed

This completes the comprehensive publishing guide for all major MCP registries and platforms.