# scripts/ conventions — QUANTUM

- Bootstrap `src/` with `# noqa: E402` on the sys-path insert lines (deep
  monorepo path is not covered by root per-file-ignore patterns).
- `sys.executable` with `cwd=project_root` in subprocess smoke tests.
- Exit codes: 0 on success; 2 for CLI usage errors.
- No algorithmic math in scripts — that belongs in `src/`.
