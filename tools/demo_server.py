#!/usr/bin/env python3
"""Demo data server for trying Departures Plus without the real one.

Answers like T-Skylt's data server does (same JSON, same odd HTTP framing), with
made-up departures for three big Berlin stations. Used for the simulator and for the
pictures in the README.

    python3 tools/demo_server.py          # listens on 127.0.0.1:9090

It also answers like the BVG API (v6.bvg.transport.rest) under /stops/<number>/departures
and /locations, for trying the "BVG direct" data source with http://127.0.0.1:9090.
"""
import json
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import re

# id: (name, [(line, mode, destination, direction, every N minutes, offset)])
STATIONS = {
    "de:11000:900100003": ("S+U Alexanderplatz Bhf (Berlin)", [
        ("U2", "METRO", "S+U Pankow ", 1, 5, 1), ("U8", "METRO", "S+U Hermannstr. ", 2, 5, 3),
        ("U5", "METRO", "U Hönow ", 1, 5, 2), ("S7", "TRAIN", "S Potsdam Hauptbahnhof ", 2, 10, 4),
        ("M4", "TRAM", "Falkenberg ", 1, 10, 0), ("100", "BUS", "S+U Zoologischer Garten ", 2, 10, 7)]),
    "de:11000:900003201": ("S+U Berlin Hauptbahnhof", [
        ("S3", "TRAIN", "S Erkner ", 1, 10, 1), ("S5", "TRAIN", "S Strausberg Nord ", 1, 10, 5),
        ("S9", "TRAIN", "S Flughafen BER ", 2, 20, 3), ("U5", "METRO", "U Hönow ", 1, 5, 2),
        ("M10", "TRAM", "S+U Warschauer Str. ", 1, 10, 6), ("RE1", "TRAIN", "Frankfurt (Oder) ", 1, 30, 12)]),
    "de:11000:900023201": ("S+U Zoologischer Garten Bhf (Berlin)", [
        ("U9", "METRO", "U Osloer Str. ", 1, 5, 0), ("U2", "METRO", "U Ruhleben ", 2, 5, 2),
        ("S5", "TRAIN", "S Westkreuz ", 2, 10, 4), ("S7", "TRAIN", "S Ahrensfelde ", 1, 10, 1),
        ("X10", "BUS", "Teltow ", 1, 20, 6), ("200", "BUS", "Michelangelostr. ", 1, 10, 8)]),
}
TIMETABLE_ONLY = ("U8", "100", "X10", "S9")      # lines without real-time data in this demo


def departures(sid, now):
    out = []
    base = now.replace(second=0, microsecond=0)
    minute = base.hour * 60 + base.minute
    for line, mode, dest, direction, every, offset in STATIONS[sid][1]:
        first = (minute - offset) // every
        for i in range(6):
            t = base.replace(hour=0, minute=0) + timedelta(minutes=(first + i) * every + offset)
            if t < now - timedelta(seconds=30): continue
            live = line not in TIMETABLE_ONLY and (t - now).total_seconds() < 900
            out.append({"destination": dest, "direction_code": direction, "expected": t.strftime("%Y-%m-%dT%H:%M:%S"),
                        "line": {"id": line, "transport_mode": mode}, "deviations": [] if live else "#"})
    return out


BVG_PRODUCT = {"METRO": "subway", "TRAIN": "suburban", "TRAM": "tram", "BUS": "bus", "SHIP": "ferry"}
BVG_TZ = "+02:00"


def _stop(sid, name):
    n = sid.split(":")[-1]
    return {"type": "stop", "id": n, "name": name, "location": {"type": "location", "id": n, "latitude": 52.52, "longitude": 13.41},
            "products": {k: True for k in ("suburban", "subway", "tram", "bus", "ferry", "express", "regional")}, "ids": {"ifopt": sid}}


def bvg_departures(sid, now, q):
    """The same made-up departures, shaped like the BVG API's (with all its extra fields)."""
    off = [k for k, v in q.items() if v == ["false"]]
    out = []
    for d in departures(sid, now):
        product = "regional" if d["line"]["id"][:2] == "RE" else BVG_PRODUCT[d["line"]["transport_mode"]]
        if product in off: continue
        live = d["deviations"] != "#"
        t = d["expected"] + BVG_TZ
        out.append({"tripId": "1|1|0|86|1", "stop": _stop(sid, STATIONS[sid][0]), "when": t, "plannedWhen": t, "delay": 0 if live else None,
                    "platform": None, "plannedPlatform": None, "prognosisType": "prognosed" if live else None, "direction": d["destination"].strip(),
                    "provenance": None, "line": {"type": "line", "id": "de-vbb-" + d["line"]["id"].lower(), "fahrtNr": "1", "name": d["line"]["id"],
                    "public": True, "adminCode": "BVB---", "productName": product, "mode": "train", "product": product,
                    "operator": {"type": "operator", "id": "berliner-verkehrsbetriebe", "name": "Berliner Verkehrsbetriebe"}},
                    "remarks": [], "origin": None, "destination": _stop(sid, d["destination"].strip()),
                    "currentTripPosition": {"type": "location", "latitude": 52.5, "longitude": 13.4}})
    out.sort(key=lambda x: x["when"])
    return out[:int(q.get("results", ["10"])[0])]


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args): pass

    def do_GET(self):
        url = urlparse(self.path)
        sid = parse_qs(url.query).get("station", [""])[0]
        now = datetime.now()
        q = parse_qs(url.query)
        m = re.match(r"^/stops/(\d+)/departures$", url.path)
        if m or url.path == "/locations":
            if m:
                sid = [k for k in STATIONS if k.endswith(":" + m.group(1))]
                if not sid:
                    body, code = {"message": "stop not found"}, b"404 Not Found"
                else:
                    body, code = {"departures": bvg_departures(sid[0], now, q), "realtimeDataUpdatedAt": int(now.timestamp())}, b"200 OK"
            else:
                word = q.get("query", [""])[0].lower()
                body, code = [_stop(k, v[0]) for k, v in STATIONS.items() if word in v[0].lower()], b"200 OK"
            h = int(BVG_TZ[1:3]) * (-1 if BVG_TZ[0] == "-" else 1)
            date = (now - timedelta(hours=h)).strftime("%a, %d %b %Y %H:%M:%S GMT")
            self.wfile.write(b"HTTP/1.1 " + code + b"\r\nDate: " + date.encode() + b"\r\nAccess-Control-Allow-Origin: *\r\n"
                             b"Content-Type: application/json\r\nConnection: close\r\n\r\n" + json.dumps(body, separators=(",", ":")).encode())
            return
        if url.path == "/get_departures":
            if sid in STATIONS: body = {"departures": departures(sid, now), "timestamp": now.timestamp()}
            else: body = {"timestamp": 0, "departures": "", "msg": "Loading..."}
        elif url.path == "/search_stop":
            body = {v[0]: k for k, v in STATIONS.items() if sid.lower() in v[0].lower()} or {"No stations found!": 0}
        elif url.path == "/get_deviations":
            body = ["U2: lift out of service"]
        else:
            body = {}
        # Like the real server: a bare \n after the status line, no Content-Length, closing ends the body.
        self.wfile.write(b"HTTP/1.0 200 OK\nDate: " + now.strftime("%a, %d %b %Y %H:%M:%S +0200").encode() +
                         b"\r\nConnection: close\r\n\r\n" + (json.dumps(body) + "\n").encode())


if __name__ == "__main__":
    HTTPServer(("127.0.0.1", 9090), Handler).serve_forever()
