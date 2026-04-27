# BTRFS-GUI (Admin Console)

This project now delivers actual **administrative tools** for BTRFS instead of only a reference catalog.

## Deliverables

1. **Desktop application** (Tkinter): execute BTRFS operations from a local OS install.
2. **Web application + Docker container** (Flask): execute the same operations via browser.

## What it administers right now

- File system creation (`mkfs.btrfs`)
- RAID profile conversion / balance (`btrfs balance start`)
- Scrub (`btrfs scrub start -B`)
- Subvolume snapshot
- Quota enable
- Device add/remove
- Filesystem resize
- Readonly check
- Restore extract
- Send/receive stream file workflows

## Safety model

- **Dry run is default** in both desktop and web UI.
- Operations marked destructive are blocked unless:

```bash
export BTRFS_GUI_ALLOW_DESTRUCTIVE=true
```

## Run locally

```bash
pip install -r requirements.txt
python -m app.desktop_app
# or
python -m app.web_app
```

Web URL: <http://127.0.0.1:5000>

## Run with Docker

```bash
docker build -t btrfs-admin-web .
docker run --rm -p 5000:5000 \
  -e BTRFS_GUI_ALLOW_DESTRUCTIVE=false \
  btrfs-admin-web
```

## Tests

```bash
python -m pytest -q
```
