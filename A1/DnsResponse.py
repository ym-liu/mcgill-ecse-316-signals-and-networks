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
            length = raw_response[offset]

            # if length = 0, then it marks the end of the domain name
            if length == 0:
                offset += 1
                break
            # if length >= 0xC0, then it's a pointer (compressed name)
            elif length >= 0xC0:
                # TODO: it's a pointer (compression)
                pointer = (
                    struct.unpack("!H", raw_response[offset : offset + 2])[0] & 0x3FFF
                )
                labels.append(self.decode_domain_name(raw_response, pointer)[0])
                offset += 2
                break
            # else, it's a normal label
            else:
                offset += 1
                labels.append(raw_response[offset : offset + length].decode("utf-8"))
                offset += length

        decoded_name = ".".join(labels)
        print(f"the decoded_name is {decoded_name}")
        return decoded_name, offset

    def decode_answer(self, ancount, raw_response, offset):
        answers = []

        for i in range(ancount):
            domain_name, offset = self.decode_domain_name(raw_response, offset)
            rtype, rclass, ttl, rdlength = struct.unpack(
                "!HHIH", raw_response[offset : offset + 10]
            )
            offset += 10
            print(
                f"rtype: {rtype}\nrclass: {rclass}\n ttl: {ttl}\nrdlength: {rdlength}"
            )

            rdata = ""
            if rtype == 1:
                rdata = struct.unpack(">BBBB", raw_response[offset : offset + rdlength])
                rdata = ".".join(map(str, rdata))
                print(f"rdata: {rdata}")
            else:  # TODO: handle cname
                print(f"Answer {i + 1}: {domain_name}, Record Type: {rtype}")
                # TODO:
                # rdata = struct.unpack(">H", raw_response[offset : offset + rdlength])

            offset += rdlength
            answer = domain_name, rtype, rclass, ttl, rdlength, rdata
            answers.append(answer)

        return answers, offset

    def decode_response(self, raw_response):
        """
        Build the DNS Response structure by parsing the raw response
        """

        offset = 0

        # decode the header
        id, flags, qdcount, ancount, nscount, arcount = struct.unpack(
            ">HHHHHH", raw_response[:12]
        )

        # id: Transaction ID
        # flags: Flags (QR, Opcode, AA, TC, RD, RA, Z, RCODE)
        # qdcount: Number of questions
        # ancount: Number of answer records
        # nscount: Number of authority records
        # arcount: # Number of additional records

        print(f"Transaction ID: {id}")
        print(f"Flags: {flags}")
        print(
            f"Questions: {qdcount}, Answer RRs: {ancount}, Authority RRs: {nscount}, Additional RRs: {arcount}"
        )

        # decode the question
        offset = 12
        domain, offset = self.decode_domain_name(raw_response, offset)
        rtype, rclass = struct.unpack(">HH", raw_response[offset : offset + 4])
        offset += 4

        self.domain = domain
        self.rtype = rtype
        self.rclass = rclass

        print(f"Domain: {domain}, Type: {rtype}, Class: {rclass}")

        # decode the answer
        answers, offset = self.decode_answer(ancount, raw_response, offset)
        print(f"ANSWER: {answers}")

        # decode authority and additional records
        additional, offset = self.decode_answer(arcount, raw_response, offset)
        print(f"\nADDITIONAL: {additional}")
