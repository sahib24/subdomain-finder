import dns.resolver
from concurrent.futures import ThreadPoolExecutor


# --------------------------------
# Settings
# --------------------------------

DNS_TIMEOUT = 1
MAX_WORKERS = 10


# --------------------------------
# Check Single Subdomain
# --------------------------------

def check_subdomain(subdomain, domain):

    full_domain = f"{subdomain}.{domain}"

    try:

        answers = dns.resolver.resolve(
            full_domain,
            "A",
            lifetime=DNS_TIMEOUT
        )

        print(f"[FOUND] {full_domain}")

        for answer in answers:
            print(f"       IP: {answer}")

        return full_domain

    except Exception:

        print(f"[NOT FOUND] {full_domain}")

        return None


# --------------------------------
# Active DNS Discovery
# --------------------------------

def active_dns_discovery(domain):

    subdomains = [
        "www",
        "mail",
        "api",
        "dev",
        "test",
        "admin",
        "app",
        "blog",
        "staging",
        "portal"
    ]

    found_subdomains = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:

        futures = [
            executor.submit(
                check_subdomain,
                subdomain,
                domain
            )
            for subdomain in subdomains
        ]

        for future in futures:

            result = future.result()

            if result:
                found_subdomains.append(result)

    return found_subdomains


# --------------------------------
# Test
# --------------------------------

if __name__ == "__main__":

    domain = "example.com"

    results = active_dns_discovery(domain)

    print("\nActive DNS Results:")
    print(results)