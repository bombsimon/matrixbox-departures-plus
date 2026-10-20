# 0.10.0 - Logo, bold text, smaller icon letters

**New**

* **Logo:** upload a picture on the settings page, or paste the address of one. Your browser scales it to the display and reduces it to 14 colors, and you see a preview first. The logo can take over the display every few minutes, for as long as you like, coming in by fading, zooming, sliding, dissolving, as blinds or wiping, and while it is shown it can glow, grow and shrink, or both. It can also come first whenever the display turns on. Home Assistant can show it at the press of a button (`/api/set?logo=1`).
* **Bold text** for the departure rows in normal and large text.
* **Letters as icons:** two letters in an icon place, such as WC, can be small capitals or small capitals cut out of a box in the icon's color, like a line signet, readable in any color and LED tone.
* **Signet text per line:** two lists give chosen lines or whole vehicle types black or white text in their signets, e.g. black for `@BUS` and white for `U3`, while the rest follows the general setting.
* **Italic ticker** as an option.
* **Fewer updates for a smoother ticker** (Advanced): each station is fetched every 2 minutes at most.

**Fixed**

* The app now starts from the MatrixBOX 3rd party store, which installs it one folder deeper.
* After the display came on, a station without any data made the app keep fetching every station in the background, so the ticker kept stopping. The warm-up now only asks stations without data, for the first minute.

**Update**

Run the installer again. It removes the previous version first and keeps your stations and settings.

* Windows: download `departuresplus-install.bat`, double-click it and enter the board's IP address.
* macOS / Linux: download the zip, unpack it and run `python3 install.py <board ip>`.

The board must not be connected to a computer by USB while you install. Details are in the [README](https://github.com/jnbp/matrixbox-departures-plus#install).
