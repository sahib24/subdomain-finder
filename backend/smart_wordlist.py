
import dns.resolver

from concurrent.futures import ThreadPoolExecutor


# --------------------------------
# Settings
# --------------------------------

# এক scan-এ সর্বোচ্চ candidate
MAX_CANDIDATES = 200

# DNS timeout
DNS_TIMEOUT = 0.5

# বেশি parallel DNS lookup
MAX_WORKERS = 30


# --------------------------------
# Extract words from subdomains
# --------------------------------

def extract_words(subdomains, domain):

    words = set()

    for subdomain in subdomains:

        # Target domain বাদ
        if subdomain == domain:
            continue

        # শুধু target domain-এর subdomain
        if not subdomain.endswith("." + domain):
            continue

        # Target domain অংশ বাদ
        prefix = subdomain[
            :-(len(domain) + 1)
        ]

        # Label আলাদা
        labels = prefix.split(".")

        for label in labels:

            label = label.lower().strip()

            if not label:
                continue

            # Original word
            words.add(label)

            # Hyphen থাকলে অংশগুলোও নেওয়া
            if "-" in label:

                parts = label.split("-")

                for part in parts:

                    if part:
                        words.add(part)

    return sorted(words)


# --------------------------------
# Generate smart candidates
# --------------------------------

def generate_candidates(words, domain):

    candidates = set()

    # --------------------------------
    # 1. Original words
    # --------------------------------

    for word in words:

        candidates.add(
            f"{word}.{domain}"
        )

        if len(candidates) >= MAX_CANDIDATES:
            return candidates


    # --------------------------------
    # 2. Word combinations
    # --------------------------------

    for word1 in words:

        for word2 in words:

            if word1 == word2:
                continue

            # Hyphen combination
            candidates.add(
                f"{word1}-{word2}.{domain}"
            )

            if len(candidates) >= MAX_CANDIDATES:
                return candidates

            # Direct combination
            candidates.add(
                f"{word1}{word2}.{domain}"
            )

            if len(candidates) >= MAX_CANDIDATES:
                return candidates

    return candidates


# --------------------------------
# DNS check
# --------------------------------

def check_dns(hostname):

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
                lifetime=DNS_TIMEOUT,
                raise_on_no_answer=False
            )

            return hostname

        except Exception:

            continue

    return None


# --------------------------------
# Smart Wordlist Discovery
# --------------------------------

def smart_wordlist_discovery(
    subdomains,
    domain
):

    # --------------------------------
    # Step 1: Extract words
    # --------------------------------

    words = extract_words(
        subdomains,
        domain
    )


    # --------------------------------
    # Step 2: Generate candidates
    # --------------------------------

    candidates = generate_candidates(
        words,
        domain
    )


    # --------------------------------
    # Step 3: DNS lookup
    # --------------------------------

    results = set()

    with ThreadPoolExecutor(
        max_workers=MAX_WORKERS
    ) as executor:

        checked = executor.map(
            check_dns,
            candidates
        )

        for hostname in checked:

            if hostname:

                results.add(hostname)


    # --------------------------------
    # Final result
    # --------------------------------

    return sorted(results)

