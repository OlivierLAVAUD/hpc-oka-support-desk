# English Technical Summary — TICKET-008

## Incident

After migrating its remote visualization portal to AWS, the customer reported
that 2D sessions worked while 3D sessions remained on a black screen. Windows
users were also disconnected after approximately one minute.

## Root cause

The portal started TurboVNC sessions without the VirtualGL `vglrun` wrapper.
OpenGL applications therefore fell back to the `llvmpipe` software renderer,
which made 3D sessions unusable.

Two configuration issues worsened the impact:

- the ALB target group kept the default 60-second idle timeout;
- Nginx did not forward the `Upgrade` and `Connection` headers required by the
  noVNC WebSocket.

## Resolution

1. Updated the session launcher to run 3D applications through `vglrun`.
2. Added WebSocket headers and long-lived proxy timeouts to Nginx.
3. Raised the ALB idle timeout from 60 to 300 seconds.
4. Customized the login page and restricted access to the laboratory CIDR
   ranges.
5. Added Linux and Windows pre-flight checks for future migrations.

## Validation

A ParaView 3D session was opened from both a Linux workstation and a Windows
workstation. `vglrun glxinfo -B` reported the NVIDIA GPU renderer, sessions
remained connected beyond five minutes, and the portal rejected requests from
IP addresses outside the approved ranges.

## Prevention

- Run `check_remote_viz.sh` before each image, GPU driver or ALB change.
- Run `Test-RemoteViz.ps1` on representative Windows clients.
- Keep Nginx and ALB timeouts aligned with the maximum session duration.
- Expose the OpenGL renderer in the portal admin page and alert when
  `llvmpipe` is detected.

## Skills demonstrated

Linux administration, Nginx and AWS ALB troubleshooting, TurboVNC/VirtualGL,
remote 2D/3D visualization, Windows client validation, PowerShell and Bash
scripting, customer communication and technical writing in English.
