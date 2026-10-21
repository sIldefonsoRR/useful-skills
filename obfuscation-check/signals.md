# Obfuscation Signals Catalog

Patterns are starting points, not verdicts. Exclude `node_modules`, `vendor`, `.venv`, `site-packages`, `dist`, `build`, `*.min.*`, and declared codegen output. In a git repo use `git grep -I -nE '<pattern>'` so `.git` and untracked noise are skipped; otherwise add `--exclude-dir=.git`. In zsh, quote arguments containing `=`. **Read every match in context before recording it, and never run, import, or decode the file.**

The patterns below are **POSIX ERE** (`-E`), so they run the same under `git grep -E` and BSD/macOS `grep -E`: they use `[[:space:]]` not `\s`, and no `\b` word boundaries. If a pattern misses an expected hit, your `grep` may be matching literally; widen it (drop a prefix, add `.*`) rather than switching engines. Only if you add `\b`, `\s`, or other Perl syntax yourself, pass `-P` / `--perl-regexp` (and accept it may be unavailable on some builds).

Hard signals (B1–B4) can confirm obfuscation on their own. Soft signals (B5–B8) only raise likelihood and must each be backed by a quoted example.

## Hard signals (can confirm)

### B1 - Obfuscation / packer tool markers

Banners, runtime stubs, and imports left by known obfuscators and minifiers.

```bash
git grep -I -nE 'pyarmor|__pyarmor__|pyarmor_runtime|pytransform|Intensio|Oxyry|pyminifier|python-minifier|pyobfuscate|de4py|# *Protected by|Nuitka|cython_freeze' .
```

Markers: PyArmor (`from pyarmor_runtime`, `__pyarmor__(...)`, `# Pyarmor Plugin`, a `pytransform`/`pyarmor_runtime_*` package), `# Obfuscated with Intensio`, Oxyry header comments, pyminifier/python-minifier output banners. The presence of such a marker in a file (or its loader stub) makes that file Confirmed. Note the tool by name in the report.

### B2 - Encoded or compressed blob executed at runtime

The defining pack-and-run pattern: a payload is decoded or decompressed, then handed to an execution sink.

```bash
# decode / decompress sources
git grep -I -nE 'base64\.(b64|b32|b16|urlsafe_b64)decode|binascii\.(a2b_|unhexlify)|bytes\.fromhex|codecs\.decode|\.decode\(.{0,20}(rot_?13|hex|base64)|zlib\.decompress|lzma\.decompress|gzip\.decompress|bz2\.decompress|marshal\.loads' .
# execution sinks
git grep -I -nE 'exec[[:space:]]*\(|eval[[:space:]]*\(|compile[[:space:]]*\(|__import__[[:space:]]*\(|types\.FunctionType[[:space:]]*\(|importlib\.' .
```

Record B2 only after reading the code and confirming a decoded/decompressed value **flows into** `exec`, `eval`, `compile`, `marshal.loads` of code, `types.FunctionType`, or an equivalent. Common shapes: `exec(zlib.decompress(base64.b64decode(b'...')))`, a one-letter function that decodes then `exec`s its argument, nested decode calls many layers deep. If the decoded value is stored, written, or sent but never executed, it is **not** B2 (note it, but it does not confirm). If a decode and an `exec` both appear but you cannot connect them, cap the file at Likely.

### B3 - Bytecode-only module

Compiled Python shipped without its source, so the readable form is hidden.

```bash
git ls-files | grep -iE '\.py[co]$'          # tracked .pyc/.pyo
git ls-files | grep -iE '(^|/)__pycache__/'  # tracked bytecode cache
```

A tracked `.pyc`/`.pyo` (or `__pycache__`) is B3 when there is no matching `.py` source in the repo for that module. A `.pyc` inside an excluded `build`/`dist`/`site-packages` path is build output, not B3. Note the Python version from the file's magic only if already known; do not execute anything to read it.

### B4 - Freezer / packer artifacts replacing source

A frozen or bundled executable standing in for source code.

```bash
git grep -I -nE 'PyInstaller|pyi_|_MEIPASS|sys\._MEIPASS|py2exe|cx_Freeze|__nuitka|Nuitka-|frozen=True' .
git ls-files | grep -iE '\.(exe|bin|pyd|so)$|(^|/)(dist|build)/.*(onefile|bootloader)'
```

B4 is a packed/frozen distribution (PyInstaller onefile, py2exe, Nuitka build, cx_Freeze) committed in place of, or alongside and hiding, the source. A normal build config that produces these in an excluded `dist/` is not B4; a committed frozen binary with no corresponding source is.

## Soft signals (raise likelihood only)

Record each only with a concrete example quoted from the file.

### B5 - Lexical mangling

- Floods of non-semantic identifiers: mixes of `l`, `I`, `1`, `O`, `0` (`Il1lI = O0O0O`), hex-style names (`_0x3f2a`, `a1b2c3d4`), or many identifiers of identical random length.
- Confusable / homoglyph identifiers: names using Unicode letters that look ASCII (Cyrillic `а`, Greek `ο`).
- Every developer-facing name stripped: no docstrings, no type annotations, all locals renamed to one- or two-character tokens, unlike the rest of the repo.

```bash
git grep -I -nE '_0x[0-9a-fA-F]+|[Il1O0]{4,}' .
```

### B6 - Constant codification

- Long `\x..`/`\u....` escaped string blobs where printable text would be expected.
- `chr()` / `ord()` concatenation chains or `''.join(map(chr, [...]))` building strings.
- Integer or string constants assembled from arithmetic or bitwise expressions instead of literals (`(0x1F << 8) ^ 0x2A`, `str(int('...', 36))`) with no functional reason.

```bash
git grep -I -nE "(\\\\x[0-9a-fA-F]{2}){8,}|chr\\([0-9]+\\)([[:space:]]*\\+[[:space:]]*chr\\([0-9]+\\)){3,}|''\\.join\\(map\\(chr" .
```

### B7 - Control-flow flattening

- A single dispatch loop (`while True:` or `while <state> != N:`) whose body is a large `if <state> == 0: ... elif <state> == 1: ...` ladder or a dict/list of lambdas indexed by a state variable, with the state reassigned to jump between blocks — natural loops and conditionals replaced by goto-like state transitions.
- Abnormally high branch count with no domain meaning, one basic block per state.

```bash
git grep -I -nE 'while +True:|while +[A-Za-z_][A-Za-z0-9_]* *[!=]=' .
```

Confirm by reading: a normal event loop or state machine with meaningful states is not B7. Flattening shows machine-assigned numeric states and shuffled block order.

### B8 - Pervasive dynamic / indirect execution

- Names resolved from constructed strings throughout the file: `getattr(obj, <built string>)`, `globals()[<built string>]`, `__import__(<built string>)`, `vars()[...]`, used to hide which functions are called.
- `exec`/`eval`/`compile` on assembled source, used pervasively rather than at one documented extension point.

```bash
git grep -I -nE "getattr\\([^,]+, *[^'\"]|globals\\(\\)\\[|locals\\(\\)\\[|vars\\(\\)\\[|__import__\\(|__getattribute__\\(" .
```

A single plugin loader or one reflective call is not B8; the signal is systematic indirection that obscures the call graph.
