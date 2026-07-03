Quick deployment notes

Systemd unit (example):

1. Copy the unit file to `/etc/systemd/system/flask-app.service` (run as root):

```bash
sudo cp "$(pwd)/deploy/flask-app.service" /etc/systemd/system/flask-app.service
sudo systemctl daemon-reload
sudo systemctl enable --now flask-app.service
sudo journalctl -u flask-app.service -f
```

2. Important: The project path contains spaces. If you prefer, move the project to a path without spaces and update `WorkingDirectory` and `ExecStart` accordingly.

3. Alternatively run in a `tmux` or `screen` session for development:

```bash
cd '/home/mrindiandeveloper/Local Disk E/Projects/Practice'
tmux new -s practice
python3 app.py
```
