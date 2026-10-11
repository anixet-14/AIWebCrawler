from __future__ import annotations
import ipaddress, socket
from urllib.parse import urlsplit, urlunsplit

class URLSafetyError(ValueError): pass

def validate_url(raw: str) -> str:
    parts = urlsplit(raw.strip())
    if parts.scheme not in {"http", "https"} or not parts.hostname or parts.username or parts.password:
        raise URLSafetyError("URL must be a public HTTP(S) URL without credentials")
    if parts.port and not 1 <= parts.port <= 65535: raise URLSafetyError("invalid port")
    host = parts.hostname.rstrip(".").lower()
    if host in {"localhost", "localhost.localdomain"} or host.endswith(".local"):
        raise URLSafetyError("local destinations are not allowed")
    try:
        addresses = {item[4][0] for item in socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)}
    except socket.gaierror as exc: raise URLSafetyError("host could not be resolved") from exc
    for address in addresses:
        ip = ipaddress.ip_address(address)
        if not ip.is_global: raise URLSafetyError("non-public network destinations are not allowed")
    return urlunsplit((parts.scheme, parts.netloc, parts.path or "/", parts.query, ""))
