import ssl
import socket


# --------------------------------
# SAN / CN Certificate Extraction
# --------------------------------

def san_cn_discovery(domain):

    results = set()

    try:
        # SSL context তৈরি করছি
        context = ssl.create_default_context()

        # Domain-এর HTTPS connection তৈরি করছি
        with socket.create_connection(
            (domain, 443),
            timeout=10
        ) as sock:

            # SSL connection তৈরি করছি
            with context.wrap_socket(
                sock,
                server_hostname=domain
            ) as ssl_socket:

                # Certificate information নিচ্ছি
                certificate = ssl_socket.getpeercert()


        # --------------------------------
        # CN থেকে hostname নেওয়া
        # --------------------------------

        subject = certificate.get("subject", [])

        for item in subject:

            for key, value in item:

                if key == "commonName":

                    # CN result-এ যোগ করছি
                    results.add(value.lower())


        # --------------------------------
        # SAN থেকে hostname নেওয়া
        # --------------------------------

        subject_alt_name = certificate.get(
            "subjectAltName",
            []
        )

        for key, value in subject_alt_name:

            if key == "DNS":

                # SAN hostname result-এ যোগ করছি
                results.add(value.lower())


        # --------------------------------
        # শুধু আমাদের domain-এর hostname রাখছি
        # --------------------------------

        filtered_results = set()

        for hostname in results:

            # Wildcard (*) সরাচ্ছি
            hostname = hostname.lstrip("*.")

            # শুধু target domain-এর hostname রাখছি
            if (
                hostname == domain
                or hostname.endswith("." + domain)
            ):

                filtered_results.add(hostname)


        # Sorted list return করছি
        return sorted(filtered_results)


    except Exception as error:

        print(f"SAN/CN error: {error}")

        return []