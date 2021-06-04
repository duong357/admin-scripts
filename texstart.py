#!/usr/bin/env python3
import sys
from pathlib import Path
from shutil import copytree

from bash_tools import sed_replace

args = sys.argv[1:]
if len(args) != 2:
    print("Need two arguments, the document name and the document class {book, report, article, letter, slides}")
    exit(1)

current_dir = Path(__file__).parent
stock_latex_dir = current_dir.joinpath('stock', 'latex')
new_dir = current_dir.joinpath(args[0])

copytree(stock_latex_dir, new_dir)

preview_file = new_dir.joinpath('preview.py')
sed_replace('FILE', args[0], [preview_file])
preview_file.chmod(0o700)

stock_tex_file = new_dir.joinpath('stock.tex')
tex_to_replace = {'TITLE': args[0], 'AUTHOR': 'Heinz Jung', 'SOMECLASS': args[1]}
for key in tex_to_replace:
    sed_replace(key, tex_to_replace[key], [stock_tex_file])
new_tex_file = stock_tex_file.parent.joinpath(args[0]).with_suffix(stock_tex_file.suffix)
stock_tex_file.rename(new_tex_file)

