import struct


class DnsResponse:
    def __init__(self, raw_response):
        """
        Initializes a DNS Response structure with:
        - domain: The domain name to which the record pertains (e.g., "www.mcgill.ca").
        - rtype: The type of data in the RDATA field.
        - rclass: The class of response (expected is 0x0001, Internet class; error otherwise).
        - ttl:
        - rdlength:
        - rdata:
        - preference:
        - exchange:
        """
        self.domain = 0
        self.rtype = 0
        self.rclass = 0
        self.ttl = 0
        self.rdlength = 0
        self.rdata = 0
        self.preference = 0
        self.exchange = 0

        self.decode_response(raw_response)

    def decode_domain_name(self, raw_response, offset):
        """
        Decodes the domain name (RNAME) according to the DNS protocol.
        Each label is prefixed with its length, and the domain ends with a null byte (0x00).
        """
        labels = []
        # offset = 0

        while True:
            label_length = raw_response[offset]

            # if length = 0, then it marks the end of the domain name
            if label_length == 0:
                offset += 1
                break
            # if length >= 0xC0, then it's a pointer (compressed name)
            elif label_length >= 0xC0:
                # TODO: it's a pointer (compression)
                pointer = (
                    struct.unpack(">H", raw_response[offset : offset + 2])[0] & 0x3FFF
                )
                labels.append(self.decode_domain_name(raw_response, pointer)[0])
                offset += 2
                break
            # else, it's a normal label
            else:
                offset += 1
                labels.append(
                    raw_response[offset : offset + label_length].decode("utf-8")
                )
                offset += label_length

        decoded_name = ".".join(labels)
        return decoded_name, offset

    def decode_answer(self, ancount, raw_response, offset):
        answers = []

        for i in range(ancount):
            domain_name, offset = self.decode_domain_name(raw_response, offset)
            rtype, rclass, ttl, rdlength = struct.unpack(
                "!HHIH", raw_response[offset : offset + 10]
            )
            offset += 10

            rdata = ""
            # if 0x0001, then type-A (host-address)
            # and it's the IP-address (4 octets)
            if rtype == 0x0001:
                rdata = struct.unpack(">BBBB", raw_response[offset : offset + rdlength])
                rdata = ".".join(map(str, rdata))
            # if 0x0002, then type-NS (name server)
            # and it's the name of the server in same format as QNAME
            elif rtype == 0x0002:
                rdata, tmp_offset = self.decode_domain_name(raw_response, offset)
            # if 0x0005, then CNAME
            # and it's the name of the alias in same format as QNAME
            elif rtype == 0x0005:
                rdata, tmp_offset = self.decode_domain_name(raw_response, offset)
            # if 0x000F, MX-query (mail server)
            # then it has preference (2 bytes) and exchange (in same format as QNAME)
            elif rtype == 0x000F:
                preference = struct.unpack(">H", raw_response[offset : offset + 2])
                exchange, tmp_offset = self.decode_domain_name(raw_response, offset + 2)
                rdata = preference, exchange
            else:
                # TODO: error
                continue

            offset += rdlength
            answer = domain_name, rtype, rclass, ttl, rdlength, rdata
            answers.append(answer)

        return answers, offset

    def decode_response(self, raw_response):
        """
        Build the DNS Response structure by parsing the raw response
        """

        offset = 0

        """
        DECODE THE HEADER
        
        the header is contains:
        - id: Transaction ID
        - flags: Flags (QR, OPCODE, AA, TC, RD, RA, Z, RCODE)
        - qdcount: Number of questions
        - ancount: Number of answer records
        - nscount: Number of authority records
        - arcount: Number of additional records
        """
        id, flags, qdcount, ancount, nscount, arcount = struct.unpack(
            ">HHHHHH", raw_response[:12]
        )
        offset = 12  # update the offset to after the header in the raw response

        print(f"Transaction ID: {id}")
        print(f"Flags: {flags}")
        print(
            f"Questions: {qdcount}, Answer RRs: {ancount}, Authority RRs: {nscount}, Additional RRs: {arcount}"
        )

        """
        DECODE THE QUESTION

        the question contains:
        - domain: The domain name to which the response pertains (e.g., "www.mcgill.ca").
        - rtype: The type of query (0x0001, 0x0002, or 0x000f).
        - rclass: The class of query (default is 0x0001, Internet class).
        """

        domain, offset = self.decode_domain_name(raw_response, offset)
        rtype, rclass = struct.unpack(">HH", raw_response[offset : offset + 4])
        offset += 4

        print(f"Domain: {domain}, Type: {rtype}, Class: {rclass}")

        """
        DECODE THE ANSWERS
        store as list of answers

        an answer contains:
        - domain_name: The domain name to which the answer record pertains (e.g., "www.mcgill.ca").
        - rtype: The type of data in the RDATA field (0x0001, 0x0002, 0x0005, or 0x000f).
        - rclass: The class of response (expected is 0x0001, Internet class; error otherwise).
        - ttl: 
        - rdlength: 
        - rdata: 
        """
        answers, offset = self.decode_answer(ancount, raw_response, offset)
        print(f"ANSWER: {answers}")

        """SKIP AUTHORITY RECORDS"""
        # still need to increment offset, same format as answers
        authority, offset = self.decode_answer(nscount, raw_response, offset)
        # print(f"AUTHORITY: {authority}")

        """DECODE ADDITIONAL RECORDS"""
        # same format as answers
        additional, offset = self.decode_answer(arcount, raw_response, offset)
        print(f"ADDITIONAL: {additional}")
