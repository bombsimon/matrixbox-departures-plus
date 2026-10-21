# 0.11.0 - Choice of data source, settings page in the MatrixBOX design

**New**

* **Data source:** a new section on the settings page picks where departures come from.
  * **T-Skylt:** as before, for every country and operator in the list.
  * **BVG direct:** the free public BVG API ([v6.bvg.transport.rest](https://v6.bvg.transport.rest/)), run by volunteers, without any guarantee. It covers VBB and Berlin stations, and your stations keep working because both sources use the same VBB numbers. Other stations keep using T-Skylt. The station search asks the BVG API too.
  * **Automatic:** T-Skylt first, and the BVG API whenever T-Skylt has no data for a VBB or Berlin station.
  * **Own server:** a server of yours that answers like T-Skylt's. Settings that already used a different data server switch to this one by themselves.

  Good to know about BVG direct: its answers are bigger and come over HTTPS, so it uses more of the board's memory and each update pauses the ticker a little longer (*Fewer updates* under Advanced helps). It has no direction numbers, so the Direction field and `:1`/`:2` in Lines only work with T-Skylt, and it brings no operator service messages for the ticker. Station pills on the settings page say *In use · BVG* while a station runs on it.

* **Scrolling destinations:** a destination too long for its column, even after the abbreviations, can scroll to its end, slow, medium or fast, and then jump or scroll back to its start (Destination names, off by default).
* **Destinations without the district:** "Lankwitz, Halbauer Weg" becomes "Halbauer Weg", as the BVG API names many bus stops that way (Destination names, on by default).
* **Cancelled departures:** show them or leave them out, with your own text instead of "cancelled" and your own color instead of red (Departure rows and Colors).
* **Arrows:** the ⟳ and ⟲ of Berlin's Ringbahn S41 and S42, ↻ ↺, → and ← now show up instead of a gap, in all three text sizes, and a "->" in a destination such as "Wittenau -> Bus 22" becomes a real arrow.

**Changed**

* The settings page now uses the shared MatrixBOX look: cards with small section titles, the same switches, segmented buttons, input fields and buttons as the built-in apps, and the same page width. Wide controls such as sliders and long choices get their own line under their label.
* The clock follows the real offset from UTC when departures come from the BVG API, so it stays right across the change to winter time.

**Update**

Run the installer again. It removes the previous version first and keeps your stations and settings.

* Windows: download `departuresplus-install.bat`, double-click it and enter the board's IP address.
* macOS / Linux: download the zip, unpack it and run `python3 install.py <board ip>`.

The board must not be connected to a computer by USB while you install. Details are in the [README](https://github.com/jnbp/matrixbox-departures-plus#install).
