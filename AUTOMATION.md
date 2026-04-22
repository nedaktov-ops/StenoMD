# StenoMD Automation Guide

## Option 1: Manual Sync (One-Time)

```bash
cd /home/adrian/Desktop/NEDAILAB/StenoMD
python3 scripts/sync_vault.py
```

Then refresh Obsidian: `Ctrl+R`

---

## Option 2: File Watcher (Real-Time)

Run in background - watches `data/` for new stenogram files:

```bash
cd /home/adrian/Desktop/NEDAILAB/StenoMD
python3 scripts/watch_and_sync.py &
```

When you add new stenogram files to `data/`, it auto-syncs.

**Add a new file:**
```bash
echo "Deputat: Test MP" > data/stenogram_2026-04-25.html
```

**Stop watcher:**
```bash
pkill -f watch_and_sync
```

---

## Option 3: Cron Job (Scheduled)

Edit crontab:
```bash
crontab -e
```

Add line for hourly sync:
```cron
0 * * * * cd /home/adrian/Desktop/NEDAILAB/StenoMD && python3 scripts/watch_and_sync.py
```

Or daily at 8am:
```cron
0 8 * * * cd /home/adrian/Desktop/NEDAILAB/StenoMD && python3 scripts/sync_vault.py
```

---

## Option 4: Systemd Service (Advanced)

Copy service files to systemd:
```bash
sudo cp stenomd-sync.service /etc/systemd/system/
sudo cp stenomd-timer.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable stenomd-sync.timer
sudo systemctl start stenomd-sync.timer
```

Check status:
```bash
systemctl status stenomd-sync.timer
```

---

## Quick Start: Always-On Watcher

Start now and keep running:

```bash
cd /home/adrian/Desktop/NEDAILAB/StenoMD
nohup python3 scripts/watch_and_sync.py > /tmp/stenomd-watch.log 2>&1 &
echo "Watcher started - check with: tail /tmp/stenomd-watch.log"
```

---

## Adding Stenogram Data

Place stenogram files in `data/` folder:

```bash
# Format: stenogram_YYYY-MM-DD.html
echo "Deputat: Klaus Iohannis
Deputat: Marcel Ciolacu
Proiect de lege nr. 123/2026" > data/stenogram_2026-04-25.html
```

The watcher detects and syncs automatically.

---

## Troubleshooting

Check watcher status:
```bash
ps aux | grep watch_and_sync
```

Check latest sync:
```bash
cat /tmp/stenomd-watch.log
```

Force manual sync:
```bash
python3 scripts/sync_vault.py
```