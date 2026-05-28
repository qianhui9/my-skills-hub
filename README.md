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


## Visual execution steps

- Add skills information to the sources/skills.json file;

- Go to Actions → Sync skills → Run workflow;

- Merge the skills in the Pull requests section, and you'll see the new skills displayed in the skills/ directory.
