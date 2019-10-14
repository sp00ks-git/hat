# hat-hashcat-automation-tool
An Automated Hashcat Tool for common wordlists and rules to speed up the process of cracking hashes during engagements.
HAT is simple a wrapper for Hashcat - https://hashcat.net and I take no credit for that superb tool.

Supported Hashes:

NTLMv2 (NTHASH) -> NetNTLMv1 -> NetNTLMv2 -> MD5 -> SHA-512 -> RC4-HMAC-MD5 (Kerberoasting)


Features:

* Straight Wordlist testing from publicy known breaches
* Straight Wordlists using the Oxford Dictionary incrmementing through various combinations
* Common Rule sets used in corporate environments
* Smart ordering of compromised hashes alphabetically in (Username::Domain:Hash:Password) format.
* Visual realtime hash cracking status showing you how many hashes you have left to crack 
* Cewl Integration for finding specific words common to the business not found in dictionaries or breached lists
* Rsmangler Integration for finding permutations of a specific word that the firm might be using. (includes incrementing various combinations on either side)


The directory structure that HAT expects is.. (of course you can just ammend the code to your own needs)

/opt/wordlists/1GB-4GB/  
/opt/wordlists/4GB+/  
/opt/wordlists/english-words/  
/opt/wordlists/merged_list/  
