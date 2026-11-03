"""LaTeX syntax, citation, and environment validator for CROSSWIRE papers."""
from __future__ import annotations

import re
import sys
from pathlib import Path


def validate_bib(bib_path: Path) -> set[str]:
    text = bib_path.read_text(encoding='utf-8')
    pattern = re.compile(r'@\w+\s*\{\s*([a-zA-Z0-9_-]+)\s*,')
    keys = set(pattern.findall(text))
    if not keys:
        raise ValueError(f"No citation keys found in {bib_path}")
    print(f"Loaded {len(keys)} citation keys from {bib_path.name}")
    return keys


def validate_tex(tex_path: Path, valid_bib_keys: set[str]):
    text = tex_path.read_text(encoding='utf-8')

    # Remove comments
    lines = []
    for line in text.splitlines():
        # Strip comments not preceded by backslash
        cleaned = re.sub(r'(?<!\\)%.*$', '', line)
        lines.append(cleaned)
    clean_text = '\n'.join(lines)

    # Check balanced braces
    stack = []
    for i, char in enumerate(clean_text):
        if char == '{':
            stack.append(i)
        elif char == '}':
            if not stack:
                raise ValueError(f"Unmatched closing brace '}}' at character offset {i}")
            stack.pop()
    if stack:
        raise ValueError(f"{len(stack)} unclosed opening brace(s) '{{' in {tex_path.name}")

    # Check environments
    begin_pattern = re.compile(r'\\begin\{([a-zA-Z0-9_*]+)\}')
    end_pattern = re.compile(r'\\end\{([a-zA-Z0-9_*]+)\}')

    env_stack = []
    for match in re.finditer(r'\\(begin|end)\{([a-zA-Z0-9_*]+)\}', clean_text):
        kind, env = match.groups()
        if kind == 'begin':
            env_stack.append((env, match.start()))
        else:
            if not env_stack:
                raise ValueError(f"Unexpected \\end{{{env}}} with no matching \\begin")
            prev_env, _ = env_stack.pop()
            if prev_env != env:
                raise ValueError(f"Mismatched environment: \\begin{{{prev_env}}} closed by \\end{{{env}}}")
    if env_stack:
        raise ValueError(f"Unclosed environments: {[e for e, _ in env_stack]}")

    # Check labels and cross references
    labels = set(re.findall(r'\\label\{([a-zA-Z0-9_:-]+)\}', clean_text))
    refs = set(re.findall(r'\\(?:ref|Cref|cref)\{([a-zA-Z0-9_:-]+)\}', clean_text))
    missing_refs = refs - labels
    if missing_refs:
        raise ValueError(f"Missing labels referenced in text: {missing_refs}")

    # Check citations
    cites = set()
    for match in re.finditer(r'\\cite\{([a-zA-Z0-9,_ -]+)\}', clean_text):
        for key in match.group(1).split(','):
            cites.add(key.strip())
    missing_cites = cites - valid_bib_keys
    if missing_cites:
        raise ValueError(f"Citations missing from bibliography: {missing_cites}")

    print(f"Validated {tex_path.name}:")
    print(f"  - All {len(labels)} labels and {len(refs)} references match.")
    print(f"  - All {len(cites)} citations present in bibliography.")
    print(f"  - All environments and braces balanced.")


def main():
    paper_dir = Path(__file__).resolve().parents[1] / 'paper'
    tex_file = paper_dir / 'crosswire_formal_synthesis.tex'
    bib_file = paper_dir / 'references.bib'

    if not tex_file.exists():
        sys.exit(f"LaTeX file not found: {tex_file}")
    if not bib_file.exists():
        sys.exit(f"Bib file not found: {bib_file}")

    bib_keys = validate_bib(bib_file)
    validate_tex(tex_file, bib_keys)
    print("LaTeX validation PASSED successfully.")


if __name__ == '__main__':
    main()
