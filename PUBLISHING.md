# Publishing EDSMapPlotter to PyPI

## Prerequisites

1. Install build tools:
```bash
pip install build twine
```

2. Create PyPI account at https://pypi.org/account/register/
3. Create TestPyPI account at https://test.pypi.org/account/register/

## Build the Package

From the project root directory:

```bash
# Clean previous builds
Remove-Item -Recurse -Force dist, build, *.egg-info -ErrorAction SilentlyContinue

# Build the package
python -m build
```

This creates:
- `dist/edsmapplotter-0.2.1.tar.gz` (source distribution)
- `dist/edsmapplotter-0.2.1-py3-none-any.whl` (wheel distribution)

## Test on TestPyPI First

```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ edsmapplotter

# Test the package
edsmapplotter
```

## Publish to PyPI (Production)

Once tested successfully:

```bash
# Upload to PyPI
twine upload dist/*
```

You'll be prompted for your PyPI credentials.

## Post-Publication

Users can now install via:
```bash
pip install edsmapplotter
```

And run:
```bash
edsmapplotter
```

Or import in Python:
```python
from edsmapplotter import gerar_eds_map, run_gui

# Use programmatically
gerar_eds_map("data.csv", "output/", cmap_name="viridis")

# Or launch GUI
run_gui()
```

## API Token (Recommended)

For automated uploads, use API tokens:

1. Go to https://pypi.org/manage/account/token/
2. Create a new API token
3. Save credentials in `~/.pypirc`:

```ini
[pypi]
username = __token__
password = pypi-YOUR-TOKEN-HERE

[testpypi]
username = __token__
password = pypi-YOUR-TESTPYPI-TOKEN-HERE
```

Then upload with:
```bash
twine upload dist/*
```
