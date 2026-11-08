# Repository Guidelines

## Project Structure & Module Organization

Engineering Fieldnotes is a dependency-free, Traditional Chinese learning site for engineers moving from AI software into modem logging.

- `content/`: authored HTML; `modem.html` supplies the first chapter's original layout.
- `tools/build_site.py`: shared templates and chapter navigation; generates the four committed root HTML pages. Edit sources and regenerate rather than editing outputs alone.
- `assets/`: shared CSS, JavaScript interactions, and favicon.
- `examples/`: C11 teaching programs and Python integration tests.
- `tools/`: site validation and JavaScript decoder tests.
- `.github/workflows/pages.yml`: validates pull requests and deploys successful `main` builds to GitHub Pages.

## Build, Test, and Development Commands

Run from the repository root with Python 3.9+, Node.js, and Clang:

```bash
python3 tools/build_site.py       # Regenerate pages
python3 tools/check_site.py       # Check local links, IDs, and assets
node --check assets/app.js
node --check assets/labs.js
node tools/test_labs.cjs          # Check browser decoder logic
python3 -m http.server 8000       # Preview at localhost:8000
```

Compile and test the C logger:

```bash
mkdir -p build
clang -std=c11 -Wall -Wextra -Wpedantic -Werror -g -O1 \
  -fsanitize=address,undefined -fno-omit-frame-pointer \
  examples/log_lab.c -o build/log_lab
python3 examples/test_lab.py build/log_lab
```

## Coding Style & Naming Conventions

Use four-space indentation for Python and C, two spaces for JavaScript and YAML. Use `snake_case` for Python/C identifiers, `camelCase` for JavaScript, and kebab-case for chapter filenames and HTML IDs. Preserve surrounding HTML/CSS formatting; no formatter or linter is configured. Keep asset links relative for repository-subpath hosting, and guard page-specific JavaScript initialization.

## Testing Guidelines

Tests use Python assertions, Node's built-in assertions, and C self-tests; no coverage percentage is enforced. Follow `test_*.py` and `test_*.cjs` naming. Cover valid input, truncation, invalid fields, size limits, and ring-buffer wraparound when changing parsers. Check desktop/mobile layouts and affected interactions. Report sanitizer limitations explicitly. New chapters require updates to the generator, checker, and deployment allowlist.

## Commit & Pull Request Guidelines

History uses short, imperative subjects, such as “Build modem learning knowledge base…”, without a mandatory prefix. Keep commits focused. PRs should explain changes, list validation results, link relevant issues, and include screenshots for visual changes. Include regenerated pages with source edits.

## Content Accuracy & Publication

Cite authoritative public sources and identify specification versions, teaching simplifications, and verification dates. Never add proprietary code, logs, credentials, or guessed internal acronym definitions. LG v1 is a teaching format; its single-threaded ring buffer is not production firmware. Keep `build/` and `_site/` untracked, and verify deployment success before claiming publication.
