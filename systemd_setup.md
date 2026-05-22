## Use the following document to set up a service using systemd.

*Note: This systemctl service file is set up for Raspberry Pi OS with the default username being `pi`.*

#### Create the file:
```bash
sudo nano /etc/systemd/system/talentstream.service
```

#### Paste the contents of the text block below into the edit file screen

```text
[Unit]
Description=TalentStream ATS Gunicorn Service
After=network.target

[Service]
# The user that runs Gunicorn (e.g., pi or louie)
User=<Your Username Here>

# Path to your app directory
WorkingDirectory=/home/pi/talent-stream-ats

# Absolute path to the virtualenv Gunicorn binary and parameters
ExecStart=/home/pi/talent-stream-ats/.venv/bin/gunicorn --workers 2 --bind 0.0.0.0:5000 app:app

# Automatically restart the service if it crashes
Restart=always

[Install]
WantedBy=multi-user.target
```
Then save the file using `Ctrl+X, Y, Enter` to save the file.


#### Paste the following commands in the terminal
```bash
sudo systemctl daemon-reload
sudo systemctl enable talentstream
sudo systemctl start talentstream
```
The WSGI server will start automatically.
