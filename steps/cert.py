import logging
import os
from OpenSSL import crypto


def generate_ca(**kwargs):
    """
    Gegerate CA key pair for testing

    :param kwargs: parameters for generate ca key pair
    :return: ca and private key object
    :rtype: tuple
    """
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 4096)

    ca = crypto.X509()

    subjects = ["C", "ST", "L", "O", "OU", "CN", "emailAddress"]

    for sub in subjects:
        if sub in kwargs:
            setattr(ca.get_subject(), sub, kwargs[sub])

    ca.set_issuer(ca.get_subject())
    ca.set_pubkey(key)
    ca.set_version(kwargs.get("version", 0))
    ca.set_serial_number(kwargs.get("serial_number", 1000))
    ca.gmtime_adj_notBefore(kwargs.get("adj_notBefore", 0))
    ca.gmtime_adj_notAfter(kwargs.get("adj_notAfter", 31536000))

    extensions = kwargs.get("extensions", [])
    for extension in extensions:
        if "typename" not in extension:
            logging.warn("Typename is not defined, "
                         "skip this item.\n%s" % extension)
            pass
        args = [extension.get("typename"), extension.get("critical", False),
                extension.get("value", "")]
        sub_iss = {}
        if extension.get("subject"):
            sub_iss["subject"] = eval(extension["subject"])

        if extension.get("issuer"):
            sub_iss["issuer"] = eval(extension["issuer"])

        ca.add_extensions([crypto.X509Extension(*args, **sub_iss)])

    ca.sign(key, kwargs.get("digest", "sha1"))

    return ca, key


def generate_cert(ca, ca_key, **kwargs):
    """
    Generate cert, csr and key pairs for testing

    :param ca: ca
    :type ca: X509 object
    :param ca_key:
    :type ca_key: PKey object
    :param kwargs: parameters for generate ca key pair
    :return: cert, csr and private key object
    :rtype: tuple
    """
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 4096)

    csr = crypto.X509Req()

    subjects = ["C", "ST", "L", "O", "OU", "CN", "emailAddress"]

    for sub in subjects:
        if sub in kwargs:
            setattr(csr.get_subject(), sub, kwargs[sub])

    csr.set_pubkey(key)
    csr.sign(ca_key, kwargs.get("digest_csr", "sha1"))

    cert = crypto.X509()

    cert.set_issuer(ca.get_subject())
    cert.set_pubkey(csr.get_pubkey())
    cert.set_subject(csr.get_subject())
    cert.set_version(kwargs.get("version", 0))
    cert.set_serial_number(kwargs.get("serial_number", 100))
    cert.gmtime_adj_notBefore(kwargs.get("adj_notBefore", 0))
    cert.gmtime_adj_notAfter(kwargs.get("adj_notAfter", 31536000))

    extensions = kwargs.get("extensions", [])
    for extension in extensions:
        if "typename" not in extension:
            logging.warn("Typename is not defined, "
                         "skip this item.\n%s" % extension)
            pass
        tmp = [extension.get("typename"), extension.get("critical", False),
               extension.get("value", "")]
        args = []
        for arg in tmp:
            if isinstance(arg, unicode):
                args.append(str(arg))
            else:
                args.append(arg)

        sub_iss = {}
        if extension.get("subject"):
            sub_iss["subject"] = eval(extension["subject"])

        if extension.get("issuer"):
            sub_iss["issuer"] = eval(extension["issuer"])

        cert.add_extensions([crypto.X509Extension(*args, **sub_iss)])

    cert.sign(ca_key, kwargs.get("digest", "sha1"))

    return cert, key, csr


def dump_to_file(filename, filetype, cert, cert_type):
    """
    Dump a certificate object to a file

    :param filename: File to store the cert context
    :type filename: str
    :param filetype: Crypto file type, should be one of FILETYPE_PEM,
                     FILETYPE_PEM and FILETYPE_TXT
    :type filetype: str
    :param cert: The certificate object to dump
    :type cert: PKey, X509 or X509Req
    :param cert_type: The certificate target type want to be dumped. Such as
                      privatekey, certificate, certificate_request and so on
    :type cert_type: str
    """
    dump_func = getattr(crypto, "dump_%s" % cert_type)
    file_path = os.path.dirname(filename)
    if not os.path.exists(file_path):
        os.mkdir(file_path)
    txt = dump_func(getattr(crypto, filetype), cert)
    with open(filename, 'w') as f:
        f.write(txt)


def generate_etcd_ca():
    """
    Generate ca key pairs fit for etcd test request

    :return: ca and private key object
    :rtype: tuple
    """
    ca, key = generate_ca(O="etcd-test", version=2,
                          extensions=[{"typename": "basicConstraints",
                                       "critical": True,
                                       "value": "CA:TRUE"},
                                      {"typename": "keyUsage",
                                       "critical": True,
                                       "value": "keyCertSign"},
                                      {"typename": "subjectKeyIdentifier",
                                       "value": "hash",
                                       "subject": "ca"},
                                      {"typename": "authorityKeyIdentifier",
                                       "value": "keyid:always",
                                       "issuer": "ca"},
                                      ])
    return ca, key


def generate_etcd_cert(ca, ca_key, ip="127.0.0.1"):
    """
    Generate cert key pairs fit for etcd test request

    :param ca: ca
    :type ca: X509 object
    :param ca_key:
    :type ca_key: PKey object
    :param ip: ip or host name.
    :type ip: str
    :return: cert, csr and private key object
    :rtype: tuple
    """
    extensions = [{"typename": "extendedKeyUsage",
                   "value": "serverAuth,clientAuth"},
                  {"typename": "subjectKeyIdentifier",
                   "value": "hash", "subject": "cert"},
                  {"typename": "authorityKeyIdentifier",
                   "value": "keyid:always",
                   "issuer": "ca"},
                  {"typename": "subjectAltName",
                   "value": "IP:%s" % ip}]

    cert, key, _ = generate_cert(ca, ca_key, CN=ip, version=2,
                                 extensions=extensions)
    return cert, key
