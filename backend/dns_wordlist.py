import dns.resolver
from concurrent.futures import ThreadPoolExecutor


# --------------------------------
# Common DNS Wordlist
# --------------------------------

WORDLIST = [
    "www",
    "api",
    "app",
    "admin",
    "mail",
    "ftp",
    "dev",
    "test",
    "staging",
    "stage",
    "beta",
    "demo",
    "portal",
    "login",
    "dashboard",
    "web",
    "server",
    "cdn",
    "static",
    "assets",
    "blog",
    "shop",
    "store",
    "support",
    "help",
    "docs",
    "backend",
    "frontend",
    "database",
    "db",
    "prod",
    "production",
    "uat",
    "qa",
    "internal",
    "mobile",
    "vpn",
    "remote",
    "gateway",
    "status",
    "monitor",
    "dev-api",
    "test-api",
    "api-dev",
    "api-test",
    "api-staging",
]


# --------------------------------
# Check one hostname
# --------------------------------

def check_hostname(hostname):

    record_types = [
        "A",
        "AAAA",
        "CNAME"
    ]

    for record_type in record_types:

        try:

            dns.resolver.resolve(
                hostname,
                record_type,
                lifetime=1
            )

            return hostname

        except Exception:

            continue

    return None


# --------------------------------
# DNS Wordlist Discovery
# --------------------------------

def dns_wordlist_discovery(domain):

    results = set()

    # Wordlist থেকে hostname তৈরি করছি
    hostnames = [
        f"{word}.{domain}"
        for word in WORDLIST
    ]

    # একসাথে একাধিক DNS lookup
    with ThreadPoolExecutor(max_workers=20) as executor:

        checked_hosts = executor.map(
            check_hostname,
            hostnames
        )

        for hostname in checked_hosts:

            if hostname:

                results.add(hostname)

    # Sorted result return
    return sorted(results)