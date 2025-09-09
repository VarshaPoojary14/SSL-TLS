import ssl
import socket
from datetime import datetime, timezone
from OpenSSL import crypto

def get_certificate_info(hostname):
    context = ssl.create_default_context()
    with socket.create_connection((hostname, 443)) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            cert = ssock.getpeercert(True)
            return ssl.DER_cert_to_PEM_cert(cert)

def parse_certificate(cert_pem):
    cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_pem)
    return {
        'not_before': datetime.strptime(cert.get_notBefore().decode('utf-8'), "%Y%m%d%H%M%SZ").replace(tzinfo=timezone.utc),
        'not_after': datetime.strptime(cert.get_notAfter().decode('utf-8'), "%Y%m%d%H%M%SZ").replace(tzinfo=timezone.utc),
        'issuer': {k.decode(): v.decode() for k, v in cert.get_issuer().get_components()},
        'subject': {k.decode(): v.decode() for k, v in cert.get_subject().get_components()},
    }

def check_certificate(cert_info):
    current_time = datetime.now(timezone.utc)
    is_valid = cert_info['not_before'] <= current_time <= cert_info['not_after']
    return is_valid

def main():
    hostname = input("Enter the hostname (e.g., example.com): ")
    try:
        cert_pem = get_certificate_info(hostname)
        cert_info = parse_certificate(cert_pem)

        is_valid = check_certificate(cert_info)

        print(f"\nCertificate for {hostname}:")
        print(f"  Valid: {'Yes' if is_valid else 'No'}")
        print(f"  Not Before: {cert_info['not_before']}")
        print(f"  Not After:  {cert_info['not_after']}")
        print(f"  Issuer: {cert_info['issuer']}")
        print(f"  Subject: {cert_info['subject']}")

    except Exception as e:
        print(f"Error fetching certificate: {e}")

if __name__ == "__main__":
    main()
