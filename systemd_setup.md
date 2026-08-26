## Use the following document to set up a service using systemd.

*Note: This systemctl service file is set up for Raspberry Pi OS with the default username being `pi`.*

#### Paste the following command in the terminal to create a systemd service file and populate it with the correct systemd setup:
```bash
cat > /etc/systemd/system/resumematcher.service <<EOF
[Unit]
Description=Resume Matcher ATS Gunicorn Service
After=network.target

[Service]
# The user that runs Gunicorn (e.g., pi)
User=pi

# Path to your app directory
WorkingDirectory=/home/pi/resume-matcher-ats

# Absolute path to the virtualenv Gunicorn binary and parameters
ExecStart=/home/pi/resume-matcher-ats/.venv/bin/gunicorn --workers 1 --bind 0.0.0.0:5000 app:app

# Automatically restart the service if it crashes
Restart=always

[Install]
WantedBy=multi-user.target
EOF
```

#### Paste the following commands in the terminal
```bash
sudo systemctl daemon-reload
sudo systemctl enable resumematcher
sudo systemctl start resumematcher
```
The WSGI server will start automatically.

If you make any changes to the service file, you need to reload the daemon and restart the service:
```bash
sudo systemctl daemon-reload
sudo systemctl restart resumematcher
```

If you make any changes to the application code, you only need to restart the service:
```bash
sudo systemctl restart resumematcher
```