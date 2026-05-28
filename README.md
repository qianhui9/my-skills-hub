# My Skills Hub

A curated collection of selected skills synced from upstream repositories.

## Structure

- `skills/`: synced skills
- `sources/skills.json`: upstream source manifest
- `scripts/sync_skills.py`: sync script
- `.github/workflows/sync-skills.yml`: scheduled sync workflow

## Current skills

- `autoresearch`: synced from `wanshuiyin/Auto-claude-code-research-in-sleep`
- `nature-skills`: synced from `Yuan1z0825/nature-skills`

## Sync locally

```bash
python scripts/sync_skills.py
