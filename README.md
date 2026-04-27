# BTRFS-GUI

A one-stop BTRFS administration suite with:

1. **Desktop app** (Tkinter) for local operating-system installation.
2. **Web app** (Flask) suitable for running in a **Docker container**.

The project organizes BTRFS administration into clear sections:
- File system creation & device onboarding
- RAID profile setup and balancing
- Snapshot/backup/replication workflows
- Maintenance/dedupe/scrub/trim/quotas
- Rescue/repair/recovery tooling

Each section includes links to the upstream application/docs used as its foundation.

## Quick start

### Local (desktop app)

```bash
python -m app.desktop_app
```

### Local (web app)

```bash
pip install -r requirements.txt
python -m app.web_app
```

Open: `http://127.0.0.1:5000`

### Docker (web interface)

```bash
docker build -t btrfs-gui-web .
docker run --rm -p 5000:5000 btrfs-gui-web
```

Then open `http://127.0.0.1:5000`.

## Testing

```bash
python -m pytest -q
```

## Notes

This repository focuses on **interface aggregation and orchestration planning**. It does not bundle or execute privileged BTRFS operations directly by default. Instead, it maps and organizes tools/commands so users can navigate safely and intentionally.
