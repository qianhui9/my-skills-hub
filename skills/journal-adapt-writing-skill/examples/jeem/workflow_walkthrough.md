# Workflow Walkthrough: JEEM MVP (Anonymized)

This file shows what happened in the public MVP example. It is intentionally descriptive, so users can understand the workflow without seeing the private manuscript.

---

## Stage 0. Inputs

| Input type | Public sample content | Included in repo? |
|------------|----------------------|-------------------|
| Manuscript | One anonymized working paper; title, topic details, author info, model objects, and results redacted | No |
| Primary corpus | 6 JEEM papers | Titles only |
| Secondary corpus | 9 field/topical papers from related journals | Titles only |
| User/lab exemplars | None | Not applicable |
| Static skill | None in the public sample | Not applicable |

The public sample shows the writing-pattern extraction process, not the manuscript revision itself.

---

## Stage 1. Conversion Gate

All corpus files must be fully readable before style extraction.

| Status | Action |
|--------|--------|
| Full conversion | Enter Phase 1 |
| Partial conversion | Retry conversion |
| Failed conversion | Retry, provide clean Markdown/text, or replace the paper |

The MVP rule is strict: partial and failed conversions do not enter Phase 1.

See: [`conversion_report.md`](conversion_report.md).

---

## Stage 2. Paper Style Cards

Each paper is converted into a style card. A style card does not copy or summarize the paper's substantive findings. It records writing behavior:

- how the abstract is structured;
- how the introduction opens;
- where the gap appears;
- how contributions are stated;
- how methods, results, and discussion are sequenced;
- what language/register patterns are useful for revision.

See: [`paper_style_cards/`](paper_style_cards/).

---

## Stage 3. Aggregated Style Profile

The paper cards are aggregated into a JEEM-oriented style profile.

The aggregation separates:

- **primary target-journal patterns** from JEEM papers;
- **secondary supporting patterns** from other field/topical papers;
- **red flags** that would make a manuscript feel less aligned with JEEM.

See: [`style_profile.md`](style_profile.md).

---

## Stage 4. Final Writing Pattern Table

The aggregated profile is translated into a compact writing table. This is the bridge between corpus analysis and usable revision behavior.

See: [`writing_pattern_table.md`](writing_pattern_table.md).

---

## Stage 5. Dynamic Writing Skill

The writing table becomes a temporary `dynamic_writing_skill.md`.

This file tells the agent how to revise this manuscript for this writing destination, while preserving:

- facts;
- citations;
- equations and notation;
- numerical results;
- labels and cross-references;
- author-defined terms.

See: [`dynamic_writing_skill.md`](dynamic_writing_skill.md).

---

## Stage 6. Redacted Phase 2 Sample

The public example includes only sanitized placeholders for Phase 2:

- [`section_diagnosis_sample.md`](section_diagnosis_sample.md)
- [`section_revision_sample.md`](section_revision_sample.md)
- [`section_revision_log_sample.md`](section_revision_log_sample.md)

The real manuscript section and real revised text are not included.
