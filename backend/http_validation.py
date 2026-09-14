import requests


# --------------------------------
# HTTP / HTTPS Validation
# --------------------------------

def validate_http_https(subdomain):

    # প্রথমে HTTPS check করবে
    urls = [
        f"https://{subdomain}",
        f"http://{subdomain}"
    ]

    # প্রতিটি URL check করবে
    for url in urls:

        try:

            # Website-এ request পাঠাবে
            response = requests.get(
                url,
                timeout=5,
                allow_redirects=True
            )

            # HTTP status code
            status_code = response.status_code

            # Successful response হলে
            if 200 <= status_code < 400:

                return {
                    "http_valid": True,
                    "url": url,
                    "status_code": status_code
                }

        except requests.RequestException:

            # এই URL কাজ না করলে পরের URL check করবে
            continue


    # HTTP এবং HTTPS দুটোই fail হলে
    return {
        "http_valid": False,
        "url": None,
        "status_code": None
    }


# --------------------------------
# Test
# --------------------------------

if __name__ == "__main__":

    subdomain = "www.example.com"

    result = validate_http_https(subdomain)

    print(result)