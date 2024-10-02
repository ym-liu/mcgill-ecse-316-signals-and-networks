class DnsHeader:
    def __init__(self, transaction_id=None):
        # If no transaction ID is provided, generate a random 16-bit number
        self.transaction_id = transaction_id if transaction_id else random.randint(
            0, 65535)
        self.flags = 0x0100  # Standard query with recursion desired
        self.qdcount = 1     # One question
        self.ancount = 0     # No answers yet
        self.nscount = 0     # No authority records
        self.arcount = 0     # No additional records

    # TODO:
    # Build and return the header as a string
    def build(self):
        return None

class DnsQuestion:
    def __init__(self, domain, qtype=0x0001, qclass=0x0001):
        self.domain = domain
        self.qtype = qtype
        self.qclass = qclass

    # TODO:
    # Build and return the question as a string
    def build(self):
        return None

class DnsQuery:
    def __init__(self, domain):
        self.header = DnsHeader()
        self.question = DnsQuestion(domain)