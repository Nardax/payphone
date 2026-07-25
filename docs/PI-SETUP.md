# Pi Setup Runbook — Headless Raspberry Pi 3B → first Google Voice call

Step-by-step guide to bring the Raspberry Pi 3 Model B online **headless (Wi-Fi + SSH)** from a
Windows PC and place a first **Google Voice** call. Companion to [PLAN.md](./PLAN.md),
[TASKS.md](./TASKS.md), and [HARDWARE.md](./HARDWARE.md). Completing the **test call** (Step 8)
clears the `v2-pi-bridge` spike gate — the point before which you should **not** buy/wire the
payphone hardware.

> ℹ️ **Why a browser, not a softphone?** Google Voice hands out **no SIP credentials**, so a
> normal CLI softphone would need a **paid** SIP provider (breaks the $0 goal). The realistic **$0**
> path on Linux is the **Google Voice web app (voice.google.com) running in Chromium (WebRTC)**,
> with call audio routed to a USB headset. That's why we install the **Desktop** OS and drive it
> from Windows over **VNC**. This is **decision D3** — treat it as the *leading candidate to
> validate*, not yet proven, until Step 8 passes.

---

## Prerequisites
- Raspberry Pi 3 Model B + its 32GB microSD card.
- **microSD card reader/adapter** for this Windows PC (the card is currently in the Pi — you'll
  move it to the PC to flash it).
- Micro-USB power supply for the Pi (**5V/2.5A**).
- A **2.4GHz** Wi-Fi network (the Pi 3B has no 5GHz radio) + its password.
- A **USB headset** (or USB audio adapter) for the test call.
- Your existing free Google Voice account/number.

---

## Step 1 — Install Raspberry Pi Imager (Windows)
1. Download and install **Raspberry Pi Imager** from https://www.raspberrypi.com/software/.
2. Move the microSD card from the Pi into the Windows PC's card reader.

## Step 2 — Flash Raspberry Pi OS (64-bit, Desktop) with headless settings
1. Open Imager → **Choose Device:** Raspberry Pi 3.
2. **Choose OS:** Raspberry Pi OS (64-bit) — the **Desktop** version (needed for the browser).
3. **Choose Storage:** your 32GB card.
4. Click **Next** → when asked to apply OS customisation, choose **Edit Settings**:
   - **Hostname:** `payphone`
   - **Enable SSH:** yes (use password authentication)
   - **Username / password:** set a username and a **strong password** (the Pi will be on your Wi-Fi)
   - **Configure wireless LAN:** your **2.4GHz** SSID + password, and your Wi-Fi **country**
   - **Locale:** your timezone + keyboard layout
5. **Save** → **Write**. Wait for write + verify to finish.

## Step 3 — First boot onto Wi-Fi
1. Move the flashed card back into the Pi.
2. Connect the micro-USB power (5V/2.5A). The green LED will flicker as it boots.
3. Give it ~1–2 minutes to join Wi-Fi on first boot.

## Step 4 — Connect from Windows over SSH
1. Open **Windows Terminal / PowerShell**.
2. Connect by hostname:
   ```powershell
   ssh <username>@payphone.local
   ```
3. If `payphone.local` doesn't resolve, find the Pi's IP in your router's client list (or your
   phone's network scanner) and use it:
   ```powershell
   ssh <username>@<pi-ip-address>
   ```
4. Accept the host key prompt and log in with the password you set.

## Step 5 — Update the OS
```bash
sudo apt update && sudo apt full-upgrade -y
sudo reboot
```
Reconnect with SSH after it reboots.

## Step 6 — Enable the desktop over VNC (still headless)
1. Run the config tool:
   ```bash
   sudo raspi-config
   ```
2. **Interface Options → VNC → Enable.**
3. **System Options → Boot / Auto Login → Desktop Autologin.**
4. Finish and reboot.
5. On Windows, install a **VNC viewer** (e.g., RealVNC Viewer) and connect to `payphone.local`
   (or the Pi's IP). You now see the Pi's desktop with no monitor attached.

## Step 7 — Verify USB audio
1. Plug the USB headset/adapter into the Pi.
2. List devices:
   ```bash
   aplay -l    # playback devices
   arecord -l  # capture devices
   ```
3. Set the USB device as the default output/input (via `sudo raspi-config` → System → Audio, or
   the desktop volume applet).
4. Quick test:
   ```bash
   speaker-test -t wav -c 2 -l 1      # hear test tone in the headset
   arecord -d 3 test.wav && aplay test.wav   # record 3s, play it back
   ```

### Routing audio to the USB headset (Bookworm / PipeWire)
Current Raspberry Pi OS uses **PipeWire**; the easiest control panel is **`pavucontrol`**:
```bash
sudo apt install -y pavucontrol
pavucontrol   # run from the VNC desktop
```
- **Output Devices** tab → click the check-mark to set the **USB headset as fallback (default)**.
- **Input Devices** tab → set the **USB mic as fallback (default)**.
- **Configuration** tab → if the headset has both mic + speaker, pick a **Duplex** profile.
- **Playback** tab → while a call is live, you can move **Chromium's** audio stream onto the USB
  device from here.
- Sanity-check the devices are seen: `pw-cli ls Node` (or `aplay -l` / `arecord -l`).

## Step 8 — Google Voice bridge + test call (decision D3, spike gate)
1. On the Pi desktop (over VNC), open **Chromium** and go to **https://voice.google.com**.
2. Sign in to the Google account that owns your Voice number.
3. Point Chromium at the USB headset:
   - **Microphone:** open `chrome://settings/content/microphone` and select the USB headset as the
     default mic (Chromium exposes an input-device picker here).
   - **Output:** Chromium follows the **system default sink**, so setting the USB headset as the
     fallback in `pavucontrol` (Step 7) routes call audio to it. If it doesn't, use `pavucontrol`'s
     **Playback** tab to drag Chromium's stream onto the headset while the call is ringing.
   - When the site asks, **allow microphone** access for voice.google.com.
4. **Outbound test:** click **Calls**, dial a number you can answer, and confirm clean two-way
   audio on the headset.
5. **Inbound test:** call your Google Voice number from another phone and answer it in the
   browser; confirm two-way audio.
6. ✅ **Both directions working = the `v2-pi-bridge` spike is cleared.** Record the result and any
   quirks below, then proceed to buying/wiring the payphone hardware.

---

## Troubleshooting
- **`payphone.local` won't resolve:** use the IP from your router; ensure the PC and Pi are on the
  same 2.4GHz network.
- **Pi never joins Wi-Fi:** re-flash and double-check the SSID is 2.4GHz and the Wi-Fi country was
  set in Imager.
- **VNC connects but audio is silent:** confirm the USB device is the system default *and* selected
  inside Chromium; some HDMI/analog defaults steal the audio route.
- **Chromium/WebRTC feels heavy on the Pi 3B:** close other apps; if calls are choppy, capture it in
  the decision log — a newer Pi (4/5) is the fallback for the browser path.

## Security
- Use a **strong Pi password** — it's reachable on your Wi-Fi.
- **Never commit** Wi-Fi or Google credentials to this repo.

## Related decisions
See the [decision log](./TASKS.md#decision-log): **D3** GV bridge = Google Voice web app in
Chromium (WebRTC) — *pending validation in Step 8*.
