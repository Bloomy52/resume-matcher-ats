## Use the following document to set up a service using systemd.

*Note: This systemctl service file is set up for Raspberry Pi OS with the default username being `pi`.*

#### Create the file:
```bash
sudo nano /etc/systemd/system/resumematcher.service
```

#### Paste the contents of the text block below into the edit file screen

```text
[Unit]
Description=Resume Matcher ATS Gunicorn Service
After=network.target

[Service]
# The user that runs Gunicorn (e.g., pi)
User=pi

# Path to your app directory
WorkingDirectory=/home/pi/resume-matcher-ats

# Absolute path to the virtualenv Gunicorn binary and parameters
ExecStart=/home/pi/resume-matcher-ats/.venv/bin/gunicorn --workers 2 --bind 0.0.0.0:5000 app:app

# Automatically restart the service if it crashes
Restart=always

[Install]
WantedBy=multi-user.target
```
Then save the file using `Ctrl+X, Y, Enter` to save the file.


#### Paste the following commands in the terminal
```bash
sudo systemctl daemon-reload
sudo systemctl enable resumematcher
sudo systemctl start resumematcher
```
The WSGI server will start automatically.
