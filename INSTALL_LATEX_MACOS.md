# Install LaTeX Environment on macOS

This guide provides step-by-step instructions for installing LaTeX on the current macOS system for the Particle Physics Agent.

## Current System Status

Based on system check, LaTeX is not currently installed. This guide will install a complete LaTeX environment with TikZ-Feynman support.

## Installation Options

### Option 1: MacTeX (Complete Installation - Recommended)

MacTeX is the most comprehensive LaTeX distribution for macOS, including all packages needed.

```bash
# Install MacTeX via Homebrew Cask (easiest method)
brew install --cask mactex

# This will download and install ~4GB of LaTeX packages
# Installation may take 10-20 minutes depending on internet speed
```

**After installation, restart your terminal and verify:**
```bash
# Check if LaTeX is available
latex --version
pdflatex --version
lualatex --version

# Verify TikZ-Feynman is available
lualatex -interaction=nonstopmode <<< "\\documentclass{article}\\usepackage{tikz-feynman}\\begin{document}Test\\end{document}" && echo "TikZ-Feynman OK"
```

### Option 2: BasicTeX (Minimal Installation)

If disk space is a concern, use BasicTeX and install packages as needed:

```bash
# Install BasicTeX (smaller ~100MB base installation)
brew install --cask basictex

# Update PATH for current session
export PATH="/usr/local/texlive/2024basic/bin/universal-darwin:$PATH"

# Make PATH permanent
echo 'export PATH="/usr/local/texlive/2024basic/bin/universal-darwin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Update package manager
sudo tlmgr update --self

# Install required packages for Particle Physics Agent
sudo tlmgr install tikz-feynman
sudo tlmgr install amsmath amsfonts amssymb
sudo tlmgr install standalone
sudo tlmgr install xcolor
sudo tlmgr install luaotfload
sudo tlmgr install ifluatex ifxetex
sudo tlmgr install feynmf
sudo tlmgr install pgf
sudo tlmgr install tikz-cd
```

## Install Conversion Tools

The system needs tools to convert PDF output to SVG and PNG formats:

```bash
# Install PDF conversion tools
brew install pdf2svg        # For PDF to SVG conversion
brew install poppler        # For PDF to PNG conversion (pdftoppm)
brew install ghostscript    # Alternative conversion tool
brew install imagemagick    # Alternative conversion tool

# Verify conversion tools
pdf2svg --help
pdftoppm -h
gs --version
convert --version
```

## Verify Complete Installation

Create and run a comprehensive test:

```bash
# Create test directory
mkdir -p ~/latex_test
cd ~/latex_test

# Create test TikZ-Feynman document
cat > test_feynman.tex << 'EOF'
\documentclass[tikz,border=2pt]{standalone}
\usepackage{tikz}
\usepackage{tikz-feynman}
\usetikzlibrary{positioning}

\begin{document}
\begin{tikzpicture}
\begin{feynman}
\vertex (e1) at (0,1) {$e^-$};
\vertex (e2) at (4,1) {$e^+$};
\vertex (p1) at (0,-1) {$\gamma$};
\vertex (p2) at (4,-1) {$\gamma$};
\vertex (center) at (2,0);

\diagram* {
(e1) -- [fermion] (center) -- [anti fermion] (e2),
(center) -- [photon] (p1),
(center) -- [photon] (p2)
};
\end{feynman}
\end{tikzpicture}
\end{document}
EOF

# Compile with LuaLaTeX (required for tikz-feynman)
echo "Testing LaTeX compilation..."
lualatex test_feynman.tex

# Check if PDF was created
if [ -f test_feynman.pdf ]; then
    echo "✓ LaTeX compilation successful"
    
    # Test conversions
    echo "Testing format conversions..."
    
    # Test SVG conversion
    pdf2svg test_feynman.pdf test_feynman.svg && echo "✓ PDF to SVG conversion successful" || echo "✗ PDF to SVG conversion failed"
    
    # Test PNG conversion
    pdftoppm -png -singlefile -r 300 test_feynman.pdf test_feynman && echo "✓ PDF to PNG conversion successful" || echo "✗ PDF to PNG conversion failed"
    
    # Display results
    echo ""
    echo "Generated files:"
    ls -la test_feynman.*
    
else
    echo "✗ LaTeX compilation failed"
    echo "Error log:"
    cat test_feynman.log
fi

# Cleanup
cd ..
rm -rf ~/latex_test
```

## Integration with Particle Physics Agent

After successful installation, the application should automatically detect the LaTeX environment.

### Verify Application Integration

```bash
# Navigate to project directory
cd /Users/shawn-mac/Documents/agent/Particle-Physics-Agent-test

# Test the LaTeX compiler module
python3 -c "
import asyncio
from feynmancraft_adk.tools.latex_compiler import compile_tikz

async def test():
    result = await compile_tikz('''
\\begin{tikzpicture}
\\begin{feynman}
\\vertex (a) at (0,0) {\\(e^-\\)};
\\vertex (b) at (2,0) {\\(e^+\\)};
\\vertex (c) at (1,1) {\\(\\gamma\\)};
\\vertex (d) at (1,-1) {\\(\\gamma\\)};
\\diagram* {
  (a) -- [fermion] (b),
  (a) -- [photon] (c),
  (b) -- [photon] (d)
};
\\end{feynman}
\\end{tikzpicture}
    ''', output_formats=['pdf', 'svg', 'png'])
    
    print(f'Compilation success: {result.success}')
    if result.success:
        print(f'PDF path: {result.pdf_path}')
        print(f'SVG path: {result.svg_path}')
        print(f'PNG path: {result.png_path}')
    else:
        print(f'Errors: {[e.message for e in result.errors]}')

asyncio.run(test())
"
```

## Troubleshooting

### Common Installation Issues

#### 1. Permission Errors
```bash
# If you get permission errors with tlmgr
sudo chown -R $(whoami) /usr/local/texlive/2024basic/tlpkg/
```

#### 2. PATH Issues
```bash
# Verify LaTeX is in PATH
echo $PATH | grep texlive

# If not found, add to shell profile
echo 'export PATH="/usr/local/texlive/2024basic/bin/universal-darwin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

#### 3. Package Installation Failures
```bash
# Update package database
sudo tlmgr update --self --all

# Install packages individually if batch install fails
sudo tlmgr install tikz-feynman
sudo tlmgr install standalone
sudo tlmgr install amsmath
```

#### 4. Homebrew Installation Issues
```bash
# If Homebrew cask installation fails
brew update
brew cleanup
brew install --cask mactex --force
```

### Manual Installation (Alternative)

If Homebrew installation fails:

1. Visit [MacTeX Download](https://tug.org/mactex/mactex-download.html)
2. Download MacTeX.pkg (about 4GB)
3. Run the installer package
4. Restart terminal and verify installation

## Performance Tips

### Speed Up Compilation
```bash
# Create format file for faster subsequent compilations
sudo fmtutil-sys --all

# Use ramdisk for temporary files (optional)
# This creates a 512MB RAM disk for faster I/O
diskutil erasevolume HFS+ "LaTeXTemp" $(hdiutil attach -nomount ram://1048576)
export TMPDIR="/Volumes/LaTeXTemp"
```

### Reduce Disk Usage
If using BasicTeX and want to minimize package installation:
```bash
# Only install essential packages
sudo tlmgr install collection-basic
sudo tlmgr install tikz-feynman standalone
```

## Final Verification Script

Save this script as `verify_latex_setup.sh`:

```bash
#!/bin/bash
echo "=== LaTeX Environment Verification ==="
echo ""

# Check LaTeX engines
echo "1. LaTeX Engines:"
engines=("latex" "pdflatex" "lualatex" "xelatex")
for engine in "${engines[@]}"; do
    if command -v $engine >/dev/null 2>&1; then
        version=$($engine --version 2>&1 | head -1)
        echo "   ✓ $engine: $version"
    else
        echo "   ✗ $engine: not found"
    fi
done

echo ""
echo "2. Conversion Tools:"
tools=("pdf2svg" "pdftoppm" "gs" "convert")
for tool in "${tools[@]}"; do
    if command -v $tool >/dev/null 2>&1; then
        echo "   ✓ $tool: available"
    else
        echo "   ✗ $tool: not found"
    fi
done

echo ""
echo "3. TikZ-Feynman Test:"
tmpdir=$(mktemp -d)
cd "$tmpdir"

cat > test.tex << 'EOF'
\documentclass{standalone}
\usepackage{tikz}
\usepackage{tikz-feynman}
\begin{document}
\begin{tikzpicture}
\begin{feynman}
\vertex (a);
\vertex [right=of a] (b);
\diagram* { (a) -- [fermion] (b) };
\end{feynman}
\end{tikzpicture}
\end{document}
EOF

if lualatex -interaction=batchmode test.tex >/dev/null 2>&1; then
    echo "   ✓ TikZ-Feynman compilation successful"
    
    if pdf2svg test.pdf test.svg 2>/dev/null; then
        echo "   ✓ SVG conversion successful"
    fi
    
    if pdftoppm -png -singlefile test.pdf test 2>/dev/null; then
        echo "   ✓ PNG conversion successful" 
    fi
else
    echo "   ✗ TikZ-Feynman compilation failed"
fi

cd - >/dev/null
rm -rf "$tmpdir"

echo ""
echo "=== Verification Complete ==="
```

Run the verification:
```bash
chmod +x verify_latex_setup.sh
./verify_latex_setup.sh
```

## Next Steps

After successful installation:

1. Run the application: `./start.sh`
2. Test with a Feynman diagram request
3. Check that PDF, SVG, and PNG outputs are generated correctly

The system is now ready to generate TikZ Feynman diagrams with full LaTeX compilation support.