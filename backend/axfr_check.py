import dns.resolver
import dns.query
import dns.zone


def get_nameservers(domain):

    nameservers = []

    try:
        answers = dns.resolver.resolve(
            domain,
            "NS",
            lifetime=3
        )

        for answer in answers:
            nameserver = answer.to_text().rstrip(".")
            nameservers.append(nameserver)

    except Exception:
        pass

    return nameservers


def check_axfr(domain):

    results = []

    nameservers = get_nameservers(domain)

    for nameserver in nameservers:

        try:
            # Nameserver-এর IP বের করা
            ns_answers = dns.resolver.resolve(
                nameserver,
                "A",
                lifetime=3
            )

            for ns_ip in ns_answers:

                try:
                    # AXFR request
                    zone = dns.zone.from_xfr(
                        dns.query.xfr(
                            str(ns_ip),
                            domain,
                            timeout=5
                        )
                    )

                    records = []

                    for name, node in zone.nodes.items():
                        hostname = str(name)

                        if hostname == "@":
                            hostname = domain
                        else:
                            hostname = (
                                f"{hostname}.{domain}"
                            )

                        records.append(hostname)

                    results.append({
                        "nameserver": nameserver,
                        "ip": str(ns_ip),
                        "transfer_allowed": True,
                        "records": sorted(
                            set(records)
                        )
                    })

                except Exception:

                    results.append({
                        "nameserver": nameserver,
                        "ip": str(ns_ip),
                        "transfer_allowed": False,
                        "records": []
                    })

        except Exception:
            continue

    return results