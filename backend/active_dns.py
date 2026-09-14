import dns.resolver


# --------------------------------
# Active DNS Discovery Function
# --------------------------------

def active_dns_discovery(domain):

    # Common subdomain names
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

    # Found subdomain এখানে রাখবে
    found_subdomains = []


    # প্রতিটি subdomain check করবে
    for subdomain in subdomains:

        # Full domain তৈরি করবে
        full_domain = f"{subdomain}.{domain}"

        try:

            # DNS A record query করবে
            answers = dns.resolver.resolve(
                full_domain,
                "A"
            )

            # DNS resolve হলে list-এ রাখবে
            found_subdomains.append(full_domain)

            print(f"[FOUND] {full_domain}")

            # IP address দেখাবে
            for answer in answers:
                print(f"       IP: {answer}")


        except Exception:

            # DNS resolve না হলে
            print(f"[NOT FOUND] {full_domain}")


    # Found subdomain return করবে
    return found_subdomains


# --------------------------------
# Test
# --------------------------------

if __name__ == "__main__":

    domain = "example.com"

    results = active_dns_discovery(domain)

    print("\nActive DNS Results:")
    print(results)