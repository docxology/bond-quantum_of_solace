# Manuscript Syntax Reference — QUANTUM

## Citations

Use Pandoc-citeproc syntax referencing `references.bib`: `[@dijkstra1959note]`.

## Cross-references

Refer to figures with Pandoc-crossref: `@fig:delivery` (narrative) or
`[@fig:leverage]` (parenthetical). Each figure is a markdown image with a
`{#fig:label}` anchor pointing at `../output/figures/<name>.png`.

## {{TOKEN}} variables

Numbered sections may reference `{{TOKEN}}` placeholders resolved by
`scripts/z_generate_manuscript_variables.py`. **Do not** put literal
`{{VARIABLE}}` examples in numbered prose sections — the live cross-reference
test treats any token there as a required output.
