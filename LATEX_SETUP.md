# LaTeX Environment Setup Guide

This guide provides comprehensive instructions for setting up the LaTeX compilation environment required by the Particle Physics Agent system.

## Overview

The system supports two LaTeX compilation modes:
- **Local Mode**: Direct compilation using local LaTeX installation
- **MCP Mode**: Remote compilation via LaTeX MCP server

Both modes require a properly configured LaTeX environment with TikZ-Feynman support.

## System Requirements

### Operating System Support
- **macOS**: 10.14+ (Mojave or later)
- **Linux**: Ubuntu 18.04+, CentOS 7+, Debian 9+
- **Windows**: Windows 10+ (with WSL2 recommended)

### Hardware Requirements
- **RAM**: Minimum 2GB, recommended 4GB+
- **Storage**: 3-5GB for full LaTeX installation
- **CPU**: Any modern x64 processor

## LaTeX Installation

### macOS Installation

#### Option 1: MacTeX (Recommended)
```bash
# Download and install MacTeX (3.9GB)
# Visit: https://tug.org/mactex/mactex-download.html
# Or use Homebrew:
brew install --cask mactex

# Add LaTeX to PATH (if not automatically done)
export PATH="/usr/local/texlive/2024/bin/universal-darwin:$PATH"

# Verify installation
latex --version
pdflatex --version
```

#### Option 2: BasicTeX (Minimal Installation)
```bash
# Install BasicTeX (much smaller ~100MB)
brew install --cask basictex

# Update PATH
export PATH="/usr/local/texlive/2024basic/bin/universal-darwin:$PATH"
sudo tlmgr update --self

# Install required packages
sudo tlmgr install tikz-feynman
sudo tlmgr install feynmf
sudo tlmgr install amsmath amsfonts amssymb
sudo tlmgr install standalone
sudo tlmgr install xcolor
sudo tlmgr install luaotfload
sudo tlmgr install ifluatex ifxetex
```

### Linux Installation

#### Ubuntu/Debian
```bash
# Update package list
sudo apt update

# Install TeX Live and required packages
sudo apt install -y texlive-latex-base texlive-latex-extra texlive-pictures
sudo apt install -y texlive-fonts-recommended texlive-fonts-extra
sudo apt install -y texlive-luatex texlive-xetex

# Install TikZ-Feynman specifically
sudo apt install -y texlive-science

# Install conversion tools
sudo apt install -y pdf2svg poppler-utils ghostscript

# Verify installation
latex --version
pdflatex --version
lualatex --version
```

#### CentOS/RHEL/Fedora
```bash
# For CentOS/RHEL with EPEL
sudo yum install -y epel-release
sudo yum install -y texlive texlive-latex texlive-latex-extra
sudo yum install -y texlive-tikz-feynman texlive-standalone

# For Fedora
sudo dnf install -y texlive-scheme-medium
sudo dnf install -y texlive-tikz-feynman texlive-standalone

# Install conversion tools
sudo yum install -y pdf2svg poppler-utils ghostscript
# or for Fedora: sudo dnf install -y pdf2svg poppler-utils ghostscript
```

### Windows Installation

#### Option 1: MiKTeX (Recommended for Windows)
```powershell
# Download and install MiKTeX
# Visit: https://miktex.org/download

# Install required packages via MiKTeX Console or command line
mpm --install tikz-feynman
mpm --install standalone
mpm --install amsmath
mpm --install amsfonts
mpm --install amssymb
```

#### Option 2: TeX Live on Windows
```powershell
# Download TeX Live installer
# Visit: https://tug.org/texlive/windows.html
# Run install-tl-windows.exe

# Install conversion tools (requires additional setup)
# Install ImageMagick or Ghostscript separately
```

## TikZ-Feynman Package Installation

### Verify TikZ-Feynman Installation
```bash
# Test basic LaTeX compilation
cat > test_tikz.tex << 'EOF'
\documentclass{standalone}
\usepackage{tikz}
\usepackage{tikz-feynman}
\begin{document}
\begin{tikzpicture}
\begin{feynman}
\vertex (a);
\vertex [right=of a] (b);
\diagram* {
(a) -- [fermion] (b)
};
\end{feynman}
\end{tikzpicture}
\end{document}
EOF

# Compile with LuaLaTeX (required for tikz-feynman)
lualatex test_tikz.tex

# If successful, test_tikz.pdf should be created
ls -la test_tikz.pdf
```

### Manual TikZ-Feynman Installation
If automatic installation fails:

```bash
# Download tikz-feynman from CTAN
wget https://mirrors.ctan.org/graphics/pgf/contrib/tikz-feynman.zip
unzip tikz-feynman.zip

# Find your local texmf directory
kpsewhich -var-value TEXMFHOME

# Install manually (replace path as needed)
mkdir -p ~/texmf/tex/latex/tikz-feynman
cp -r tikz-feynman/* ~/texmf/tex/latex/tikz-feynman/

# Update LaTeX database
sudo texhash
# or for user installation: texhash ~/texmf
```

## Conversion Tools Installation

The system supports multiple output formats (PDF, SVG, PNG). Install conversion tools based on your needs.

### PDF to SVG Conversion
```bash
# Option 1: dvisvgm (usually included with LaTeX)
dvisvgm --version

# Option 2: pdf2svg
# macOS
brew install pdf2svg

# Ubuntu/Debian
sudo apt install -y pdf2svg

# CentOS/RHEL
sudo yum install -y pdf2svg

# Option 3: Inkscape (more features but heavier)
# macOS
brew install --cask inkscape

# Ubuntu/Debian
sudo apt install -y inkscape
```

### PDF to PNG Conversion
```bash
# Option 1: pdftoppm (part of poppler-utils)
# macOS
brew install poppler

# Ubuntu/Debian  
sudo apt install -y poppler-utils

# CentOS/RHEL
sudo yum install -y poppler-utils

# Option 2: ImageMagick convert
# macOS
brew install imagemagick

# Ubuntu/Debian
sudo apt install -y imagemagick

# Option 3: Ghostscript
# macOS
brew install ghostscript

# Ubuntu/Debian
sudo apt install -y ghostscript
```

## Environment Configuration

### Environment Variables
Add these to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):

```bash
# LaTeX PATH configuration
export PATH="/usr/local/texlive/2024/bin/x86_64-linux:$PATH"  # Linux
export PATH="/usr/local/texlive/2024/bin/universal-darwin:$PATH"  # macOS

# Set TEXMF paths if needed
export TEXMFHOME="$HOME/texmf"

# Optional: Set compilation timeout
export LATEX_COMPILE_TIMEOUT=30
```

### Python Environment Variables
```bash
# In your .env file
LATEX_COMPILE_ENGINE=pdflatex  # or lualatex
LATEX_COMPILE_TIMEOUT=30
LATEX_OUTPUT_FORMATS=pdf,svg,png
```

## Verification and Testing

### System Check Script
Create a verification script:

```bash
#!/bin/bash
# save as check_latex_env.sh

echo "Checking LaTeX Environment..."

# Check LaTeX engines
echo "1. Checking LaTeX engines:"
latex --version >/dev/null 2>&1 && echo "  ✓ latex" || echo "  ✗ latex"
pdflatex --version >/dev/null 2>&1 && echo "  ✓ pdflatex" || echo "  ✗ pdflatex"
lualatex --version >/dev/null 2>&1 && echo "  ✓ lualatex" || echo "  ✗ lualatex"

# Check conversion tools
echo "2. Checking conversion tools:"
pdf2svg >/dev/null 2>&1 && echo "  ✓ pdf2svg" || echo "  ✗ pdf2svg"
pdftoppm -h >/dev/null 2>&1 && echo "  ✓ pdftoppm" || echo "  ✗ pdftoppm"
convert -version >/dev/null 2>&1 && echo "  ✓ imagemagick" || echo "  ✗ imagemagick"
gs --version >/dev/null 2>&1 && echo "  ✓ ghostscript" || echo "  ✗ ghostscript"

# Test TikZ-Feynman compilation
echo "3. Testing TikZ-Feynman compilation:"
cat > /tmp/test_feynman.tex << 'EOF'
\documentclass[tikz,border=2pt]{standalone}
\usepackage{tikz}
\usepackage{tikz-feynman}
\begin{document}
\begin{tikzpicture}
\begin{feynman}
\vertex (e1) {$e^-$};
\vertex [right=2cm of e1] (e2) {$e^+$};
\vertex [below=1cm of e1] (p1) {$\gamma$};
\vertex [below=1cm of e2] (p2) {$\gamma$};
\diagram* {
(e1) -- [fermion] (e2),
(e1) -- [photon] (p1),
(e2) -- [photon] (p2)
};
\end{feynman}
\end{tikzpicture}
\end{document}
EOF

cd /tmp
lualatex test_feynman.tex >/dev/null 2>&1
if [ -f test_feynman.pdf ]; then
    echo "  ✓ TikZ-Feynman compilation successful"
    # Test conversion
    pdf2svg test_feynman.pdf test_feynman.svg 2>/dev/null && echo "  ✓ PDF to SVG conversion" || echo "  ✗ PDF to SVG conversion"
    pdftoppm -png -singlefile test_feynman.pdf test_feynman 2>/dev/null && echo "  ✓ PDF to PNG conversion" || echo "  ✗ PDF to PNG conversion"
else
    echo "  ✗ TikZ-Feynman compilation failed"
fi

echo "Environment check complete!"
```

Run the verification:
```bash
chmod +x check_latex_env.sh
./check_latex_env.sh
```

## Application Integration

### Local Compilation Mode
The system automatically uses local LaTeX if available:

```python
# In feynmancraft_adk/tools/latex_compiler.py
result = await compile_tikz(
    tikz_code="\\begin{tikzpicture}...\\end{tikzpicture}",
    output_formats=["pdf", "svg", "png"]
)
```

### MCP Remote Compilation Mode
Configure for remote compilation:

```bash
# In .env file
LATEX_MCP_ENABLED=true
LATEX_MCP_URL=http://localhost:8003
```

## Troubleshooting

### Common Issues

#### 1. tikz-feynman not found
```bash
# Solution: Install manually or update package database
sudo tlmgr update --self
sudo tlmgr install tikz-feynman
```

#### 2. luatex not available
```bash
# Solution: Install LuaTeX
# Ubuntu/Debian
sudo apt install texlive-luatex

# macOS
# Should be included with MacTeX
```

#### 3. Conversion tools failing
```bash
# Check tool availability
which pdf2svg
which pdftoppm

# Install missing tools (see installation sections above)
```

#### 4. Permission errors
```bash
# Fix permissions for local texmf
chmod -R 755 ~/texmf
texhash ~/texmf
```

#### 5. Memory issues during compilation
```bash
# Increase memory limits
export max_print_line=1000
export error_line=254
export half_error_line=127
```

### Advanced Configuration

#### Custom LaTeX Packages
```bash
# Add custom packages to local texmf
mkdir -p ~/texmf/tex/latex/local
# Copy .sty files to ~/texmf/tex/latex/local/
texhash ~/texmf
```

#### Performance Optimization
```bash
# Precompile frequently used packages
pdflatex -ini -jobname="preamble" "&pdflatex preamble.tex\\dump"
```

## Docker Environment

For containerized deployments:

```dockerfile
# Dockerfile snippet for LaTeX environment
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \\
    texlive-latex-base \\
    texlive-latex-extra \\
    texlive-pictures \\
    texlive-science \\
    texlive-luatex \\
    pdf2svg \\
    poppler-utils \\
    ghostscript \\
    && rm -rf /var/lib/apt/lists/*

# Verify installation
RUN lualatex --version && pdf2svg --version
```

## Support and Resources

### Documentation
- [TikZ-Feynman Manual](http://mirrors.ctan.org/graphics/pgf/contrib/tikz-feynman/tikz-feynman.pdf)
- [TikZ Manual](http://mirrors.ctan.org/graphics/pgf/base/doc/pgfmanual.pdf)
- [LaTeX Project](https://www.latex-project.org/)

### Community
- [TeX Stack Exchange](https://tex.stackexchange.com/)
- [TikZ-Feynman GitHub](https://github.com/JP-Ellis/tikz-feynman)

### Getting Help
If you encounter issues:
1. Check this troubleshooting guide
2. Verify your LaTeX installation with the check script
3. Consult the application logs for specific error messages
4. Report issues with complete system information and error logs