"""Automated test validating paper LaTeX syntax and citations."""
from pathlib import Path
from tools.check_latex import validate_bib, validate_tex


def test_latex_paper_structure_and_citations():
    root = Path(__file__).resolve().parents[1]
    paper_dir = root / 'paper'
    tex_path = paper_dir / 'crosswire_formal_synthesis.tex'
    bib_path = paper_dir / 'references.bib'

    assert tex_path.exists(), f"Missing LaTeX paper at {tex_path}"
    assert bib_path.exists(), f"Missing bibliography at {bib_path}"

    bib_keys = validate_bib(bib_path)
    validate_tex(tex_path, bib_keys)
