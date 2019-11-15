#!/usr/bin/python2.7
'''
#Release Date - 14/10/2019
#Latest update - Pre-Release
#Last Modified - 14/10/2019
#Python Hashcat Automated Password Recovery
#Version 1.0
#Currenty working in python 2.7
#Update to python 3 (to do)
'''

#Module Imports
import fnmatch
import os
import readline
import subprocess
import sys

#Define Colours
def prRed(prt):
    print"\033[91m {}\033[00m" .format(prt)

def prGreen(prt):
    print"\033[92m {}\033[00m" .format(prt)

def prYellow(prt):
    print"\033[93m {}\033[00m" .format(prt)

def prLightPurple(prt):
    print"\033[94m {}\033[00m" .format(prt)

def prPurple(prt):
    print"\033[95m {}\033[00m" .format(prt)

def prCyan(prt):
    print"\033[96m {}\033[00m" .format(prt)

def prLightGray(prt):
    print"\033[97m {}\033[00m" .format(prt)

'''
More Colours Reference Table
print('\033[32m' + 'Bright Green' + '\033[0m')
print('\033[31m' + 'Red' + '\033[0m')
print('\033[33m' + 'Yellow' + '\033[0m')
print('\033[34m' + 'Blue' + '\033[0m')
print('\033[35m' + 'Purple' + '\033[0m')
print('\033[44m' + 'Cyan' + '\033[0m')
print('\033[45m' + 'Purple_back-white-text' + '\033[0m')
print('\033[46m' + 'Cyan_back-white-text' + '\033[0m')
print('\033[47m' + 'Grey_back-white-text' + '\033[0m')
print('\033[48m' + 'Black-back_white-text' + '\033[0m')
print('\033[41m' + 'Red-back-White-text' + '\033[0m')
print('\033[42m' + 'Green-back-white-text' + '\033[0m')
print('\033[43m' + 'Yellow-back-White-text' + '\033[0m')
'''

ALL_MENU = False

#Both Values are set to false on program start.
#This is used to trigger the pot file and hash upload functionality.
FILE_HASH_BOOLEAN = False
SINGLE_HASH_BOOLEAN = False

#Used to allow multiple tests via the menu with the same pot file already selected.
#Note Global pot_boolean resides inside the pot_function() function block.
POT_BOOLEAN = False

#Used for supporting the cewl wordlists if standard wordlists are not getting results
CEWL_BOOLEAN = False

#Initally Clear the Screen
os.system('clear')

#AWK command - AWKward command that doesn't sit well when called idrectly.
AWK = " " + "awk '!x[$0]++'" + " "

#Declare Paths
#First make the hat absolute path dynamic and go up one level to accomodate each related path
HASHCAT_PATH = os.getcwd()
#Set the wordlist directory to where you're wordlists are...
WORDLIST_DIRECTORY = "/opt/wordlists"
L00T_POT_DIR = os.path.join(HASHCAT_PATH, 'l00t')
RULES_DIR = os.path.join(HASHCAT_PATH, 'rules')
HASH_UPLOAD_DIR = os.path.join(HASHCAT_PATH, 'hash_upload')
CEWL_UPLOAD_DIR = os.path.join(HASHCAT_PATH, 'cewl_wordlists')
TOOLS_DIR = os.path.join(HASHCAT_PATH, 'tools')
RSMANGLER_UPLOAD_DIR = os.path.join(HASHCAT_PATH, 'rsmangler')
RSMANGLER_INPUT_DIR = os.path.join(RSMANGLER_UPLOAD_DIR, 'input')
RSMANGLER_OUTPUT_DIR = os.path.join(RSMANGLER_UPLOAD_DIR, 'output')

#Banner
def banner():
    os.system('clear')
    print""
    prGreen("    @@@,@&&&&@@@@@@@@@@                                                         ")
    prGreen("    @@@@@@&&&&@@@@@@@@@            `7MMF'  `7MMF'      db      MMP''MM''YMM     ")
    prGreen("     @@@@@&&&&@@@@@@@@@              MM      MM       ;MM:     P'   MM   `7     ")
    prGreen("     @@@@@@&&&&@@@@@@@@              MM      MM      ,V^MM.         MM          ")
    prGreen("      @@@@@&&&&@@@@@@@@              MMmmmmmmMM     ,M  `MM         MM          ")
    prGreen("      @@@@@@&&&&@@@@@@@@             MM      MM     AbmmmqMA        MM          ")
    prGreen("       @@@@@&&&&@@@@@@@@  .          MM      MM    A'     VML       MM          ")
    prGreen("       @@@@@&&&&&@@@@@@&&&@@@      .JMML.  .JMML..AMA.   .AMMA.   .JMML.        ")
    prGreen("   %@@@@@@@@@&&@@@@@&&&@@@@@@                                                   ")
    prGreen(" @@@@@@@@@@@@@@@@&&&@@@@@@@        --==The Hashcat Automation Toolset==--       ")
    prGreen(" @@@@@@@@@@@@@@&&                           Created By @__sp00ks__              ")
    prGreen("  %@@@@@@@@&                          https://github.com/sp00ks-git/hat         ")
    print""

#Pot File - Create a New Potfile when using a single wordlist or the file upload functionality.
def pot_function():
    global POT
    global POT_BOOLEAN
    global HASH_PATH_AND_NAME
    global HASH_ABS_PATH
    if SINGLE_HASH_BOOLEAN:
        POT = SINGLE_HASH_FILE_NAME.lower()
        HASH_PATH_AND_NAME = os.path.join(os.getcwd(), SINGLE_HASH_FILE_NAME)
    else:
        HASH_PATH_AND_NAME = HASH_ABS_PATH
        POT = HASH_INPUT.lower()
    POT = POT + '.pot' #No need to create a file here as hashcat will automajically make one
    POT_BOOLEAN = True
    return

#Hash Mode Selection Menu
def hash_mode_menu():
    global HASH_TYPE
    global HM_ANSWER
    loop = True
    while loop:
        print"Input Hash Mode To Crack"
        prCyan("\t(0) NTLM {AKA NTHASH} - A SAM Database Hash - NTDS.dit - {PTH Possible}")
        prGreen("\t\tNTLM Example - 49a9a1e1f0127c7d70d750349d0bc09a - order (LM-NT)")
        prLightPurple("\t(1) Net-NTLMv1 Hash {AKA NTLMv1}")
        prGreen("\t\tNet-NTLMv1 Hash Example - u4-netntlm::kNS:338d08f8e26de93300000000000000000000000000000000:\n\t\t9526fb8c23a90751cdd619b6cea564742e1e4bf33006ba41:cb8086049ec4736c")
        prCyan("\t(2) Net-NTLMv2 Hash {AKA NTLMv2}")
        prGreen("\t\tNet-NTLMv2 Hash Example - admin::N46iSNekpT:08ca45b7d7ea58ee:88dcbe4446168966a153a0064958dac6:\n\t\t5c7830315c7830310000000000000b45c67103d07d7b95acd12ffa11230e0000000052920b85f78d013c31cdb3b92f5d765c783030")
        prLightPurple("\t(3) MD5 Unix {Shadow File Format}")
        prGreen("\t\tMD5 Unix Example - $1$28772684$iEwNOgGugqO9.bIz5sk8k/")
        prCyan("\t(4) SHA-512 Unix {Shadow File Format}")
        prGreen("\t\tSHA-512 Example - $6$52450745$k5ka2p8bFuSmoVT1tzOyyuaREkkKBcCNqoDKzYiJL9RaE8yMnPgh2XzzF0NDrUhgrcLwg78xs1w5pJiypEdFX/")
        prLightPurple("\t(5) Kerberos 5 TGS-REP etype 23 - Kerberoasting Format")
        prGreen("\t\tKerberos 5 TGS-REP etype 23 (RC4-HMAC-MD5)")
        prCyan("\t\tRC4-HMAC-MD5 Example - $krb5tgs$23$*user$realm$test/spn*$b548eb06bae0eead3b7f639178a90cf24d9a1<snip>")
        prRed("\t(6) Back")
        HM_ANSWER = raw_input(": ")
        if HM_ANSWER == "0":   #NTLM aka NTHASH
            HASH_TYPE = '1000'
            return
        elif HM_ANSWER == "1": #Net-NTLMv1 aka NTLMv1
            HASH_TYPE = '5500'
            return
        elif HM_ANSWER == "2": #Net-NTLMv2 aka NTLMv2
            HASH_TYPE = '5600'
            return
        elif HM_ANSWER == "3": #MD5 Unix
            HASH_TYPE = '0'
            return
        elif HM_ANSWER == "4": #SHA-512 Unix
            HASH_TYPE = '1800'
            return
        elif HM_ANSWER == "5": #Kerberos 5 TGS-Rep etype 23 --> RC4-HMAC-MD5
            HASH_TYPE = '13100'
            return
        elif HM_ANSWER == "6":
            crack_menu()
        else:
            raw_input("You did not give a valid answer, press any key to try again \n")
            os.system('clear')
            print''
            banner()

#Straight Wordlist_walk
def wordlist_walk():
    for dirpath, dirnames, files in os.walk(WORDLIST_DIRECTORY):
        for wordlist_filename in files:
            abs_wordlist = (os.path.join(dirpath, wordlist_filename))
            hc_cmd = ['hashcat', '-a', '0', '-m', HASH_TYPE, HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), abs_wordlist, '-w', '3', '-O']
            subprocess.call(hc_cmd)
    if HM_ANSWER == '0' or HM_ANSWER == '1' or HM_ANSWER == '2':
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
        os.system('clear')
    else:
        os.system('clear')

#Rule Set Walk
def rule_set_walk():
    exten = '*.rule'
    for root, dirs, files in os.walk(RULES_DIR):
        for filename in fnmatch.filter(files, exten):
            abs_rule_set = (os.path.join(root, filename))
            hc_cmd = ['hashcat', '-a', '0', '-m', HASH_TYPE, HASH_PATH_AND_NAME, '-w', '3', '-O', '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), SINGLE_WORDLIST, '-r', abs_rule_set]
            subprocess.call(hc_cmd)
    if HM_ANSWER == '0' or HM_ANSWER == '1' or HM_ANSWER == '2':
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
        os.system('clear')
    else:
        os.system('clear')

#File Unique menu
#Used to remove any duplicate entries in files
#also helps to keep down the .format3 file
def file_unique_menu():
    lines_seen = set() # holds lines already seen
    outfile = open("out.txt", "w")
    for line in open("input.txt", "r"):
        if line not in lines_seen: # if not a duplicate
            outfile.write(line)
            lines_seen.add(line)
            outfile.close()

#Rsmangler Rule Set - {5 ANY Characters RIGHT --> LEFT incremental}
def rsmangler_rule_set():
    hash_answer()
    hc = ['hashcat', '-a', '0', '-m', HASH_TYPE, HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, pot), SINGLE_WORDLIST, '-r', os.path.join(RULES_DIR, 'OneRuleToRuleThemAll.rule'), '-w', '3', '-O']
    subprocess.call(hc)
    #Right Side
    hc1 = ['hashcat', '-a', '6', HASH_TYPE, HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), SINGLE_WORDLIST, '?a?a?a?a', '-w', '3', '-O', '--increment']
    subprocess.call(hc1)
    if HM_ANSWER == '0' or HM_ANSWER == '1' or HM_ANSWER == '2':
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
        os.system('clear')
    else:
        os.system('clear')
    #LeftSide
    hc2 = ['hashcat', '-a', '7', '-m', HASH_TYPE, HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '?a?a?a?a', SINGLE_WORDLIST, '-w', '3', '-O', '--increment']
    subprocess.call(hc2)
    if HM_ANSWER == '0' or HM_ANSWER == '1' or HM_ANSWER == '2':
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
        os.system('clear')
    else:
        os.system('clear')

#Crack Menu 0 - Try all words lists merged List -  Common Credentials
#Updated and merged all smaller wordlists into one file for more effcient testing
#(find . -name "*.txt" | xarg cat >> ./mergedfile.txt)
def crack_menu_0():
    global DEFAULT_CEWL_FILE_OUTPUT
    global CEWL_BOOLEAN
    global FILE_HASH_BOOLEAN
    global POT_BOOLEAN
    global SINGLE_WORDLIST
    WORDLIST_DIRECTORY = "/opt/wordlists" #Needed to reset the wordlist directory.
    if CEWL_BOOLEAN and FILE_HASH_BOOLEAN or SINGLE_HASH_BOOLEAN and CEWL_BOOLEAN:
        SINGLE_WORDLIST = DEFAULT_CEWL_FILE_OUTPUT
    else:
        SINGLE_WORDLIST = os.path.join(WORDLIST_DIRECTORY, 'merged_list/sp00ks_merged_file_uniq.txt')
    if ALL_MENU:
        pot_function()
    else:
        hash_mode_menu()
        pot_function()
    hc_cmd1 = ['hashcat', '-a', '0', '-m', HASH_TYPE, HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), SINGLE_WORDLIST, '-w', '3', '-O']
    subprocess.call(hc_cmd1)
    if HM_ANSWER == '0' or HM_ANSWER == '1':
        hc_cmd2 = ['hashcat', '-m', HASH_TYPE, '-a', '0', '--username', '--session', 'all', '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME]
        subprocess.call(hc_cmd2)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
    elif HM_ANSWER == '2':
        hc_cmd3 = ['hashcat', '-m', HASH_TYPE, '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--session', 'all']
        subprocess.call(hc_cmd3)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
    else:
        return

#Crack Menu 1 - Try all words lists between 1GB < 4GB
def crack_menu_1():
    global WORDLIST_DIRECTORY
    WORDLIST_DIRECTORY = "/opt/wordlists" # Needed to reset the wordlist directory.
    WORDLIST_DIRECTORY = os.path.join(WORDLIST_DIRECTORY, '1GB-4GB')
    if ALL_MENU:
        pot_function()
        wordlist_walk()
        os.system('clear')
        return
    else:
        hash_mode_menu()
        pot_function()
        wordlist_walk()
        os.system('clear')
        return

#Crack Menu 2 - Try crackstation list (15GB)
def crack_menu_2():
    WORDLIST_DIRECTORY = "/opt/wordlists" # Needed to reset the wordlist directory.
    if ALL_MENU:
        pot_function()
    else:
        hash_mode_menu()
        pot_function()
    if CEWL_BOOLEAN and FILE_HASH_BOOLEAN or SINGLE_HASH_BOOLEAN and CEWL_BOOLEAN:
        SINGLE_WORDLIST = DEFAULT_CEWL_FILE_OUTPUT
    else:
        SINGLE_WORDLIST = os.path.join(WORDLIST_DIRECTORY, '4GB+/crackstation.txt')
    hc_cmd1 = ['hashcat', '-a', '0', '-m', HASH_TYPE, HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), SINGLE_WORDLIST, '-w', '3', '-O']
    subprocess.call(hc_cmd1)
    hc_cmd2 = ['hashcat', '-a', '0', '-m', HASH_TYPE, HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), os.path.join(WORDLIST_DIRECTORY, '4GB+/hashes.org-2019.txt'), '-w', '3', '-O']
    subprocess.call(hc_cmd2)
    if HM_ANSWER == '0' or HM_ANSWER == '1':
        hc_cmd3 = ['hashcat', '-m', HASH_TYPE, '-a', '0', '--username', '--session', 'all', '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME]
        subprocess.call(hc_cmd3)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
    elif HM_ANSWER == '2':
        hc_cmd4 = ['hashcat', '-m', HASH_TYPE, '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--session', 'all']
        subprocess.call(hc_cmd4)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
    else:
        return

#Crack_Menu 3
def crack_menu_3():
    WORDLIST_DIRECTORY = "/opt/wordlists" # Needed to reset the wordlist directory.
    if ALL_MENU:
        pot_function()
    else:
        hash_mode_menu()
        pot_function()
    if CEWL_BOOLEAN and FILE_HASH_BOOLEAN or SINGLE_HASH_BOOLEAN and CEWL_BOOLEAN:
        SINGLE_WORDLIST = DEFAULT_CEWL_FILE_OUTPUT
    else:
        SINGLE_WORDLIST = os.path.join(WORDLIST_DIRECTORY, '4GB+/weakpass_2p')
    hc_cmd1 = ['hashcat', '-a', '0', '-m', HASH_TYPE, HASH_ABS_PATH, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), SINGLE_WORDLIST, '-w', '3', '-O']
    subprocess.call(hc_cmd1)
    if HM_ANSWER == '0' or HM_ANSWER == '1':
        hc_cmd2 = ['hashcat', '-m', HASH_TYPE, '-a', '0', '--username', '--session', 'all', '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_ABS_PATH]
        subprocess.call(hc_cmd2)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
    elif HM_ANSWER == '2':
        hc_cmd3 = ['hashcat', '-m', HASH_TYPE, '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_ABS_PATH, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--session', 'all']
        subprocess.call(hc_cmd3)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
    else:
        return

#Crack Menu 4 - Try all words lists 4GB+ - (will take a while to cache each wordlist prior to testing)
def crack_menu_4():
    global WORDLIST_DIRECTORY
    WORDLIST_DIRECTORY = "/opt/wordlists" # Needed to reset the wordlist directory.
    WORDLIST_DIRECTORY = os.path.join(WORDLIST_DIRECTORY, '4GB+')
    if ALL_MENU:
        pot_function()
        wordlist_walk()
        os.system('clear')
        return
    else:
        hash_mode_menu()
        pot_function()
        wordlist_walk()
        os.system('clear')
        return

#Crack Menu 5 - Oxford Dic, capital letter, upto 4 characters, incrementally - RIGHT SIDE
def crack_menu_5():
    AWK = "awk '!x[$0]++'"
    WORDLIST_DIRECTORY = "/opt/wordlists" # Needed to reset the wordlist directory.
    SINGLE_WORDLIST = os.path.join(WORDLIST_DIRECTORY, 'english-words/words.txt')
    if ALL_MENU:
        pot_function()
        os.system('clear')
    else:
        hash_mode_menu()
        pot_function()
        os.system('clear')
    hc = ['hashcat', '-a', '6', '-m', HASH_TYPE, HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), SINGLE_WORDLIST, '?a?a?a?a', '-w', '3', '-O', '--increment']
    subprocess.call(hc)
    if HM_ANSWER == '0' or HM_ANSWER == '1':
        hc_cmd2 = ['hashcat', '-m', HASH_TYPE, '-a', '0', '--username', '--session', 'all', '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME]
        subprocess.call(hc_cmd2)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
    elif HM_ANSWER == '2':
        hc_cmd3 = ['hashcat', '-m', HASH_TYPE, '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--session', 'all']
        subprocess.call(hc_cmd3)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
    else:
        return

#Crack Menu 6 - Oxford Dic, capital letter, upto 4 characters, incrementally - LEFT SIDE
def crack_menu_6():
    AWK = "awk '!x[$0]++'"
    WORDLIST_DIRECTORY = "/opt/wordlists" # Needed to reset the wordlist directory.
    SINGLE_WORDLIST = os.path.join(WORDLIST_DIRECTORY, 'english-words/words_first_letter_upper.txt')
    if ALL_MENU:
        pot_function()
    else:
        hash_mode_menu()
        pot_function()
    os.system('clear')
    hc = ['hashcat', '-a', '7', '-m', HASH_TYPE, HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '?a?a?a?a', SINGLE_WORDLIST, '-w', '3', '-O', '--increment']
    subprocess.call(hc)
    if HM_ANSWER == '0' or HM_ANSWER == '1':
        hc_cmd2 = ['hashcat', '-m', HASH_TYPE, '-a', '0', '--username', '--session', 'all', '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME]
        subprocess.call(hc_cmd2)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
    elif HM_ANSWER == '2':
        hc_cmd3 = ['hashcat', '-m', HASH_TYPE, '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--session', 'all']
        subprocess.call(hc_cmd3)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
    else:
        return

#Crack Menu 7 - Try Oxford Dictionary Starting with UPPER Case + {upto 4 Numbers LEFT SIDE, upto 4 numbers RIGHT SIDE}
def crack_menu_7():
    AWK = "awk '!x[$0]++'"
    WORDLIST_DIRECTORY = "/opt/wordlists" # Needed to reset the wordlist directory.
    SINGLE_WORDLIST = os.path.join(WORDLIST_DIRECTORY, 'english-words/words_first_letter_upper.txt')
    if ALL_MENU:
        pot_function()
    else:
        hash_mode_menu()
        pot_function()
    os.system('clear')
    #Four Numbers (Left Side)
    hc1 = ['hashcat', '-a', '7', '-m', HASH_TYPE, HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '?d?d?d?d', SINGLE_WORDLIST, '-w', '3', '-O', '--increment']
    subprocess.call(hc1)
    if HM_ANSWER == '0' or HM_ANSWER == '1' or HM_ANSWER == '2':
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
        os.system('clear')
    else:
        os.system('clear')
    #Four Numbers (Right Side)
    hc2 = ['hashcat', '-a', '6', '-m', HASH_TYPE, HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), SINGLE_WORDLIST, '?d?d?d?d', '-w', '3', '-O', '--increment']
    subprocess.call(hc2)
    if HM_ANSWER == '0' or HM_ANSWER == '1':
        hc_cmd2 = ['hashcat', '-m', HASH_TYPE, '-a', '0', '--username', '--session', 'all', '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME]
        subprocess.call(hc_cmd2)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
    elif HM_ANSWER == '2':
        hc_cmd3 = ['hashcat', '-m', HASH_TYPE, '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--session', 'all']
        subprocess.call(hc_cmd3)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
    else:
        return

#Crack Menu 8 - Automated Testing - Oxford Dictionary MIXED CASE + upto 3 ANY Characters on RIGHT SIDE - {Corporate Scan}
def crack_menu_8():
    AWK = "awk '!x[$0]++'"
    WORDLIST_DIRECTORY = "/opt/wordlists" # Needed to reset the wordlist directory.
    SINGLE_WORDLIST = os.path.join(WORDLIST_DIRECTORY, 'english-words/words.txt')
    if ALL_MENU:
        pot_function()
    else:
        hash_mode_menu()
        pot_function()
    os.system('clear')
    hc = ['hashcat', '-a', '6', '-m', HASH_TYPE, HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), SINGLE_WORDLIST, '?a?a?a?a', '-w', '3', '-O', '--increment']
    subprocess.call(hc)
    if HM_ANSWER == '0' or HM_ANSWER == '1':
        hc_cmd2 = ['hashcat', '-m', HASH_TYPE, '-a', '0', '--username', '--session', 'all', '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME]
        subprocess.call(hc_cmd2)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
    elif HM_ANSWER == '2':
        hc_cmd3 = ['hashcat', '-m', HASH_TYPE, '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--session', 'all']
        subprocess.call(hc_cmd3)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
    else:
        return

#Crack Menu 9 - Rockyou with rule - d3ad0ne
def crack_menu_9():
    AWK = "awk '!x[$0]++'"
    WORDLIST_DIRECTORY = "/opt/wordlists" # Needed to reset the wordlist directory.
    global DEFAULT_CEWL_FILE_OUTPUT
    global SINGLE_HASH_BOOLEAN
    global FILE_HASH_BOOLEAN
    global RULE_SET_DIRECTORY
    if CEWL_BOOLEAN and FILE_HASH_BOOLEAN or SINGLE_HASH_BOOLEAN and CEWL_BOOLEAN:
        SINGLE_WORDLIST = DEFAULT_CEWL_FILE_OUTPUT
    else:
        SINGLE_WORDLIST = os.path.join(WORDLIST_DIRECTORY, 'rockyou.txt')
    if ALL_MENU:
        pot_function()
    else:
        hash_mode_menu()
        pot_function()
    os.system('clear')
    hc = ['hashcat', '-a', '0', '-m', HASH_TYPE, HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), SINGLE_WORDLIST, '-r', os.path.join(RULES_DIR, 'd3ad0ne.rule'), '-w', '3', '-O']
    subprocess.call(hc)
    if HM_ANSWER == '0' or HM_ANSWER == '1':
        hc_cmd2 = ['hashcat', '-m', HASH_TYPE, '-a', '0', '--username', '--session', 'all', '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME]
        subprocess.call(hc_cmd2)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
    elif HM_ANSWER == '2':
        hc_cmd3 = ['hashcat', '-m', HASH_TYPE, '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_ABS_PATH, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--session', 'all']
        subprocess.call(hc_cmd3)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
    else:
        return

#Crack Menu 10 - Rockyou with rule - OneRuleToRuleThemAll
def crack_menu_10():
    AWK = "awk '!x[$0]++'"
    WORDLIST_DIRECTORY = "/opt/wordlists" # Needed to reset the wordlist directory.
    global SINGLE_HASH_BOOLEAN
    global FILE_HASH_BOOLEAN
    global RULE_SET_DIRECTORY
    if CEWL_BOOLEAN and FILE_HASH_BOOLEAN or SINGLE_HASH_BOOLEAN and CEWL_BOOLEAN:
        SINGLE_WORDLIST = DEFAULT_CEWL_FILE_OUTPUT
    else:
        SINGLE_WORDLIST = os.path.join(WORDLIST_DIRECTORY, 'rockyou.txt')
    if ALL_MENU:
        pot_function()
    else:
        hash_mode_menu()
        pot_function()
    os.system('clear')
    hc = ['hashcat', '-a', '0', '-m', HASH_TYPE, HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), SINGLE_WORDLIST, '-r', os.path.join(RULES_DIR, 'OneRuleToRuleThemAll.rule'), '-w', '3', '-O']
    subprocess.call(hc)
    if HM_ANSWER == '0' or HM_ANSWER == '1':
        hc_cmd2 = ['hashcat', '-m', HASH_TYPE, '-a', '0', '--username', '--session', 'all', '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_ABS_PATH]
        subprocess.call(hc_cmd2)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
    elif HM_ANSWER == '2':
        hc_cmd3 = ['hashcat', '-m', HASH_TYPE, '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--session', 'all']
        subprocess.call(hc_cmd3)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
    else:
        return

#Crack Menu 11 - Rockyou with rule - # Changed to add leet speak rules
def crack_menu_11():
    AWK = "awk '!x[$0]++'"
    WORDLIST_DIRECTORY = "/opt/wordlists" # Needed to reset the wordlist directory.
    global DEFAULT_CEWL_FILE_OUTPUT
    if CEWL_BOOLEAN and FILE_HASH_BOOLEAN or SINGLE_HASH_BOOLEAN and CEWL_BOOLEAN:
        SINGLE_WORDLIST = DEFAULT_CEWL_FILE_OUTPUT
    else:
        SINGLE_WORDLIST = os.path.join(WORDLIST_DIRECTORY, 'rockyou.txt')
    if ALL_MENU:
        pot_function()
    else:
        hash_mode_menu()
        pot_function()
    os.system('clear')
    hc1 = ['hashcat', '-a', '0', '-m', HASH_TYPE, HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), SINGLE_WORDLIST, '-r', os.path.join(RULES_DIR, 'leetspeak.rule'), '-w', '3', '-O']
    subprocess.call(hc1)
    hc2 = ['hashcat', '-a', '0', '-m', HASH_TYPE, HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), SINGLE_WORDLIST, '-r', os.path.join(RULES_DIR, 'unix-ninja-leetspeak.rule'), '-w', '3', '-O']
    subprocess.call(hc2)
    if HM_ANSWER == '0' or HM_ANSWER == '1':
        hc_cmd2 = ['hashcat', '-m', HASH_TYPE, '-a', '0', '--username', '--session', 'all', '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME]
        subprocess.call(hc_cmd2)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
    elif HM_ANSWER == '2':
        hc_cmd3 = ['hashcat', '-m', HASH_TYPE, '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--session', 'all']
        subprocess.call(hc_cmd3)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
    else:
        return

#Crack Menu 12 - Rockastic with OneRuleToRuleThemAll
def crack_menu_12():
    AWK = "awk '!x[$0]++'"
    WORDLIST_DIRECTORY = "/opt/wordlists" # Needed to reset the wordlist directory.
    global DEFAULT_CEWL_FILE_OUTPUT
    global FILE_HASH_BOOLEAN
    if CEWL_BOOLEAN and FILE_HASH_BOOLEAN or SINGLE_HASH_BOOLEAN and CEWL_BOOLEAN:
        SINGLE_WORDLIST = DEFAULT_CEWL_FILE_OUTPUT
    else:
        SINGLE_WORDLIST = os.path.join(WORDLIST_DIRECTORY, '4GB+/Rocktastic12a.txt')
    if ALL_MENU:
        pot_function()
    else:
        hash_mode_menu()
        pot_function()
    os.system('clear')
    hc = ['hashcat', '-a', '0', '-m', HASH_TYPE, HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), SINGLE_WORDLIST, '-r', os.path.join(RULES_DIR, 'OneRuleToRuleThemAll.rule'), '-w', '3', '-O']
    subprocess.call(hc)
    if HM_ANSWER == '0' or HM_ANSWER == '1':
        hc_cmd2 = ['hashcat', '-m', HASH_TYPE, '-a', '0', '--username', '--session', 'all', '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME]
        subprocess.call(hc_cmd2)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
    elif HM_ANSWER == '2':
        hc_cmd3 = ['hashcat', '-m', HASH_TYPE, '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--session', 'all']
        subprocess.call(hc_cmd3)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
    else:
        return

#Crack Menu 13 - Rocktastic with dive rule
def crack_menu_13():
    AWK = "awk '!x[$0]++'"
    WORDLIST_DIRECTORY = "/opt/wordlists" # Needed to reset the wordlist directory.
    global DEFAULT_CEWL_FILE_OUTPUT
    global SINGLE_HASH_BOOLEAN
    global FILE_HASH_BOOLEAN
    global RULE_SET_DIRECTORY
    if CEWL_BOOLEAN and FILE_HASH_BOOLEAN or SINGLE_HASH_BOOLEAN and CEWL_BOOLEAN:
        SINGLE_WORDLIST = DEFAULT_CEWL_FILE_OUTPUT
    else:
        SINGLE_WORDLIST = os.path.join(WORDLIST_DIRECTORY, '4GB+/Rocktastic12a.txt')
    if ALL_MENU:
        pot_function()
    else:
        hash_mode_menu()
        pot_function()
    os.system('clear')
    hc = ['hashcat', '-a', '0', '-m', HASH_TYPE, HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), SINGLE_WORDLIST, '-r', os.path.join(RULES_DIR, 'dive.rule'), '-w', '3', '-O']
    subprocess.call(hc)
    if HM_ANSWER == '0' or HM_ANSWER == '1':
        hc_cmd2 = ['hashcat', '-m', HASH_TYPE, '-a', '0', '--username', '--session', 'all', '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME]
        subprocess.call(hc_cmd2)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
    elif HM_ANSWER == '2':
        hc_cmd3 = ['hashcat', '-m', HASH_TYPE, '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--session', 'all']
        subprocess.call(hc_cmd3)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
    else:
        return

#Crack Menu 14 - Rocktastic with Hob0Rules -> Quick {hob064.rule} -> Comprenensive Test {d3adhob0.rule}
def crack_menu_14():
    AWK = " awk '!x[$0]++' "
    WORDLIST_DIRECTORY = "/opt/wordlists" # Needed to reset the wordlist directory.
    global SINGLE_HASH_BOOLEAN
    global FILE_HASH_BOOLEAN
    global RULE_SET_DIRECTORY
    if CEWL_BOOLEAN and FILE_HASH_BOOLEAN or SINGLE_HASH_BOOLEAN and CEWL_BOOLEAN:
        SINGLE_WORDLIST = DEFAULT_CEWL_FILE_OUTPUT
    else:
        SINGLE_WORDLIST = os.path.join(WORDLIST_DIRECTORY, '4GB+/Rocktastic12a.txt')
    if ALL_MENU:
        pot_function()
    else:
        hash_mode_menu()
        pot_function()
    os.system('clear')
    hc1 = ['hashcat', '-a', '0', '-m', HASH_TYPE, HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), SINGLE_WORDLIST, '-r', os.path.join(RULES_DIR, 'hob064.rule'), '-w', '3', '-O']
    subprocess.call(hc1)
    if HM_ANSWER == '0' or HM_ANSWER == '1' or HM_ANSWER == '2':
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
        os.system('clear')
    else:
        os.system('clear')
    hc2 = ['hashcat', '-a', '0', '-m', HASH_TYPE, HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), SINGLE_WORDLIST, '-r', os.path.join(RULES_DIR, 'd3adhob0.rule'), '-w', '3', '-O']
    subprocess.call(hc2)
    if HM_ANSWER == '0' or HM_ANSWER == '1':
        hc_cmd2 = ['hashcat', '-m', HASH_TYPE, '-a', '0', '--username', '--session', 'all', '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME]
        subprocess.call(hc_cmd2)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
    elif HM_ANSWER == '2':
        hc_cmd3 = ['hashcat', '-m', HASH_TYPE, '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--session', 'all']
        subprocess.call(hc_cmd3)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
    else:
        return

#Crack Menu 15 - Auto Multi Rule Test - Iterate through each rule with rockyou.txt - {Corporate Scan}
def crack_menu_15():
    WORDLIST_DIRECTORY = "/opt/wordlists" # Needed to reset the wordlist directory.
    global SINGLE_WORDLIST
    global DEFAULT_CEWL_FILE_OUTPUT
    global HASH_ABS_PATH
    global RULE_SET_DIRECTORY
    if CEWL_BOOLEAN and FILE_HASH_BOOLEAN or SINGLE_HASH_BOOLEAN and CEWL_BOOLEAN:
        SINGLE_WORDLIST = DEFAULT_CEWL_FILE_OUTPUT
    else:
        SINGLE_WORDLIST = os.path.join(WORDLIST_DIRECTORY, 'rockyou.txt')
    if ALL_MENU:
        pot_function()
        os.system('clear')
    else:
        hash_mode_menu()
        pot_function()
        os.system('clear')
    rule_set_walk()
    return

#Rsmangler - Create multiple permutations of a word
def rsmangler_menu():
    AWK = "awk '!x[$0]++'"
    global SINGLE_HASH_BOOLEAN
    global SINGLE_WORDLIST
    global CEWL_BOOLEAN
    global FILE_HASH_BOOLEAN
    os.system("clear")
    banner()
    firmname = raw_input("What is the name of the firm to be mangled?" + "\n")
    os.chdir(RSMANGLER_INPUT_DIR)
    sh = open(firmname, "w+")
    sh.write(firmname + "\n")
    sh.close()
    rsmangler = os.path.join(TOOLS_DIR, 'rsmangler.rb')
    RSMANGLER_OUTPUT_DIR_AND_FIRMNAME = os.path.join(RSMANGLER_OUTPUT_DIR, firmname)
    RSMANGLER_INPUT_DIR_AND_FIRMNAME = os.path.join(RSMANGLER_INPUT_DIR, firmname)
    rs = [rsmangler, '--file', RSMANGLER_INPUT_DIR_AND_FIRMNAME, '--output', RSMANGLER_OUTPUT_DIR_AND_FIRMNAME]
    subprocess.call(rs)
    os.system('clear')
    banner()
    hash_mode_menu()
    pot_function()
    if SINGLE_HASH_BOOLEAN and CEWL_BOOLEAN == False:
        SINGLE_WORDLIST = RSMANGLER_OUTPUT_DIR_AND_FIRMNAME # Space added for correct argument spacing
    elif SINGLE_HASH_BOOLEAN and CEWL_BOOLEAN:
        SINGLE_WORDLIST = DEFAULT_CEWL_FILE_OUTPUT
    elif FILE_HASH_BOOLEAN and CEWL_BOOLEAN == False:
        SINGLE_WORDLIST = RSMANGLER_OUTPUT_DIR_AND_FIRMNAME # Space added for correct argument spacing
    elif FILE_HASH_BOOLEAN and CEWL_BOOLEAN:
        SINGLE_WORDLIST = DEFAULT_CEWL_FILE_OUTPUT
    os.system('clear')
    hc = ['hashcat', '-a', '0', '-m', HASH_TYPE, HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), SINGLE_WORDLIST, '-r', os.path.join(RULES_DIR, 'OneRuleToRuleThemAll.rule'), '-w', '3', '-O']
    subprocess.call(hc)
    #Right Side
    hc1 = ['hashcat', '-a', '6', '-m', HASH_TYPE, HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), SINGLE_WORDLIST, '?a?a?a?a', '-w', '3', '-O', '--increment']
    subprocess.call(hc1)
    if HM_ANSWER == '0' or HM_ANSWER == '1' or HM_ANSWER == '2':
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
        os.system('clear')
    else:
        os.system('clear')
    #Left Side
    hc2 = ['hashcat', '-a', '7', '-m', HASH_TYPE, HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '?a?a?a?a', SINGLE_WORDLIST, '-w', '3', '-O', '--increment']
    subprocess.call(hc2)
    if HM_ANSWER == '0' or HM_ANSWER == '1':
        hc_cmd2 = ['hashcat', '-m', HASH_TYPE, '-a', '0', '--username', '--session', 'all', '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME]
        subprocess.call(hc_cmd2)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
    elif HM_ANSWER == '2':
        hc_cmd3 = ['hashcat', '-m', HASH_TYPE, '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--session', 'all']
        subprocess.call(hc_cmd3)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
    else:
        return

#Cewl menu - Ran first before 17 or 18 can be activated
def cewl_menu_16():
    global CEWL_BOOLEAN
    global DEFAULT_CEWL_FILE_OUTPUT
    global SINGLE_HASH_ABS_PATH
    global CEWL_WORDLIST_SIZE
    CEWL_BOOLEAN = True
    os.system('clear')
    banner()
    print"We will now make a wordlist based on the given website address"
    cewl_url_input = raw_input("Specify the website for collecting the wordlist in full including protocols and ports numbers if non standard:" + '\n')
    if SINGLE_HASH_BOOLEAN:
        cewl_hash_input = SINGLE_HASH_ABS_PATH + '.cewl-list.txt'
    elif FILE_HASH_BOOLEAN:
        cewl_hash_input = HASH_INPUT + '.cewl-list.txt'
    DEFAULT_CEWL_FILE_OUTPUT = os.path.join(CEWL_UPLOAD_DIR, cewl_hash_input)
    cewl = ['cewl', '--depth', '2', '--min_word_length', '5', cewl_url_input, '-v', '-w', DEFAULT_CEWL_FILE_OUTPUT]
    subprocess.call(cewl)
    os.system('clear')
    CEWL_WORDLIST_SIZE = os.popen('wc -l ' + DEFAULT_CEWL_FILE_OUTPUT).read()
    banner()
    hash_mode_menu()
    os.system('clear')
    return

#Run straight Cewl Wordlist
def cewl_menu_17():
    global SINGLE_WORDLIST
    global DEFAULT_CEWL_FILE_OUTPUT
    global CEWL_BOOLEAN
    global FILE_HASH_BOOLEAN
    if CEWL_BOOLEAN and FILE_HASH_BOOLEAN or SINGLE_HASH_BOOLEAN and CEWL_BOOLEAN:
        SINGLE_WORDLIST = DEFAULT_CEWL_FILE_OUTPUT
    else:
        raw_input("Cewl Wordlist not ran yet!, run cewl first, (Option 16)")
        crack_menu()
    pot_function()
    hc = ['hashcat', '-a', '0', '-m', HASH_TYPE, HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), SINGLE_WORDLIST, '-w', '3', '-O']
    subprocess.call(hc)
    if HM_ANSWER == '0' or HM_ANSWER == '1':
        hc_cmd2 = ['hashcat', '-m', HASH_TYPE, '-a', '0', '--username', '--session', 'all', '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME]
        subprocess.call(hc_cmd2)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
    elif HM_ANSWER == '2':
        hc_cmd3 = ['hashcat', '-m', HASH_TYPE, '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--session', 'all']
        subprocess.call(hc_cmd3)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
    else:
        return
    return

#Automated Cewl wordlist - {4 ANY Characters RIGHT --> LEFT incrementally} (could take a while dependant on size of cewl wordlist generated)
def cewl_menu_18():
    AWK = "awk '!x[$0]++'"
    global SINGLE_WORDLIST
    global DEFAULT_CEWL_FILE_OUTPUT
    global CEWL_BOOLEAN
    global FILE_HASH_BOOLEAN
    if CEWL_BOOLEAN and FILE_HASH_BOOLEAN or single_hash_boolean and CEWL_BOOLEAN:
        SINGLE_WORDLIST = DEFAULT_CEWL_FILE_OUTPUT
    else:
        raw_input("Cewl Wordlist not ran yet!, run cewl first, (Option 16)")
        crack_menu()
    pot_function()
    #Right Side
    hc1 = ['hashcat', '-a', '6', '-m', HASH_TYPE, HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), SINGLE_WORDLIST, '?a?a?a?a', '-w', '3', '-O', '--increment']
    subprocess.call(hc1)
    #Left Side
    hc2 = ['hashcat', '-a', '7', '-m', HASH_TYPE, HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '?a?a?a?a', SINGLE_WORDLIST, '-w', '3', '-O', '--increment']
    subprocess.call(hc2)
    #Run against 'dive' Rule
    hc3 = ['hashcat', '-a', '0', '-m', HASH_TYPE, HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), SINGLE_WORDLIST, '-r', os.path.join(RULES_DIR, 'dive.rule'), '-w', '3', '-O']
    subprocess.call(hc3)
    #Run Against 'OneRuleToRuleThemAll' Rule
    hc4 = ['hashcat', '-a', '0', '-m', HASH_TYPE, HASH_PATH_AND_NAME, SINGLE_WORDLIST, '-r', os.path.join(RULES_DIR, 'OneRuleToRuleThemAll.rule'), '-w', '3', '-O']
    subprocess.call(hc4)
    if HM_ANSWER == '0' or HM_ANSWER == '1':
        hc_cmd2 = ['hashcat', '-m', HASH_TYPE, '-a', '0', '--username', '--session', 'all', '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME]
        subprocess.call(hc_cmd2)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, pot) + '.sorted ', shell=True)
    elif HM_ANSWER == '2':
        hc_cmd3 = ['hashcat', '-m', HASH_TYPE, '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--session', 'all']
        subprocess.call(hc_cmd3)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
    else:
        return

#All Menus
#This will increment the menus from 1 - Useful when leaving on the go..
def increment_menu():
    global ALL_MENU
    global WORDLIST_DIRECTORY
    ALL_MENU = True
    WORDLIST_DIRECTORY = "/opt/wordlists"
    banner()
    hash_mode_menu()
    pot_function()
    crack_menu_0()
    crack_menu_1()
    crack_menu_2()
    crack_menu_3()
    crack_menu_4()
    crack_menu_5()
    crack_menu_6()
    crack_menu_7()
    crack_menu_8()
    crack_menu_9()
    crack_menu_10()
    crack_menu_11()
    crack_menu_12()
    crack_menu_13()
    crack_menu_14()
    any_menu()

#Passphrase testing Menu
def passphrase_menu():
    WORDLIST_DIRECTORY = "/opt/wordlists"
    global DEFAULT_CEWL_FILE_OUTPUT
    global HASH_ABS_PATH
    if CEWL_BOOLEAN and FILE_HASH_BOOLEAN or SINGLE_HASH_BOOLEAN and CEWL_BOOLEAN:
        SINGLE_WORDLIST = DEFAULT_CEWL_FILE_OUTPUT
    else:
        SINGLE_WORDLIST = os.path.join(WORDLIST_DIRECTORY, 'passphrases/passphrases.txt')
    if ALL_MENU:
        pot_function()
    else:
        banner()
        hash_mode_menu()
        pot_function()
    os.system('clear')
    hc = ['hashcat', '-a', '0', '-m', HASH_TYPE, HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), SINGLE_WORDLIST, '-r', os.path.join(RULES_DIR, 'passphrase-rule1.rule'), '-r', os.path.join(RULES_DIR, 'passphrase-rule2.rule'), '-w', '3', '-O']
    subprocess.call(hc)
    if HM_ANSWER == '0' or HM_ANSWER == '1' or HM_ANSWER == '2':
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
    else:
        os.system('clear')
    hc1 = ['hashcat', '-a', '0', '-m', HASH_TYPE, HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), SINGLE_WORDLIST, '-r', os.path.join(RULES_DIR, 'dive.rule'), '-w', '3', '-O']
    subprocess.call(hc1)
    hc2 = ['hashcat', '-a', '0', '-m', HASH_TYPE, HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), SINGLE_WORDLIST, '-r', os.path.join(RULES_DIR, 'OneRuleToRuleThemAll.rule'), '-w', '3', '-O']
    subprocess.call(hc2)
    if HM_ANSWER == '0' or HM_ANSWER == '1':
        hc_cmd2 = ['hashcat', '-m', HASH_TYPE, '-a', '0', '--username', '--session', 'all', '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME]
        subprocess.call(hc_cmd2)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
    elif HM_ANSWER == '2':
        hc_cmd3 = ['hashcat', '-m', HASH_TYPE, '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--session', 'all']
        subprocess.call(hc_cmd3)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
    else:
        return

#Any Menu
def any_menu():
    if ALL_MENU:
        pot_function()
    else:
        banner()
        hash_mode_menu()
        pot_function()
    os.system('clear')
    hc1 = ['hashcat', '-a', '3', '-m', HASH_TYPE, HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), "?a?a?a?a?a?a?a?a?a?a?a?a", '-w', '3', '-O', '--increment']
    subprocess.call(hc1)
    if HM_ANSWER == '0' or HM_ANSWER == '1':
        hc_cmd2 = ['hashcat', '-m', HASH_TYPE, '-a', '0', '--username', '--session', 'all', '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME]
        subprocess.call(hc_cmd2)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
    elif HM_ANSWER == '2':
        hc_cmd3 = ['hashcat', '-m', HASH_TYPE, '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--session', 'all']
        subprocess.call(hc_cmd3)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
    else:
        return

#Crack Menu (Back Crack) - go back one stage...
def back_crack():
    global ALL_MENU
    global CEWL_BOOLEAN
    global SINGLE_HASH_BOOLEAN
    global FILE_HASH_BOOLEAN
    global POT_BOOLEAN
    ALL_MENU = False # Needed to reset for the automatic menu.
    CEWL_BOOLEAN = False # Needed to reset for new menu settings to be applied.
    SINGLE_HASH_BOOLEAN = False # Needed to reset for new menu settings to be applied.
    FILE_HASH_BOOLEAN = False # Needed to reset for new menu settings to be applied.
    POT_BOOLEAN = False # Needed to reset for new menu settings to be applied.
    main_menu()
    return

#Cracking Menu
def crack_menu():
    global HASH_ABS_PATH
    global DEFAULT_CEWL_FILE_OUTPUT
    global CEWL_BOOLEAN
    global CEWL_WORDLIST_SIZE
    global L00T_POT_DIR
    global HASH_INPUT
    os.system('clear')
    try:
        while 1:
            if SINGLE_HASH_BOOLEAN and not CEWL_BOOLEAN:
                banner()
                print""
                print'\t\t\t\t' + '\033[40m' + '--==Single Hash Cracking Menu==--' + '\033[0m'
                print""
                print""
                print" Hash file created:"
                prYellow(SINGLE_HASH_ABS_PATH)
            elif SINGLE_HASH_BOOLEAN and CEWL_BOOLEAN:
                banner()
                print""
                print'\t\t\t\t' + '\033[40m' + '--==Single Hash Cewl Cracking Menu==--' + '\033[0m'
                print""
                print""
                print" Single Hash file in Use:"
                prYellow(SINGLE_HASH_ABS_PATH)
                print" Cewl Wordlist in Use:"
                prYellow(DEFAULT_CEWL_FILE_OUTPUT)
            elif FILE_HASH_BOOLEAN and not CEWL_BOOLEAN:
                banner() # Currently display duplicates first time round, second time round it only shows one banner..
                print""
                print'\t\t\t\t\t' + '\033[40m' + '--==Multi Hash Cracking Menu==--' + '\033[0m'
                print""
                print""
                print" " + "Hash File Loaded:  ",
                prYellow(HASH_ABS_PATH)
                print" " + "Hashes Loaded:     ",
                prRed(HASHES_LOADED)
                print" " + "Hashes Cracked:    ",
                POT = HASH_INPUT.lower()
                POT = POT + '.pot'
                pot_absolute = os.path.join(L00T_POT_DIR, POT)
                if os.path.exists(pot_absolute):
                    with open(pot_absolute) as lines:
                        hashes_cracked = len(lines.readlines())
                        print' ' + '\033[92m' + str(hashes_cracked) + '\033[0m'
                        print' ' + 'Percentage Cracked:',
                        percent_cracked = (hashes_cracked * 100 / HASHES_LOADED)
                        print' ' + '\033[34m' + str(percent_cracked) + ('%') + '\033[0m'
                else:
                    prRed("0")
                    print' ' + 'Percentage Cracked:',
                    print'\033[34m' + ' ' + str(0) + ('%') + '\033[0m'
            elif FILE_HASH_BOOLEAN and CEWL_BOOLEAN:
                banner() # Added after the call as still in the loop for aesthtics.
                print""
                print'\t\t\t\t' + '\033[40m' + '--==Multi Hash Cewl Cracking Menu==--' + '\033[0m'
                print""
                print""
                print" " + "Hash file in use:"
                prYellow(HASH_ABS_PATH)
                print""
                print" " + "Amount of Cewl words written + Absolute Path: "
                prYellow(CEWL_WORDLIST_SIZE)
            print""
            print' ' + '\033[44m' + 'Supported - NTLMv2 (NTHASH) -> NetNTLMv1 -> NetNTLMv2 -> MD5 -> SHA-512 -> RC4-HMAC-MD5 (Kerberoasting)' + '\033[0m'
            print""
            prCyan("0) A single merged list of wordlists in the public domain")
            prLightPurple("1) Common Wordlists - includes rockyou, hashkiller")
            prCyan("2) Crackstation + Hashes.org(2019) list")
            prLightPurple("3) +8 chars + 0-9 + UCASE + LCASE (with diacritic marks, Greek & Cyrillic chars)")
            prCyan("4) All wordlists 4GB+ - {Incremental Scan}")
            prLightPurple("5) Oxford Dict Start UPPER Case + upto 3 ANY Chars on RIGHT SIDE")
            prCyan("6) Oxford Dict Start UPPER Case + upto 3 ANY Chars on LEFT SIDE")
            prLightPurple("7) Oxford Dict Start UPPER Case + upto 4 digits LEFT SIDE, upto 4 digits RIGHT SIDE")
            prCyan("8) Oxford Dict MIXED CASE + upto 3 ANY Chars on RIGHT SIDE")
            prLightPurple("9) Rule - Rockyou or cewl - d3ad0ne")
            prCyan("10) Rule - Rockyou or cewl - OneRuleToRuleThemAll")
            prLightPurple("11) Rule - Rockyou or cewl - L33t speak rules (leetspeak.rule + unix-ninja-leetspeak.rule)")
            prCyan("12) Rule - Rocktastic or cewl -> OneRuleToRuleThemAll.rule")
            prLightPurple("13) Rule - Rocktastic with dive rule")
            prCyan("14) Rule - Rocktastic or cewl -> Quick {hob064.rule} -> Comprehensive {d3adhob0.rule}")
            prLightPurple("15) Auto Multi Rule Test - Iterate through each rule with rockyou.txt")
            prCyan("16) Cewl Test - Enter the firms website to create a bespoke, focussed wordlist")
            prLightPurple("17) Straight Cewl wordlist - (Run option 16 first to activate)")
            prCyan("18) Auto Cewl wordlist - {4 ANY Characters RIGHT --> LEFT incrementally -> Dive Rule}")
            prLightPurple("19) Wordlist Mangling Tool - Various permutations of a specified name")
            prCyan("a) Multiple Tests - All of the above, mainly in ascending numerical order")
            prLightPurple("b) Passphrases testing - Multiple words strung together using multiple rule sets")
            prCyan("c) Auto Increment ANY combination upto 12 characters '?a?a?a?a?a?a?a?a?a?a?a?a'")
            prRed("d) Back to Main Menu")
            crack_option = {"0": crack_menu_0,
                            "1": crack_menu_1,
                            "2": crack_menu_2,
                            "3": crack_menu_3,
                            "4": crack_menu_4,
                            "5": crack_menu_5,
                            "6": crack_menu_6,
                            "7": crack_menu_7,
                            "8": crack_menu_8,
                            "9": crack_menu_9,
                            "10": crack_menu_10,
                            "11": crack_menu_11,
                            "12": crack_menu_12,
                            "13": crack_menu_13,
                            "14": crack_menu_14,
                            "15": crack_menu_15,
                            "16": cewl_menu_16,
                            "17": cewl_menu_17,
                            "18": cewl_menu_18,
                            "19": rsmangler_menu,
                            "a": increment_menu,
                            "b": passphrase_menu,
                            "c": any_menu,
                            "d": back_crack
                           }
            try:
                selection = raw_input("\n Select an Option: ")
                crack_option[selection]()
            except KeyError:
                os.system('clear')
                banner()
    except KeyboardInterrupt:
        sys.exit()

#Single Hash Menu
def single_hash_menu():
    global SINGLE_HASH_FILE_NAME
    global SINGLE_HASH_BOOLEAN
    global SINGLE_HASH_ABS_PATH
    SINGLE_HASH_BOOLEAN = True
    os.system('clear')
    banner()
    print"Example NetNTLMv2 Hash"
    print"admin::N46iSNekpT:08ca45b7d7ea58ee:88dcbe4446168966a153a0064958dac6:5c7830315c7830310000000000000b45c67103d07d7b95acd12ffa11230e0000000052920b85f78d013c31cdb3b92f5d765c783030"
    print"Password - hashcat"
    print""
    single_hash = raw_input(" Add your hash" + '\n')
    single_hash_string = str(single_hash)
    print""
    print" You entered : " + '\n' + single_hash_string
    print" OK - Need to put the hash into a file..." #Put hash into a file
    SINGLE_HASH_FILE_NAME = raw_input("Enter a logical filename: ")
    SINGLE_HASH_ABS_PATH = (os.path.join(HASH_UPLOAD_DIR, SINGLE_HASH_FILE_NAME))
    os.chdir(HASH_UPLOAD_DIR)
    sh = open(SINGLE_HASH_FILE_NAME, "w+")
    sh.write(single_hash_string)
    print"File Created"
    sh.close()
    crack_menu()
    return

#Hash File Upload Menu
def hash_from_file():
    global HASH_ABS_PATH
    global HASH_INPUT
    global HASHES_LOADED
    global FILE_HASH_BOOLEAN
    global HASH_UPLOAD_DIR
    FILE_HASH_BOOLEAN = True
    os.system('clear')
    banner()
    print'\033[33m' + ' ' + 'Add hash files into the hash upload directory shown below:' + '\033[0m'
    prCyan(HASH_UPLOAD_DIR)
    print""
    print'\033[34m' + ' ' + 'Below are the files currently available in the hash upload directory.. (Hit Enter to Refresh)' + '\033[0m'
    print""
    #Used for removing emacs created backup files ending with a tilde
    ignore = '~'
    for root, dirs, files in os.walk(HASH_UPLOAD_DIR):
        files.sort()
        for f in files:
            if not f.endswith(ignore):
                print" \t" + os.path.join(f)
    print""
    print'\033[33m' + ' ' + 'Select the filename from the above list to be uploaded:' + '\033[0m'
    os.chdir(HASH_UPLOAD_DIR)               
    readline.parse_and_bind("tab: complete")
    HASH_INPUT = raw_input("------> ")
    try:
        if os.path.isfile(HASH_INPUT):
            print" Hash File %s found and accepted..." % HASH_INPUT
            HASH_ABS_PATH = (os.path.join(HASH_UPLOAD_DIR, HASH_INPUT))
            print" Absolute Path of hash file is: \n" + HASH_ABS_PATH
            with open(HASH_ABS_PATH) as lines:
                HASHES_LOADED = len(lines.readlines())
            os.system('clear')
            crack_menu()
        else:
            print" " + "Error: %s file not found" % HASH_INPUT
            os.system('clear')
            hash_from_file()
    except KeyError:
        os.system('clear')
        pass
    return

#Exit system
def program_exit():
    sys.exit()

#MainMenu
def main_menu():
    try:
        while 1:
            banner()
            prCyan("\t(0) Input Singluar Hash")
            prLightPurple("\t(1) Input Hash from File")
            prRed("\t(2) Exit")
            options = {"0": single_hash_menu,
                       "1": hash_from_file,
                       "2": program_exit,
                      }
            try:
                task = raw_input("\n Choose an Option: ")
                options[task]()
            except KeyError:
                os.system('clear')
    except KeyboardInterrupt:
        sys.exit()

if __name__ == '__main__':
    main_menu()
