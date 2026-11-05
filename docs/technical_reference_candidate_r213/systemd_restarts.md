# systemd service restart behavior
Sources:
https://www.freedesktop.org/software/systemd/man/261/systemd.service.html
https://www.freedesktop.org/software/systemd/man/260/systemd.unit.html

Restart= selects which service exits trigger automatic restart. RestartSec= sets the delay before an automatic restart. StartLimitIntervalSec= and StartLimitBurst= configure start-rate limiting in the [Unit] section; Restart= and RestartSec= belong in [Service]. Defaults can depend on systemd version and manager configuration. Do not invent a RestartMaxAttempts= directive.

Example:
    [Unit]
    StartLimitIntervalSec=60s
    StartLimitBurst=3

    [Service]
    ExecStart=/usr/bin/myapp
    Restart=on-failure
    RestartSec=5s
