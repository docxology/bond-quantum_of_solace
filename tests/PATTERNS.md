# Test patterns — QUANTUM

- **Analytical expectations**: assert against hand-computed values (e.g. HHI of
  known shares, max-flow totals on small networks) rather than loose checks.
- **Error branches**: every validation `ValueError`/`KeyError` in the domain
  core is exercised via `pytest.raises`.
- **Subprocess smoke**: run thin CLIs with `sys.executable`, `cwd=project_root`,
  asserting exit code and artifacts.
- **Live token cross-reference**: `test_scripts_smoke.py` asserts every
  `{{TOKEN}}` in `manuscript/[0-9]*.md` is produced by `generate_variables()`.
- **tmp_path**: figure generators and config loading write into `tmp_path`, so
  they never pollute the tree.
- **No mocks, period.** If a test needs a "fake", implement the real behaviour.
