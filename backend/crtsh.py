import requests  # Internet API request করার জন্য


def crtsh_discovery(domain):
    # crt.sh API URL তৈরি করছি
    url = f"https://crt.sh/?q=%.{domain}&output=json"

    try:
        # crt.sh থেকে certificate data নিচ্ছি
        response = requests.get(url, timeout=20)

        # HTTP error হলে exception হবে
        response.raise_for_status()

        # JSON data Python list/dictionary-তে convert করছি
        certificates = response.json()

        results = set()  # Duplicate hostname বাদ দেওয়ার জন্য set

        # প্রতিটি certificate নিয়ে কাজ করছি
        for certificate in certificates:

            # Certificate-এর name_value field নিচ্ছি
            names = certificate.get("name_value", "")

            # এক certificate-এ একাধিক hostname থাকতে পারে
            for name in names.splitlines():

                # Extra space এবং wildcard (*) সরাচ্ছি
                name = name.strip().lower().lstrip("*.")

                # শুধু আমাদের domain-এর hostname রাখছি
                if name == domain or name.endswith("." + domain):
                    results.add(name)

        # Sorted list হিসেবে result return করছি
        return sorted(results)

    except requests.RequestException as error:
        # Network/API error হলে empty list return করবে
        print(f"crt.sh error: {error}")
        return []