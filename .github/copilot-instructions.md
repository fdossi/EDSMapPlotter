# EDSMapPlotter - AI Coding Agent Instructions

## Project Overview
EDSMapPlotter is a Python tool that converts raw EDS (Energy Dispersive Spectroscopy) microscopy data into publication-quality heatmap images. It exists in two implementations: a desktop GUI (Windows/Linux/Mac) and a Google Colab notebook for cloud-based processing.

## Core Architecture

### Dual-Implementation Pattern
- **EDSMapPlotter.py**: Desktop GUI with tkinter, supporting drag-and-drop file handling
- **EDSMapPlotter_Colab.ipynb**: Google Colab notebook version using `google.colab.files` for uploads
- **Shared Logic**: Both use the `gerar_eds_map()` function (core processing) - changes must be synchronized across implementations

### Data Flow
1. User provides CSV files (raw numeric matrices from SEM software, no headers)
2. `gerar_eds_map()` reads CSV → validates → extracts element name from filename → generates heatmap
3. Output: 300 DPI PNG with colorbar, element-specific title
4. Filename parsing: `Area1_Fe.csv` → `Area1_edsmap_Fe.png` (element extracted from suffix after `_`)

## Critical Patterns & Conventions

### Filename-Based Element Detection
```python
parts = n0.split("_")
if len(parts) > 1:
    elemento = parts[-1]  # Always take LAST segment after splitting by "_"
    prefix = "_".join(parts[:-1])
    out_name = f"{prefix}_edsmap_{elemento}.png"
```
This is NOT configurable - element detection depends on filename format. Preserve this logic when modifying.

### Resource Path Handling
```python
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # PyInstaller bundled executable
    except Exception:
        base_path = os.path.abspath(".")  # Development mode
    return os.path.join(base_path, relative_path)
```
Used for icon loading. Images (PNG/ICO) must be in workspace root for PyInstaller builds.

### Optional Dependencies
- `tkinterdnd2` for drag-and-drop: gracefully disabled if missing (shows messagebox warning)
- DPI awareness on Windows via `ctypes.windll.shcore.SetProcessDpiAwareness(1)` for clarity
- When modifying imports, ensure try/except blocks preserve functionality

### Plotting Configuration (Fixed)
- Figure size: 8x8 inches, 300 DPI
- Colormap: matplotlib standard options (viridis, magma, Blues, Reds, etc.)
- Title format: `"EDS-Map - {element}"` with 26pt font
- Colorbar label: "Intensidade" (Portuguese - language-specific)
- Memory management: Always `plt.close(fig)` after save to prevent memory leaks

## GUI-Specific Implementation Details

### Tkinter Event Handling
- Uses `root.update()` during processing to keep UI responsive
- Status messages use color coding: info (#0056b3), warning (#e67e22), success (#28a745), error (#dc3545)
- Drag-and-drop paths may arrive wrapped in curly braces on Windows: `p.strip("{}")`
- TkinterDnD path parsing uses `root.tk.splitlist()` for robust multi-file handling

### Data Validation Pattern
```python
df = pd.read_csv(caminho_csv, header=None)
df_numeric = df.apply(pd.to_numeric, errors="coerce")
data = df_numeric.to_numpy(dtype=float)
if data.size == 0 or np.all(np.isnan(data)):
    return False  # Silent failure, logged to console
```
Empty or all-NaN data is silently skipped (not a hard error).

## Development Workflows

### Testing CSV Inputs
Use numeric-only CSV files (no headers). Example:
```
0.1,0.2,0.3
0.4,0.5,0.6
0.7,0.8,0.9
```

### Building Executable (PyInstaller)
Assets required in root: `EDSMapPlotter_icon.png`, `EDSMapPlotter_icon.ico`
The `resource_path()` function enables bundling these into `.exe`

### Colab Deployment
Colab version differs: uses `google.colab.files` instead of tkinter, direct file download output
Keep `gerar_eds_map()` core logic synchronized between both versions

## Language & Localization Notes
- UI messages in Portuguese (pt-BR): "Arquivos CSV Selecionados", "Salvar Imagens em", etc.
- Colorbar label hardcoded as "Intensidade"
- Project maintains separate README.md (Portuguese) and README_en.md (English)
- When translating, preserve Portuguese style in messages

## Known Issues & Edge Cases
- Drag-and-drop on Windows sometimes wraps paths in curly braces (handled by `strip("{}")`)
- tkinterdnd2 not available on all systems (non-blocking, fallback to button)
- Memory leaks possible if `plt.close()` is omitted in batch processing
- CSV parsing permissive: coerces invalid numbers to NaN, silently skips files with all-NaN data

## Key Dependencies
- **pandas**: CSV reading with permissive numeric coercion
- **numpy**: Array operations, NaN detection
- **matplotlib**: Plotting, 300 DPI export, colormaps
- **tkinter**: Built-in GUI framework
- **tkinterdnd2** (optional): Drag-and-drop feature
- **Pillow**: Icon image handling (PNG↔ICO)
