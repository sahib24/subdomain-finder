import dns.resolver


# --------------------------------
# DNS Resolver Configuration
# --------------------------------

# Use working DNS servers directly
resolver = dns.resolver.Resolver(configure=False)

resolver.nameservers = [
    "103.248.12.62",
    "103.248.12.61"
]

# DNS timeout settings
resolver.timeout = 0.5
resolver.lifetime = 0.5


# --------------------------------
# DNS Validation Function
# --------------------------------

def validate_dns(subdomain):

    try:

        # DNS A record check করবে
        resolver.resolve(
            subdomain,
            "A"
        )

        # DNS পাওয়া গেলে
        return True

    except Exception:

        # DNS না পাওয়া গেলে
        return False


# --------------------------------
# Test
# --------------------------------

if __name__ == "__main__":

    subdomain = "www.example.com"

    result = validate_dns(subdomain)

    print("DNS Valid:", result)