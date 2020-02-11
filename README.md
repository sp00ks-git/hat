![Python 2.7 and 3 compatible](https://img.shields.io/badge/python-2.7%2C%203.x-blue.svg)
![PyPI version](https://img.shields.io/pypi/v/bloodhound.svg)
# HAT - Hashcat Automation Tool
An automated Hashcat tool for common wordlists and rules to speed up the process of cracking hashes during engagements.
HAT is simply a wrapper for Hashcat (with a few extra features) - https://hashcat.net, however I take no credit for that superb tool.

***Linux support only***  

Supported Hashes:

NTLMv2 (NTHASH) -> NetNTLMv1 -> NetNTLMv2 -> MD5 -> SHA-512 -> RC4-HMAC-MD5 (Kerberoasting)


Features:

* Straight Wordlist testing from publicy known breaches (dependant on your wordlists)
* Straight Wordlists using the Oxford Dictionary incrmementing through various combinations
* Common Rule sets used in corporate environments
* Smart ordering of compromised hashes alphabetically in (Username::Domain:Hash:Password) format.
* Visual hash cracking status showing you how many hashes you have left to crack 
* Cewl Integration for finding specific words common to the business not found in dictionaries or breached lists
* Rsmangler Integration for finding permutations of a specific word that the firm might be using. (includes incrementing various combinations on either side)


The directory structure that HAT expects is.. (of course you can just ammend the code to your own needs)

-> /opt/worliststs/rockyou.txt  
-> /opt/wordlists/1GB-4GB/  
-> /opt/wordlists/4GB+/  
-> /opt/wordlists/english-words/  
-> /opt/wordlists/merged_list/

Suggested Wordlists download links (HTTP) - working as of 14/10/2019   
* https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt (~14,300,000 words)  
* https://github.com/dwyl/english-words/blob/master/words.txt (~466,000 words) 
* http://storage.aircrack-ng.org/users/PsycO/PsycOPacKv2.rar (1.4GB)  
* https://download.g0tmi1k.com/wordlists/large/sp00ks_merged_file_uniq.7z (2.7 GB - Compressed)  
* https://srv-file4.gofile.io/download/NHXEGm/sp00ks_merged_file_uniq.7z (8.2 GB - mirror)  
* https://crackstation.net/files/crackstation-human-only.txt.gz (4.2 GB)  
* https://download.g0tmi1k.com/wordlists/large/crackstation.txt.gz (4.5 GB)  
* https://download.g0tmi1k.com/wordlists/large/10-million-combos.zip (8.8 GB)  
* https://download.g0tmi1k.com/wordlists/large/36.4GB-18_in_1.lst.7z (48.4 GB)  
* https://download.g0tmi1k.com/wordlists/large/b0n3z-wordlist-sorted-something.tar.gz (165 GB)  
* http://download1568.mediafire.com/yuh4jmehecwg/8oazhwqzexid771/WordlistBySheez_v8.7z (166.17 GB)  


Thanks to:

Cewl - @digininja         - https://github.com/digininja/CeWL   
Passphrases - @initstring - https://github.com/initstring/passphrase-wordlist   
Rsmangler - @digininja    - https://github.com/digininja/RSMangler   

