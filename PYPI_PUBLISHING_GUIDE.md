# PyPI Publishing Guide for Alpaca MCP Server

This guide walks you through publishing the uvx-rebuilt Alpaca MCP Server to PyPI (Python Package Index), making it available for easy installation via `uvx alpaca-mcp`.

## Prerequisites

### 1. PyPI Account Setup
1. **Create PyPI Account:** Go to [https://pypi.org/account/register/](https://pypi.org/account/register/)
2. **Verify Email:** Check your email and verify your account
3. **Enable 2FA:** Highly recommended for security
4. **Create API Token:**
   - Go to [https://pypi.org/manage/account/token/](https://pypi.org/manage/account/token/)
   - Click "Add API token"
   - Scope: "Entire account" (for first time) or "Project: alpaca-mcp" (if project exists)
   - Copy the token (starts with `pypi-`)

### 2. Install Publishing Tools
```bash
# Install required tools
pip install build twine

# Or with uv
uv tool install build
uv tool install twine
```

## Step-by-Step Publishing Process

### Step 1: Prepare the Package

**Check Current Version:**
```bash
# Current version in pyproject.toml
grep "version" pyproject.toml
# Output: version = "0.1.0"
```

**Update Version (if needed):**
```bash
# Edit pyproject.toml and bump version
# version = "0.1.0" → "0.1.1" or "0.2.0"
```

**Verify Package Metadata:**
```bash
# Check that all required fields are present
cat pyproject.toml
```

### Step 2: Build the Package

```bash
# Clean any previous builds
rm -rf dist/ build/ *.egg-info/

# Build the package
python -m build

# Or with uv
uv build
```

**Expected Output:**
```
dist/
├── alpaca_mcp-0.1.0-py3-none-any.whl    # Wheel file (preferred)
└── alpaca_mcp-0.1.0.tar.gz               # Source distribution
```

### Step 3: Test the Build (Optional but Recommended)

```bash
# Install locally to test
pip install dist/alpaca_mcp-0.1.0-py3-none-any.whl

# Test the CLI
alpaca-mcp --help
alpaca-mcp init --help
alpaca-mcp serve --help

# Uninstall after testing
pip uninstall alpaca-mcp
```

### Step 4: Upload to PyPI

#### Option A: Using API Token (Recommended)
```bash
# Upload using twine with API token
python -m twine upload dist/* --username __token__ --password pypi-YOUR_API_TOKEN_HERE

# Or interactively (will prompt for token)
python -m twine upload dist/*
# Username: __token__
# Password: [paste your API token]
```

#### Option B: Using .pypirc File (Alternative)
```bash
# Create ~/.pypirc file
cat > ~/.pypirc << 'EOF'
[distutils]
index-servers = pypi

[pypi]
username = __token__
password = pypi-YOUR_API_TOKEN_HERE
EOF

# Set secure permissions
chmod 600 ~/.pypirc

# Upload
python -m twine upload dist/*
```

### Step 5: Verify Publication

1. **Check PyPI:** Visit [https://pypi.org/project/alpaca-mcp/](https://pypi.org/project/alpaca-mcp/)
2. **Test Installation:**
   ```bash
   # Test uvx installation
   uvx alpaca-mcp --help

   # Test pip installation
   pip install alpaca-mcp
   alpaca-mcp --help
   ```

## Publication Workflow

### For Regular Updates:

```bash
# 1. Update version in pyproject.toml
sed -i 's/version = "0.1.0"/version = "0.1.1"/' pyproject.toml

# 2. Build and upload
python -m build
python -m twine upload dist/*

# 3. Clean up
rm -rf dist/ build/
```

### For Major Releases:

```bash
# 1. Update version (e.g., 0.1.0 → 1.0.0)
# 2. Update CHANGELOG.md (if you create one)
# 3. Create Git tag
git tag v1.0.0
git push origin v1.0.0

# 4. Build and upload
python -m build
python -m twine upload dist/*
```

## Automated Publishing with GitHub Actions

You can automate PyPI publishing using GitHub Actions. Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine

    - name: Build package
      run: python -m build

    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

**Setup:**
1. Add your PyPI API token to GitHub Secrets as `PYPI_API_TOKEN`
2. Create a GitHub release with a tag (e.g., `v0.1.0`)
3. The action will automatically build and publish

## How uvx Resolution Works

### Without PyPI (Current):
```bash
# uvx fetches from GitHub
uvx --from git+https://github.com/alpacahq/alpaca-mcp-server.git alpaca-mcp
```

### With PyPI (After Publishing):
```bash
# uvx fetches from PyPI (much faster)
uvx alpaca-mcp
```

### Resolution Order:
1. **PyPI** (fastest) - if package exists
2. **Git repository** (fallback) - if PyPI fails
3. **Local path** - for development

## Version Management Best Practices

### Semantic Versioning:
- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **MAJOR:** Breaking changes
- **MINOR:** New features (backwards compatible)
- **PATCH:** Bug fixes

### Version Bumping:
```bash
# Bug fix: 0.1.0 → 0.1.1
# New feature: 0.1.1 → 0.2.0
# Breaking change: 0.2.0 → 1.0.0
```

## Troubleshooting

### Common Issues:

1. **Package Name Already Exists:**
   ```
   Error: The name 'alpaca-mcp' is already in use
   ```
   **Solution:** Change the name in pyproject.toml to something unique

2. **Authentication Failed:**
   ```
   Error: 403 Forbidden
   ```
   **Solution:** Check your API token and username (__token__)

3. **Version Already Exists:**
   ```
   Error: File already exists
   ```
   **Solution:** Bump version number in pyproject.toml

4. **Missing Required Metadata:**
   ```
   Error: Missing required metadata
   ```
   **Solution:** Add missing fields to pyproject.toml (description, license, etc.)

### Debugging Commands:
```bash
# Check package metadata
python -m twine check dist/*

# Test upload to TestPyPI first
python -m twine upload --repository testpypi dist/*
```

## Security Considerations

1. **Never commit API tokens** to version control
2. **Use API tokens** instead of username/password
3. **Set token scope** to specific projects when possible
4. **Rotate tokens regularly**
5. **Enable 2FA** on your PyPI account

## Benefits After Publishing

### For Users:
- **Faster installation:** `uvx alpaca-mcp` (no Git clone)
- **Automatic updates:** uvx can detect new versions
- **Better caching:** PyPI packages are cached by uvx
- **Dependency resolution:** pip/uv can resolve conflicts better

### For Developers:
- **Distribution metrics:** Download statistics on PyPI
- **Professional appearance:** Listed on official Python package index
- **Integration compatibility:** Works with all Python package managers
- **Automated tooling:** CI/CD can reference published versions

This guide provides everything needed to publish the rebuilt Alpaca MCP Server to PyPI, making it easily accessible via the modern uvx workflow.