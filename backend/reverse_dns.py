import dns.resolver
import ipaddress
from concurrent.futures import ThreadPoolExecutor


def reverse_dns_lookup(ip):

    try:
        # IP address valid কিনা check
        ipaddress.ip_address(ip)

        # Reverse DNS lookup name তৈরি
        reverse_name = dns.reversename.from_address(ip)

        # PTR record query
        answers = dns.resolver.resolve(
            reverse_name,
            "PTR",
            lifetime=3
        )

        results = []

        for answer in answers:
            hostname = answer.to_text().rstrip(".")
            results.append(hostname)

        return results

    except Exception:
        return []


def reverse_dns_discovery(ip_addresses):

    discovered = set()

    # একাধিক IP একসাথে Reverse DNS lookup করবে
    with ThreadPoolExecutor(max_workers=10) as executor:

        results = executor.map(
            reverse_dns_lookup,
            ip_addresses
        )

        for result in results:
            for hostname in result:
                discovered.add(
                    hostname.lower()
                )

    return sorted(discovered)