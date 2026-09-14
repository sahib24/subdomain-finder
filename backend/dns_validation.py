import dns.resolver


# --------------------------------
# DNS Validation Function
# --------------------------------

def validate_dns(subdomain):

    try:

        # DNS A record check করবে
        dns.resolver.resolve(
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