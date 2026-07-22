# HACS default publication checklist

The repository files are prepared for HACS integration validation. Complete these steps in order.

## 1. Publish the repository

- Create the public GitHub repository `soulripper13/bandwagon_host`.
- Use `main` as its default branch.
- Push the complete repository, including `.github`, `custom_components/bandwagon_host/brand`, and `RELEASE_NOTES.md`.
- Enable GitHub Issues.
- Set a concise repository description.
- Add topics such as `home-assistant`, `hacs`, `custom-component`, `bandwagon-host`, `kiwivm`, and `vps`.

## 2. Pass validation

- Wait for **HACS validation** and **Hassfest validation** to complete.
- Resolve every error. Do not configure ignored HACS checks for a default-list submission.
- Install the default branch as a HACS custom repository and test setup, update, unload, controls, and the dashboard card.

## 3. Publish the release

- Create a full GitHub release only after both validation workflows pass.
- Use tag `v1.0.0`, matching the `1.0.0` manifest version.
- Use `RELEASE_NOTES.md` as the release notes.
- Do not publish it as a draft or prerelease.
- Install the release through HACS and repeat a clean setup test.

## 4. Submit to HACS default

- Fork `hacs/default` using the same personal GitHub account that owns this repository.
- Create a new branch from the current `master` branch.
- Add `soulripper13/bandwagon_host` alphabetically to the `integration` file.
- Open an editable pull request and complete every item in the pull request template accurately.
- Do not display a **HACS Default** badge until the pull request is merged.

Official process: https://www.hacs.xyz/docs/publish/include/
