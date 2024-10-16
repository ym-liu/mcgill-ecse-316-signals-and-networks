# mcgill-ecse-316-signals-and-networks
Assignments for ECSE 316 Signals and Networks course offered in Fall 2024 at McGill University

## Authors ##
Dmytro Martyniuk

YuMeng Liu

## Instructions: How to use the program ##

Requires any version of python 3.0+
1. Open a terminal.
2. Clone the repository: ``` git clone https://github.com/ym-liu/mcgill-ecse-316-signals-and-networks.git ```
3. For a simple query type:
 ```python A1/dnsClient.py -t [timeout] -r [max-retries] @<server> <name>```
in the terminal
4. If a different request type mail server or name server:

   
       For mail server python A1/dnsClient.py -t [timeout] -r [max-retries] -mx @<server> <name>
       
       For name server python A1/dnsClient.py -t [timeout] -r [max-retries] -ns @<server> <name>  

## Argumments ##
- server (required) is the IPv4 address of the DNS server, in a.b.c.d. format
- name (required) is the domain name to query for.
- timeout (optional) gives how long to wait, in seconds, before retransmitting an unanswered query. Default value: 5.
- max-retries(optional) is the maximum number of times to retransmit an unanswered query before giving up. Default value: 3.
- port (optional) is the UDP port number of the DNS server. Default value: 53.
- -mx or -ns flags (optional) indicate whether to send a MX (mail server) or NS (name server)query. At most one of these can be given, and if neither is given then the client will send a type A (IP address) query.

## Python Version Used for Testing/Writing the Program ##

```Python 3.11.1```
