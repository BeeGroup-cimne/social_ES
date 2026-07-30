# `ServeMaps`

**Serving the maps**

Serves the written maps over HTTP on localhost, and returns the running server. A tiled map has to be served rather than opened from disk: a page on a `file://` URL is not allowed to fetch anything, its own tiles included.

```python
INE.ServeMaps(wd, port=8000, directory=None)
```

## Parameters

```
wd : str
    The working directory the maps were written under.
port : int, default 8000
    Port to listen on. Pass 0 to let the system choose a free one.
directory : str, optional
    Directory to serve. Defaults to ``{wd}/INE``.
```

## Notes

- Answers **byte-range requests**, which the stock `http.server` does not — and which a tiled map needs, since it reads its archive by asking for the ranges holding the header, the directory and the tiles it draws.
- Call `shutdown()` on the returned server when finished, or leave it running for the session.
- Maps written without `tiles=True` are self-contained files and need none of this.

## Example

```python
from social_ES import INE
wd = "/path/to/your/data"

server = INE.ServeMaps(wd)      # prints the address to open
# ... open the map ...
server.shutdown()
```

---

[← All datasets](README.md) · [Repository](https://github.com/BeeGroup-cimne/social_ES)
