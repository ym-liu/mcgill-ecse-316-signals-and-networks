import struct


class DnsResponse:
    def __init__(
        self, domain, rtype, rclass, ttl, rdlength, rdata, preference, exchange
    ):
        """
        Initializes a DNS Response with:
        - domain: The domain name to which the record pertains (e.g., "www.mcgill.ca").
        - rtype: The type of data in the RDATA field.
        - rclass: The class of response (expected is 0x0001, Internet class; error otherwise).
        - ttl:
        - rdlength:
        - rdata:
        - preference:
        - exchange:
        """
        self.domain = domain
        self.rtype = rtype
        self.rclass = rclass
        self.ttl = ttl
        self.rdlength = rdlength
        self.rdata = rdata
        self.preference = preference
        self.exchange = exchange

    def decode_domain_name(self):
        """
        Decodes the domain name (RNAME) according to the DNS protocol.
        Each label is prefixed with its length, and the domain ends with a null byte (0x00).
        """
        labels = []
        offset = 0

        while True:
            length = self.domain[offset]

            # if length = 0, then it marks the end of the domain name
            if length == 0:
                offset += 1
                break
            # if length >= 0xC0, then it's a pointer (compressed name)
            elif length >= 0xC0:
                # TODO: it's a pointer (compression)
                break
            # else, it's a normal label
            else:
                offset += 1
                labels.append(self.domain[offset : offset + length].decode("utf-8"))
                offset += length

        decoded_name = ".".join(labels)
        print(f"the decoded_name is {decoded_name}")
        return decoded_name
