import dns.resolver


RECORD_TYPES = [
    "A",
    "AAAA",
    "CNAME",
    "MX",
    "NS",
    "TXT"
]


# Use working DNS servers directly.
# This avoids the local router DNS timeout.
resolver = dns.resolver.Resolver(configure=False)

resolver.nameservers = [
    "103.248.12.62",
    "103.248.12.61"
]

# DNS timeout settings
resolver.timeout = 0.5
resolver.lifetime = 0.5


def get_dns_records(hostname):

    records = {}

    for record_type in RECORD_TYPES:

        try:
            answers = resolver.resolve(
                hostname,
                record_type,
                raise_on_no_answer=False
            )

            values = []

            for answer in answers:
                values.append(answer.to_text())

            records[record_type] = values

        except Exception:
            records[record_type] = []

    return records