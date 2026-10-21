# 0.11.0 - Settings page in the MatrixBOX design, scrolling destinations

**New**

* **Settings page in the MatrixBOX design:** cards with small section titles and the same switches, segmented buttons, input fields and buttons as the built-in apps, at the same page width. Wide controls such as sliders get their own line under their label.
* **Scrolling destinations:** a destination too long for its column, even after the abbreviations, can scroll to its end, slow, medium or fast, and then jump or scroll back to its start (Destination names, off by default).
* **Destinations without the district:** "Lankwitz, Halbauer Weg" becomes "Halbauer Weg" (Destination names, on by default).
* **Cancelled departures:** show them or leave them out, with your own text instead of "cancelled" and your own color instead of red (Departure rows and Colors).
* **Arrows:** the ⟳ and ⟲ of Berlin's Ringbahn S41 and S42, ↻ ↺, → and ← now show up instead of a gap, in all three text sizes, and a "->" in a destination becomes a real arrow.
* **Data source setting:** T-Skylt's data server stays the default. For VBB and Berlin stations the public VBB/BVG API ([v6.bvg.transport.rest](https://v6.bvg.transport.rest/), run by volunteers) can be used instead or as a stand-in, and a server of your own works too. With the BVG API the Direction field and `:1`/`:2` in Lines have no effect, and each update takes a little longer.

**Update**

Run the installer again. It removes the previous version first and keeps your stations and settings.

* Windows: download `departuresplus-install.bat`, double-click it and enter the board's IP address.
* macOS / Linux: download the zip, unpack it and run `python3 install.py <board ip>`.

The board must not be connected to a computer by USB while you install. Details are in the [README](https://github.com/jnbp/matrixbox-departures-plus#install).
