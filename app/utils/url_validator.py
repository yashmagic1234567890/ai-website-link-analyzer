
from urllib.parse import urlparse
import ipaddress
import socket


def validate_url(url: str) -> str:
    if not url:
        raise ValueError("URL is required.")

    url = url.strip()
    parsed = urlparse(url)

    # Allow only HTTP and HTTPS
    if parsed.scheme not in ("http", "https"):
        raise ValueError("Only HTTP and HTTPS URLs are allowed.")

    if not parsed.hostname:
        raise ValueError("Invalid URL: hostname is missing.")

    # Block URLs containing usernames or passwords
    if parsed.username or parsed.password:
        raise ValueError("URL credentials are not allowed.")

    # Validate port number
    try:
        port = parsed.port
    except ValueError:
        raise ValueError("Invalid port number.")

    # Allow only standard web ports
    if port not in (None, 80, 443):
        raise ValueError("Only ports 80 and 443 are allowed.")

    hostname = parsed.hostname.lower()

    # Block localhost
    if hostname == "localhost" or hostname.endswith(".localhost"):
        raise ValueError("Localhost URLs are not allowed.")

    # Check IP addresses and DNS records
    try:
        addresses = socket.getaddrinfo(
            hostname,
            None,
            type=socket.SOCK_STREAM
        )

        if not addresses:
            raise ValueError("Unable to resolve hostname.")

        for address in addresses:
            ip = ipaddress.ip_address(address[4][0])

            if not ip.is_global:
                raise ValueError(
                    "Private or reserved IP addresses are not allowed."
                )

    except socket.gaierror:
        raise ValueError("Unable to resolve hostname.")

    return url
