# Conversion Report (Anonymized)

This MVP used a text-first workflow. PDF conversion was treated as a preprocessing step, not as the core logic of journal-adapt.

---

## Conversion Gate

Only fully readable converted files enter Phase 1.

A converted file must pass these checks:

- major sections are readable;
- section order is intact;
- equations and notation are not badly corrupted;
- citations and references are not collapsed into unrelated text;
- tables do not destroy surrounding prose.

If a file is incomplete or partially converted, it must be retried. If retry fails, the user should provide a clean Markdown/text version or replace the corpus paper.

---

## MVP Outcome

The MVP confirmed the revised rule:

```text
partial conversion -> retry
failed conversion  -> retry or replace
successful text    -> enter Phase 1
```

This is stricter than the earlier draft workflow. The public workflow should not ask users to infer writing patterns from incomplete conversion output.
