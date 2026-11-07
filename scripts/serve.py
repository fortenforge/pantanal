#!/usr/bin/env python3
import os
import re
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

class RangeAndCacheRequestHandler(SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def end_headers(self):
        self.send_header("Accept-Ranges", "bytes")
        if self.path.endswith((".jpg", ".mp4")):
            self.send_header("Cache-Control", "public, max-age=3600")
        else:
            self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def send_head(self):
        range_header = self.headers.get("Range")
        if not range_header:
            return super().send_head()

        path = self.translate_path(self.path)
        if not os.path.isfile(path):
            return super().send_head()

        m = re.match(r"bytes=(\d+)-(\d*)", range_header)
        if not m:
            return super().send_head()

        file_size = os.path.getsize(path)
        start = int(m.group(1))
        end = int(m.group(2)) if m.group(2) else file_size - 1
        if start >= file_size:
            self.send_error(416, "Requested Range Not Satisfiable")
            return None
        end = min(end, file_size - 1)
        length = end - start + 1

        f = open(path, "rb")
        f.seek(start)
        self.send_response(206)
        self.send_header("Content-type", self.guess_type(path))
        self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        self._range_len = length
        return f

    def copyfile(self, source, outputfile):
        length = getattr(self, "_range_len", None)
        if length is None:
            return super().copyfile(source, outputfile)
        self._range_len = None
        buf_size = 64 * 1024
        remaining = length
        while remaining > 0:
            chunk = source.read(min(buf_size, remaining))
            if not chunk:
                break
            outputfile.write(chunk)
            remaining -= len(chunk)

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    os.chdir("/home/antigravity/fortenforge/pantanal")
    server = ThreadingHTTPServer(("0.0.0.0", 8080), RangeAndCacheRequestHandler)
    print("Serving multi-threaded HTTP on port 8080...", flush=True)
    server.serve_forever()
