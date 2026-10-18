# 0.9.1 - A reliable first round, a smarter fallback, seconds

**Fixed**

* When the display comes on after a night off, the first round through the stations showed no departures. Now every station is asked right away, and a station that is still loading keeps its turn for up to 20 seconds until its departures are in.
* A single failed request no longer shows "No data" at once: the station is asked again twice within a few seconds, and after that every 20 seconds instead of every minute.
* The fallback steps in when the main source has fewer than two departures to show, not only when it has none. Departures you cannot reach count as missing while they are hidden. The main source is asked first again with every update, so the display goes back to it as soon as it delivers.
* A request to the data server waits 5 seconds instead of 4.

**New**

* The clock can show seconds.

**Changed**

* The version is easy to check: it stands on the loading screen while the board starts and as a badge at the top of the settings page.

**Update**

Run the installer again. It removes the previous version first and keeps your stations and settings.

* Windows: download `departuresplus-install.bat`, double-click it and enter the board's IP address.
* macOS / Linux: download the zip, unpack it and run `python3 install.py <board ip>`.

The board must not be connected to a computer by USB while you install. Details are in the [README](https://github.com/jnbp/matrixbox-departures-plus#install).
