import requests


# --------------------------------
# Passive DNS Discovery
# --------------------------------

def passive_dns_discovery(domain):

    results = set()

    # DNS history/public records পাওয়ার জন্য HackerTarget API
    url = f"https://api.hackertarget.com/hostsearch/?q={domain}"

    try:

        # API request
        response = requests.get(
            url,
            timeout=20
        )

        # HTTP error হলে exception
        response.raise_for_status()

        # API response text
        data = response.text

        # প্রতিটি line আলাদা করছি
        lines = data.strip().splitlines()

        # প্রতিটি DNS record নিয়ে কাজ করছি
        for line in lines:

            # Format সাধারণত:
            # subdomain.domain.com,IP
            parts = line.split(",")

            if len(parts) >= 1:

                hostname = parts[0].strip().lower()

                # শুধু target domain-এর hostname রাখছি
                if (
                    hostname == domain
                    or hostname.endswith("." + domain)
                ):
                    results.add(hostname)

        # Sorted list return
        return sorted(results)

    except requests.RequestException as error:

        print(f"Passive DNS error: {error}")

        return []