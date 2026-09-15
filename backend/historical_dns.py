import requests
import json


def historical_dns_discovery(domain):
    discovered = set()

    url = f"https://freeapi.robtex.com/pdns/forward/{domain}"

    try:
        response = requests.get(
            url,
            timeout=20,
            headers={
                "User-Agent": "SubdomainFinder/1.0"
            }
        )

        response.raise_for_status()

        # Robtex PDNS endpoint normally returns NDJSON
        for line in response.text.splitlines():

            line = line.strip()

            if not line:
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue

            hostname = record.get("rrname", "")

            if not hostname:
                continue

            hostname = hostname.strip().lower().rstrip(".")

            if (
                hostname == domain
                or hostname.endswith("." + domain)
            ):
                discovered.add(hostname)

    except requests.RequestException as error:
        print(f"Historical DNS error: {error}")

    return sorted(discovered)