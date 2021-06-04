#!/usr/bin/env python3
from pathlib import Path
from subprocess import run


def run_this_script():
    main_path = Path(__file__).parent
    tex_file = Path('FILE').with_suffix('.tex')
    for command in ['pdflatex', 'bibtex'] + (['pdflatex'] * 2):
        run([command, str(tex_file)])
    run(['okular', tex_file.with_suffix('.pdf')])
    for file in [f for f in main_path.iterdir() if
                 f.stem == 'FILE' and f.suffix.strip().lstrip('.').lower() not in {'pdf', 'tex'}]:
        file.unlink()


if __name__ == '__main__':
    run_this_script()
