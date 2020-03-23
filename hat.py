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
import csv
import fnmatch
import os
import pprint as pp
import readline
import subprocess
#from subprocess import Popen, PIPE
import sys
import time

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

#Used to set the wireless menu
WIRELESS_BOOLEAN = False

#Used where we are only interested in User hashes to save time during engagements
USER_ONLY_BOOLEAN = False

#Initally Clear the Screen
os.system('clear')

#AWK command - AWKward command that doesn't sit well when called idrectly.
AWK = " " + "awk '!x[$0]++'" + " "

#HM_ANSWER set to '999' - Used if not declared for the stats menu.
HM_ANSWER = "999"

#Declare Paths
#First make the hat absolute path dynamic and go up one level to accomodate each related path
HASHCAT_PATH = os.getcwd()
#Set the wordlist directory to where you're wordlists are...
WORDLIST_DIRECTORY = "/opt/wordlists"
L00T_POT_DIR = os.path.join(HASHCAT_PATH, 'l00t')
RULES_DIR = os.path.join(HASHCAT_PATH, 'rules')
STATS_DIR = os.path.join(HASHCAT_PATH, 'stats')
HASH_UPLOAD_DIR = os.path.join(HASHCAT_PATH, 'hash_upload')
CEWL_UPLOAD_DIR = os.path.join(HASHCAT_PATH, 'cewl_wordlists')
TOOLS_DIR = os.path.join(HASHCAT_PATH, 'tools')
RSMANGLER_UPLOAD_DIR = os.path.join(HASHCAT_PATH, 'rsmangler')
RSMANGLER_INPUT_DIR = os.path.join(RSMANGLER_UPLOAD_DIR, 'input')
RSMANGLER_OUTPUT_DIR = os.path.join(RSMANGLER_UPLOAD_DIR, 'output')
WIRELESS_UPLOAD_DIR = os.path.join(HASHCAT_PATH, 'wireless_upload')

#Define Wireless File Extensions
CAP_FILE_EXT = '.cap'
HCCAPX_FILE_EXT = '.hccapx'

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
    global USER_ONLY_BOOLEAN
    if SINGLE_HASH_BOOLEAN:
        POT = SINGLE_HASH_FILE_NAME.lower()
        HASH_PATH_AND_NAME = os.path.join(os.getcwd(), SINGLE_HASH_FILE_NAME)
    elif WIRELESS_BOOLEAN:
        POT = WIRELESS_INPUT.lower()
        HASH_PATH_AND_NAME = os.path.join(WIRELESS_UPLOAD_DIR, WIRELESS_INPUT)
    elif USER_ONLY_BOOLEAN:
        POT = HASH_INPUT + '_users'
        HASH_PATH_AND_NAME = HASH_ABS_PATH
    else:
        HASH_PATH_AND_NAME = HASH_ABS_PATH
        POT = HASH_INPUT.lower()
    POT += '.pot' #No need to create a file here as hashcat will automajically make one
    POT_BOOLEAN = True
    return

#Hash Mode Selection Menu
def hash_mode_menu():
    global HASH_TYPE
    global HM_ANSWER
    if WIRELESS_BOOLEAN:
        HASH_TYPE = '2500' #.hccapx format
        return HASH_TYPE
    else:
        loop = True
        while loop:
            print"Input Hash Mode To Crack"
            prCyan("\t(0) NTLM {AKA NTHASH} - A SAM Database Hash - NTDS.dit - {PTH Possible}")
            prGreen("\tNTLM Example - 49a9a1e1f0127c7d70d750349d0bc09a - order (LM-NT)")
            prLightPurple("\t(1) Net-NTLMv1 Hash {AKA NTLMv1}")
            prGreen("\tNet-NTLMv1 Hash Example - u4-netntlm::kNS:338d08f00000:c23a90751cdd619b6e1e4bf33006ba41:c80860<snip>")
            prCyan("\t(2) Net-NTLMv2 Hash {AKA NTLMv2}")
            prGreen("\tNet-NTLMv2 Hash Example - admin::N46iSNekpT:08ca45b7d7ea58ee:88dcbe4446168966a153a0064958dc6:3<snip>")
            prLightPurple("\t(3) MD5 Unix {Shadow File Format}")
            prGreen("\tMD5 Unix Example - $1$28772684$iEwNOgGugqO9.bIz5sk8k/")
            prCyan("\t(4) SHA-512 Unix {Shadow File Format}")
            prGreen("\tSHA-512 Example - $6$52450745$k5ka2p8bFuSKBcCNqoDKzYiJL9RaE8yMnPgh2XzzF0NDrUhgrcLwg78xs1w5pJiy<snip>")
            prLightPurple("\t(5) Kerberos 5 TGS-REP etype 23 - Kerberoasting Format")
            prGreen("\tRC4-HMAC-MD5 Example - $krb5tgs$23$*user$realm$test/spn*$b548eb06bae0eead3b7f639178a90cf24d9a1<snip>")
            prCyan("\t(6) AS-REP ROASTING - Kerberos 5 AS-REP etype 23")
            prGreen("\tAS-REP23 Example - $krb5asrep$23$user@domain.com:3e156ada591263b8aab0965f5aebd837$007493e4r5t7<snip>")
            prLightPurple("\t(7) WPA-EAPOL-PBKDF2 (.hccapx - Wireless) ")
            prGreen("\tExample - 484350580400000000023538000000000000000000000000000000000000000000000000000000000000<snip> ")
            prCyan("\t(8) MS SQL Hash")
            prGreen("\tExample - 0x02003788006711b2e74e7d8cb4be96b1d187c96d30d0a5ee65d3ce1970f96e705c595f07622w3e4r1b1<snip>")
            prLightPurple("\t(9) Custom Hash Type - ENTER a HASHCAT MODE Number")
            prRed("\t(x) Back")
            HM_ANSWER = raw_input(": ")
            if HM_ANSWER == "0":   #NTLM aka NTHASH
                HASH_TYPE = '1000'
                return (HASH_TYPE)
            elif HM_ANSWER == "1": #Net-NTLMv1 aka NTLMv1
                HASH_TYPE = '5500'
                return (HASH_TYPE)
            elif HM_ANSWER == "2": #Net-NTLMv2 aka NTLMv2
                HASH_TYPE = '5600'
                return (HASH_TYPE)
            elif HM_ANSWER == "3": #MD5 (no salt)
                HASH_TYPE = '0'
                return (HASH_TYPE)
            elif HM_ANSWER == "4": #SHA-512 Unix
                HASH_TYPE = '1800'
                return (HASH_TYPE)
            elif HM_ANSWER == "5": #Kerberos 5 TGS-REP etype 23 --> RC4-HMAC-MD5
                HASH_TYPE = '13100'
                return (HASH_TYPE)
            elif HM_ANSWER == "6": #Kerberos 5 AS-REP etype 23 (AS-REP ROASTING)
                HASH_TYPE = '18200'
                return (HASH_TYPE)
            elif HM_ANSWER == "7": #WPA-EAPOL-PBKDF2 (.hccapx - Wireless)
                HASH_TYPE = '2500'
                return (HASH_TYPE)
            elif HM_ANSWER == "8": #MS-SQL  
                HASH_TYPE = '1300'
                return (HASH_TYPE)
            elif HM_ANSWER == "9": #Custom Hash Type
                HASH_TYPE = raw_input('If you know it, enter the Hashcat mode number to use or type' + ' ' + '\033[31m' + '"back"' + '\033[0m' + '\n')
                if HASH_TYPE == ('back') or HASH_INPUT == ('Back') or HASH_INPUT == ('BACK'):
                    break
                    hash_mode_menu()
                else:    
                    return (HASH_TYPE)
            elif HM_ANSWER == "x": #Return to the Crack Menu
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
    if WIRELESS_BOOLEAN:
        return
    elif HM_ANSWER == '0' or HM_ANSWER == '1' or HM_ANSWER == '2':
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
    if WIRELESS_BOOLEAN:
        return
    elif HM_ANSWER == '0' or HM_ANSWER == '1' or HM_ANSWER == '2':
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
        os.system('clear')
    else:
        os.system('clear')

#Rsmangler Rule Set - {5 ANY Characters RIGHT --> LEFT incremental}
def rsmangler_rule_set():
    hash_answer()
    hc = ['hashcat', '-a', '0', '-m', HASH_TYPE, HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, pot), SINGLE_WORDLIST, '-r', os.path.join(RULES_DIR, 'OneRuleToRuleThemAll.rule'), '-w', '3', '-O']
    subprocess.call(hc)
    #Right Side
    hc1 = ['hashcat', '-a', '6', HASH_TYPE, HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), SINGLE_WORDLIST, '?a?a?a?a', '-w', '3', '-O', '--increment']
    subprocess.call(hc1)
    if WIRELESS_BOOLEAN:
        return
    elif HM_ANSWER == '0' or HM_ANSWER == '1' or HM_ANSWER == '2':
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
        os.system('clear')
    else:
        os.system('clear')
    #LeftSide
    hc2 = ['hashcat', '-a', '7', '-m', HASH_TYPE, HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '?a?a?a?a', SINGLE_WORDLIST, '-w', '3', '-O', '--increment']
    subprocess.call(hc2)
    if WIRELESS_BOOLEAN:
        return
    elif HM_ANSWER == '0' or HM_ANSWER == '1' or HM_ANSWER == '2':
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
        os.system('clear')
    else:
        os.system('clear')

#Crack Menu 0 - Try all words lists merged List -  Common Credentials
#Updated and merged all smaller wordlists into one file for more effcient testing
#Added ruleset to add iterations to the based wordset
#(find . -name "*.txt" | xarg cat >> ./mergedfile.txt)
def crack_menu_0():
    global DEFAULT_CEWL_FILE_OUTPUT
    global CEWL_BOOLEAN
    global FILE_HASH_BOOLEAN
    global SINGLE_WORDLIST
    global WIRELESS_BOOLEAN
    global HASH_PATH_AND_NAME
    WORDLIST_DIRECTORY = "/opt/wordlists" #Needed to reset the wordlist directory.
    if ALL_MENU:
        pot_function()
    else:
        hash_mode_menu()
        pot_function()
    if CEWL_BOOLEAN and FILE_HASH_BOOLEAN or SINGLE_HASH_BOOLEAN and CEWL_BOOLEAN:
        SINGLE_WORDLIST = DEFAULT_CEWL_FILE_OUTPUT
    elif WIRELESS_BOOLEAN:
        HASH_PATH_AND_NAME = os.path.join(WIRELESS_UPLOAD_DIR, WIRELESS_INPUT)
        SINGLE_WORDLIST = os.path.join(WORDLIST_DIRECTORY, 'merged_list/sp00ks_merged_file_uniq.txt')
    else:
        SINGLE_WORDLIST = os.path.join(WORDLIST_DIRECTORY, 'merged_list/sp00ks_merged_file_uniq.txt')
    hc_cmd1 = ['hashcat', '-a', '0', '-m', HASH_TYPE, HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), SINGLE_WORDLIST, '-r', os.path.join(RULES_DIR, 'OneRuleToRuleThemAll.rule'), '-w', '3', '-O']
    subprocess.call(hc_cmd1)
    if WIRELESS_BOOLEAN:
        return
    elif HM_ANSWER == '0':
        hc_cmd2 = ['hashcat', '-m', HASH_TYPE, '-a', '0', '--username', '--session', 'all', '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME]
        subprocess.call(hc_cmd2)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
        subprocess.call('rm' + ' ' + os.path.join(L00T_POT_DIR, POT + '.format3'), shell=True)
    elif HM_ANSWER == '1' or HM_ANSWER == '2':
        hc_cmd3 = ['hashcat', '-m', HASH_TYPE, '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--session', 'all']
        subprocess.call(hc_cmd3)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
        subprocess.call('rm' + ' ' + os.path.join(L00T_POT_DIR, POT + '.format3'), shell=True)
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

#Crack Menu 2 - Special Wordlists Collection UK & US Cities
def crack_menu_2():
    WORDLIST_DIRECTORY = "/opt/wordlists" # Needed to reset the wordlist directory.
    global DEFAULT_CEWL_FILE_OUTPUT
    global HASH_PATH_AND_NAME
    global SINGLE_HASH_BOOLEAN
    global FILE_HASH_BOOLEAN
    global RULE_SET_DIRECTORY
    if CEWL_BOOLEAN and FILE_HASH_BOOLEAN or SINGLE_HASH_BOOLEAN and CEWL_BOOLEAN or WIRELESS_BOOLEAN and CEWL_BOOLEAN:
        SINGLE_WORDLIST = DEFAULT_CEWL_FILE_OUTPUT
    elif WIRELESS_BOOLEAN and not CEWL_BOOLEAN:
        HASH_PATH_AND_NAME = os.path.join(WIRELESS_UPLOAD_DIR, WIRELESS_INPUT)
        SINGLE_WORDLIST = os.path.join(WORDLIST_DIRECTORY, 'special/uk-cities.txt')
    else:
        SINGLE_WORDLIST = os.path.join(WORDLIST_DIRECTORY, 'special/uk-cities.txt')
    WORDLIST_DIRECTORY = "/opt/wordlists" # Needed to reset the wordlist directory.
    if ALL_MENU:
        pot_function()
    else:
        hash_mode_menu()
        pot_function()
        os.system('clear')
        hc = ['hashcat', '-a', '0', '-m', HASH_TYPE, HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), SINGLE_WORDLIST, '-r', os.path.join(RULES_DIR, 'OneRuleToRuleThemAll.rule'), '-w', '3', '-O']
        subprocess.call(hc)
    if WIRELESS_BOOLEAN:
        return
    elif HM_ANSWER == '0':
        hc_cmd2 = ['hashcat', '-m', HASH_TYPE, '-a', '0', '--username', '--session', 'all', '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME]
        subprocess.call(hc_cmd2)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
        subprocess.call('rm' + ' ' + os.path.join(L00T_POT_DIR, POT + '.format3'), shell=True)
    elif HM_ANSWER == '1' or HM_ANSWER == '2':
        hc_cmd3 = ['hashcat', '-m', HASH_TYPE, '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_ABS_PATH, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--session', 'all']
        subprocess.call(hc_cmd3)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
        subprocess.call('rm' + ' ' + os.path.join(L00T_POT_DIR, POT + '.format3'), shell=True)
    else:
        return
                                                                                                
#Crack_Menu 3
def crack_menu_3():
    global HASH_PATH_AND_NAME
    WORDLIST_DIRECTORY = "/opt/wordlists" # Needed to reset the wordlist directory.
    if ALL_MENU:
        pot_function()
    else:
        hash_mode_menu()
        pot_function()
    if CEWL_BOOLEAN and FILE_HASH_BOOLEAN or SINGLE_HASH_BOOLEAN and CEWL_BOOLEAN:
        SINGLE_WORDLIST = DEFAULT_CEWL_FILE_OUTPUT
    elif WIRELESS_BOOLEAN:
        HASH_PATH_AND_NAME = os.path.join(WIRELESS_UPLOAD_DIR, WIRELESS_INPUT)
        SINGLE_WORDLIST = os.path.join(WORDLIST_DIRECTORY, '4GB+/weakpass_2p')
    else:
        SINGLE_WORDLIST = os.path.join(WORDLIST_DIRECTORY, '4GB+/weakpass_2p')
    hc_cmd1 = ['hashcat', '-a', '0', '-m', HASH_TYPE, HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), SINGLE_WORDLIST, '-w', '3', '-O']
    subprocess.call(hc_cmd1)
    if WIRELESS_BOOLEAN:
        return
    elif HM_ANSWER == '0':
        hc_cmd2 = ['hashcat', '-m', HASH_TYPE, '-a', '0', '--username', '--session', 'all', '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME]
        subprocess.call(hc_cmd2)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
        subprocess.call('rm' + ' ' + os.path.join(L00T_POT_DIR, POT + '.format3'), shell=True)
    elif HM_ANSWER == '1' or HM_ANSWER == '2':
        hc_cmd3 = ['hashcat', '-m', HASH_TYPE, '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_ABS_PATH, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--session', 'all']
        subprocess.call(hc_cmd3)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
        subprocess.call('rm' + ' ' + os.path.join(L00T_POT_DIR, POT + '.format3'), shell=True)
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
    if WIRELESS_BOOLEAN:
        return
    elif HM_ANSWER == '0':
        hc_cmd2 = ['hashcat', '-m', HASH_TYPE, '-a', '0', '--username', '--session', 'all', '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME]
        subprocess.call(hc_cmd2)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
        subprocess.call('rm' + ' ' + os.path.join(L00T_POT_DIR, POT + '.format3'), shell=True)
    elif HM_ANSWER == '1' or HM_ANSWER == '2':
        hc_cmd3 = ['hashcat', '-m', HASH_TYPE, '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--session', 'all']
        subprocess.call(hc_cmd3)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
        subprocess.call('rm' + ' ' + os.path.join(L00T_POT_DIR, POT + '.format3'), shell=True)
    else:
        return

#Crack Menu 6 - Oxford Dic, capital letter, upto 4 characters, incrementally - LEFT SIDE
def crack_menu_6():
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
    if WIRELESS_BOOLEAN:
        return
    elif HM_ANSWER == '0':
        hc_cmd2 = ['hashcat', '-m', HASH_TYPE, '-a', '0', '--username', '--session', 'all', '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME]
        subprocess.call(hc_cmd2)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
        subprocess.call('rm' + ' ' + os.path.join(L00T_POT_DIR, POT + '.format3'), shell=True)
    elif HM_ANSWER == '1' or HM_ANSWER == '2':
        hc_cmd3 = ['hashcat', '-m', HASH_TYPE, '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--session', 'all']
        subprocess.call(hc_cmd3)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
        subprocess.call('rm' + ' ' + os.path.join(L00T_POT_DIR, POT + '.format3'), shell=True)
    else:
        return

#Crack Menu 7 - Try Oxford Dictionary Starting with UPPER Case + {upto 4 Numbers LEFT SIDE, upto 4 numbers RIGHT SIDE}
def crack_menu_7():
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
    if WIRELESS_BOOLEAN:
        return
    elif HM_ANSWER == '0' or HM_ANSWER == '1' or HM_ANSWER == '2':
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
        subprocess.call('rm' + ' ' + os.path.join(L00T_POT_DIR, POT + '.format3'), shell=True)
        os.system('clear')
    else:
        os.system('clear')
    #Four Numbers (Right Side)
    hc2 = ['hashcat', '-a', '6', '-m', HASH_TYPE, HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), SINGLE_WORDLIST, '?d?d?d?d', '-w', '3', '-O', '--increment']
    subprocess.call(hc2)
    if WIRELESS_BOOLEAN:
        return
    elif HM_ANSWER == '0':
        hc_cmd2 = ['hashcat', '-m', HASH_TYPE, '-a', '0', '--username', '--session', 'all', '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME]
        subprocess.call(hc_cmd2)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
        subprocess.call('rm' + ' ' + os.path.join(L00T_POT_DIR, POT + '.format3'), shell=True)
    elif HM_ANSWER == '1' or HM_ANSWER == '2':
        hc_cmd3 = ['hashcat', '-m', HASH_TYPE, '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--session', 'all']
        subprocess.call(hc_cmd3)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
        subprocess.call('rm' + ' ' + os.path.join(L00T_POT_DIR, POT + '.format3'), shell=True)
    else:
        return

#Crack Menu 8 - Automated Testing - Oxford Dictionary MIXED CASE + upto 3 ANY Characters on RIGHT SIDE - {Corporate Scan}
def crack_menu_8():
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
    if WIRELESS_BOOLEAN:
        return
    elif HM_ANSWER == '0':
        hc_cmd2 = ['hashcat', '-m', HASH_TYPE, '-a', '0', '--username', '--session', 'all', '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME]
        subprocess.call(hc_cmd2)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
        subprocess.call('rm' + ' ' + os.path.join(L00T_POT_DIR, POT + '.format3'), shell=True)
    elif HM_ANSWER == '1' or HM_ANSWER == '2':
        hc_cmd3 = ['hashcat', '-m', HASH_TYPE, '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--session', 'all']
        subprocess.call(hc_cmd3)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
        subprocess.call('rm' + ' ' + os.path.join(L00T_POT_DIR, POT + '.format3'), shell=True)
    else:
        return

#Crack Menu 9 - Rockyou with rule - d3ad0ne
def crack_menu_9():
    WORDLIST_DIRECTORY = "/opt/wordlists" # Needed to reset the wordlist directory.
    global DEFAULT_CEWL_FILE_OUTPUT
    global HASH_PATH_AND_NAME
    global SINGLE_HASH_BOOLEAN
    global FILE_HASH_BOOLEAN
    global RULE_SET_DIRECTORY
    if CEWL_BOOLEAN and FILE_HASH_BOOLEAN or SINGLE_HASH_BOOLEAN and CEWL_BOOLEAN or WIRELESS_BOOLEAN and CEWL_BOOLEAN:
        SINGLE_WORDLIST = DEFAULT_CEWL_FILE_OUTPUT
    elif WIRELESS_BOOLEAN and not CEWL_BOOLEAN:
        HASH_PATH_AND_NAME = os.path.join(WIRELESS_UPLOAD_DIR, WIRELESS_INPUT)
        SINGLE_WORDLIST = os.path.join(WORDLIST_DIRECTORY, 'rockyou.txt')
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
    if WIRELESS_BOOLEAN:
        return
    elif HM_ANSWER == '0':
        hc_cmd2 = ['hashcat', '-m', HASH_TYPE, '-a', '0', '--username', '--session', 'all', '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME]
        subprocess.call(hc_cmd2)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
        subprocess.call('rm' + ' ' + os.path.join(L00T_POT_DIR, POT + '.format3'), shell=True)
    elif HM_ANSWER == '1' or HM_ANSWER == '2':
        hc_cmd3 = ['hashcat', '-m', HASH_TYPE, '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_ABS_PATH, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--session', 'all']
        subprocess.call(hc_cmd3)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
        subprocess.call('rm' + ' ' + os.path.join(L00T_POT_DIR, POT + '.format3'), shell=True)
    else:
        return

#Crack Menu 10 - Rockyou with rule - OneRuleToRuleThemAll
def crack_menu_10():
    WORDLIST_DIRECTORY = "/opt/wordlists" # Needed to reset the wordlist directory.
    global SINGLE_HASH_BOOLEAN
    global FILE_HASH_BOOLEAN
    global HASH_PATH_AND_NAME
    global RULE_SET_DIRECTORY
    if CEWL_BOOLEAN and FILE_HASH_BOOLEAN or SINGLE_HASH_BOOLEAN and CEWL_BOOLEAN or WIRELESS_BOOLEAN and CEWL_BOOLEAN:
        SINGLE_WORDLIST = DEFAULT_CEWL_FILE_OUTPUT
    elif WIRELESS_BOOLEAN:
        HASH_PATH_AND_NAME = os.path.join(WIRELESS_UPLOAD_DIR, WIRELESS_INPUT)
        SINGLE_WORDLIST = os.path.join(WORDLIST_DIRECTORY, 'rockyou.txt')
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
    if WIRELESS_BOOLEAN:
        return
    elif HM_ANSWER == '0':
        hc_cmd2 = ['hashcat', '-m', HASH_TYPE, '-a', '0', '--username', '--session', 'all', '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_ABS_PATH]
        subprocess.call('rm' + ' ' + os.path.join(L00T_POT_DIR, POT + '.format3'), shell=True)
        subprocess.call(hc_cmd2)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
    elif HM_ANSWER == '1' or HM_ANSWER == '2':
        hc_cmd3 = ['hashcat', '-m', HASH_TYPE, '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--session', 'all']
        subprocess.call(hc_cmd3)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
        subprocess.call('rm' + ' ' + os.path.join(L00T_POT_DIR, POT + '.format3'), shell=True)
    else:
        return

#Crack Menu 11 - Rockyou with rule - # Changed to add leet speak rules
def crack_menu_11():
    WORDLIST_DIRECTORY = "/opt/wordlists" # Needed to reset the wordlist directory.
    global DEFAULT_CEWL_FILE_OUTPUT
    global HASH_PATH_AND_NAME
    if CEWL_BOOLEAN and FILE_HASH_BOOLEAN or SINGLE_HASH_BOOLEAN and CEWL_BOOLEAN or WIRELESS_BOOLEAN and CEWL_BOOLEAN:
        SINGLE_WORDLIST = DEFAULT_CEWL_FILE_OUTPUT
    elif WIRELESS_BOOLEAN:
        HASH_PATH_AND_NAME = os.path.join(WIRELESS_UPLOAD_DIR, WIRELESS_INPUT)
        SINGLE_WORDLIST = os.path.join(WORDLIST_DIRECTORY, 'rockyou.txt')
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
    if WIRELESS_BOOLEAN:
        return
    elif HM_ANSWER == '0':
        hc_cmd2 = ['hashcat', '-m', HASH_TYPE, '-a', '0', '--username', '--session', 'all', '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME]
        subprocess.call(hc_cmd2)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
        subprocess.call('rm' + ' ' + os.path.join(L00T_POT_DIR, POT + '.format3'), shell=True)
    elif HM_ANSWER == '1' or HM_ANSWER == '2':
        hc_cmd3 = ['hashcat', '-m', HASH_TYPE, '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--session', 'all']
        subprocess.call(hc_cmd3)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
        subprocess.call('rm' + ' ' + os.path.join(L00T_POT_DIR, POT + '.format3'), shell=True)
    else:
        return

#Crack Menu 12 - Rockastic with OneRuleToRuleThemAll
def crack_menu_12():
    WORDLIST_DIRECTORY = "/opt/wordlists" # Needed to reset the wordlist directory.
    global DEFAULT_CEWL_FILE_OUTPUT
    global FILE_HASH_BOOLEAN
    global HASH_PATH_AND_NAME
    if CEWL_BOOLEAN and FILE_HASH_BOOLEAN or SINGLE_HASH_BOOLEAN and CEWL_BOOLEAN or WIRELESS_BOOLEAN and CEWL_BOOLEAN:
        SINGLE_WORDLIST = DEFAULT_CEWL_FILE_OUTPUT
    elif WIRELESS_BOOLEAN:
        HASH_PATH_AND_NAME = os.path.join(WIRELESS_UPLOAD_DIR, WIRELESS_INPUT)
        SINGLE_WORDLIST = os.path.join(WORDLIST_DIRECTORY, '4GB+/Rocktastic12a.txt')
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
    if WIRELESS_BOOLEAN:
        return
    elif HM_ANSWER == '0':
        hc_cmd2 = ['hashcat', '-m', HASH_TYPE, '-a', '0', '--username', '--session', 'all', '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME]
        subprocess.call(hc_cmd2)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
        subprocess.call('rm' + ' ' + os.path.join(L00T_POT_DIR, POT + '.format3'), shell=True)
    elif HM_ANSWER == '1' or HM_ANSWER == '2':
        hc_cmd3 = ['hashcat', '-m', HASH_TYPE, '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--session', 'all']
        subprocess.call(hc_cmd3)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
        subprocess.call('rm' + ' ' + os.path.join(L00T_POT_DIR, POT + '.format3'), shell=True)
    else:
        return

#Crack Menu 13 - Rocktastic with dive rule
def crack_menu_13():
    WORDLIST_DIRECTORY = "/opt/wordlists" # Needed to reset the wordlist directory.
    global DEFAULT_CEWL_FILE_OUTPUT
    global HASH_PATH_AND_NAME
    global SINGLE_HASH_BOOLEAN
    global FILE_HASH_BOOLEAN
    global RULE_SET_DIRECTORY
    if CEWL_BOOLEAN and FILE_HASH_BOOLEAN or SINGLE_HASH_BOOLEAN and CEWL_BOOLEAN or WIRELESS_BOOLEAN and CEWL_BOOLEAN:
        SINGLE_WORDLIST = DEFAULT_CEWL_FILE_OUTPUT
    elif WIRELESS_BOOLEAN:
        HASH_PATH_AND_NAME = os.path.join(WIRELESS_UPLOAD_DIR, WIRELESS_INPUT)
        SINGLE_WORDLIST = os.path.join(WORDLIST_DIRECTORY, '4GB+/Rocktastic12a.txt')
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
    if WIRELESS_BOOLEAN:
        return
    elif HM_ANSWER == '0':
        hc_cmd2 = ['hashcat', '-m', HASH_TYPE, '-a', '0', '--username', '--session', 'all', '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME]
        subprocess.call(hc_cmd2)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
        subprocess.call('rm' + ' ' + os.path.join(L00T_POT_DIR, POT + '.format3'), shell=True)
    elif HM_ANSWER == '1' or HM_ANSWER == '2':
        hc_cmd3 = ['hashcat', '-m', HASH_TYPE, '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--session', 'all']
        subprocess.call(hc_cmd3)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
        subprocess.call('rm' + ' ' + os.path.join(L00T_POT_DIR, POT + '.format3'), shell=True)
    else:
        return

#Crack Menu 14 - Rocktastic with Hob0Rules -> Quick {hob064.rule} -> Comprenensive Test {d3adhob0.rule}
def crack_menu_14():
    WORDLIST_DIRECTORY = "/opt/wordlists" # Needed to reset the wordlist directory.
    global SINGLE_HASH_BOOLEAN
    global FILE_HASH_BOOLEAN
    global HASH_PATH_AND_NAME
    global RULE_SET_DIRECTORY
    if CEWL_BOOLEAN and FILE_HASH_BOOLEAN or SINGLE_HASH_BOOLEAN and CEWL_BOOLEAN or WIRELESS_BOOLEAN and CEWL_BOOLEAN:
        SINGLE_WORDLIST = DEFAULT_CEWL_FILE_OUTPUT
    elif WIRELESS_BOOLEAN:
        HASH_PATH_AND_NAME = os.path.join(WIRELESS_UPLOAD_DIR, WIRELESS_INPUT)
        SINGLE_WORDLIST = os.path.join(WORDLIST_DIRECTORY, '4GB+/Rocktastic12a.txt')
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
    if WIRELESS_BOOLEAN:
        return
    elif HM_ANSWER == '0' or HM_ANSWER == '1' or HM_ANSWER == '2':
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
        subprocess.call('rm' + ' ' + os.path.join(L00T_POT_DIR, POT + '.format3'), shell=True)
        os.system('clear')
    else:
        os.system('clear')
    hc2 = ['hashcat', '-a', '0', '-m', HASH_TYPE, HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), SINGLE_WORDLIST, '-r', os.path.join(RULES_DIR, 'd3adhob0.rule'), '-w', '3', '-O']
    subprocess.call(hc2)
    if HM_ANSWER == '0':
        hc_cmd2 = ['hashcat', '-m', HASH_TYPE, '-a', '0', '--username', '--session', 'all', '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME]
        subprocess.call(hc_cmd2)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
        subprocess.call('rm' + ' ' + os.path.join(L00T_POT_DIR, POT + '.format3'), shell=True)
    elif HM_ANSWER == '1' or HM_ANSWER == '2':
        hc_cmd3 = ['hashcat', '-m', HASH_TYPE, '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--session', 'all']
        subprocess.call(hc_cmd3)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
        subprocess.call('rm' + ' ' + os.path.join(L00T_POT_DIR, POT + '.format3'), shell=True)
    else:
        return

#Crack Menu 15 - Auto Multi Rule Test - Iterate through each rule with rockyou.txt - {Corporate Scan}
def crack_menu_15():
    WORDLIST_DIRECTORY = "/opt/wordlists" # Needed to reset the wordlist directory.
    global SINGLE_WORDLIST
    global DEFAULT_CEWL_FILE_OUTPUT
    global HASH_ABS_PATH
    global RULE_SET_DIRECTORY
    if CEWL_BOOLEAN and FILE_HASH_BOOLEAN or SINGLE_HASH_BOOLEAN and CEWL_BOOLEAN or WIRELESS_BOOLEAN and CEWL_BOOLEAN:
        SINGLE_WORDLIST = DEFAULT_CEWL_FILE_OUTPUT
    elif WIRELESS_BOOLEAN:
        HASH_PATH_AND_NAME = os.path.join(WIRELESS_UPLOAD_DIR, WIRELESS_INPUT)
        SINGLE_WORDLIST = os.path.join(WORDLIST_DIRECTORY, 'rockyou.txt')
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

#Rsmangler - Create multiple permutations of a word - Menu 19)
def rsmangler_menu():
    global SINGLE_HASH_BOOLEAN
    global SINGLE_WORDLIST
    global CEWL_BOOLEAN
    global FILE_HASH_BOOLEAN
    global WIRELESS_INPUT
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
        SINGLE_WORDLIST = RSMANGLER_OUTPUT_DIR_AND_FIRMNAME #Space added for correct argument spacing
    elif SINGLE_HASH_BOOLEAN and CEWL_BOOLEAN or WIRELESS_BOOLEAN and CEWL_BOOLEAN:
        SINGLE_WORDLIST = DEFAULT_CEWL_FILE_OUTPUT
    elif FILE_HASH_BOOLEAN and CEWL_BOOLEAN == False:
        SINGLE_WORDLIST = RSMANGLER_OUTPUT_DIR_AND_FIRMNAME #Space added for correct argument spacing
    elif FILE_HASH_BOOLEAN and CEWL_BOOLEAN:
        SINGLE_WORDLIST = DEFAULT_CEWL_FILE_OUTPUT
    elif WIRELESS_BOOLEAN and not CEWL_BOOLEAN:
        SINGLE_WORDLIST = RSMANGLER_OUTPUT_DIR_AND_FIRMNAME
        os.chdir(WIRELESS_UPLOAD_DIR)
    else:
        pass
    os.system('clear')
    hc = ['hashcat', '-a', '0', '-m', HASH_TYPE, HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), SINGLE_WORDLIST, '-r', os.path.join(RULES_DIR, 'OneRuleToRuleThemAll.rule'), '-w', '3', '-O']
    subprocess.call(hc)
    #Right Side
    hc1 = ['hashcat', '-a', '6', '-m', HASH_TYPE, HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), SINGLE_WORDLIST, '?a?a?a?a', '-w', '3', '-O', '--increment']
    subprocess.call(hc1)
    if WIRELESS_BOOLEAN:
        return
    elif HM_ANSWER == '0' or HM_ANSWER == '1' or HM_ANSWER == '2':
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
        subprocess.call('rm' + ' ' + os.path.join(L00T_POT_DIR, POT + '.format3'), shell=True)
        os.system('clear')
    else:
        os.system('clear')
    #Left Side
    hc2 = ['hashcat', '-a', '7', '-m', HASH_TYPE, HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '?a?a?a?a', SINGLE_WORDLIST, '-w', '3', '-O', '--increment']
    subprocess.call(hc2)
    if WIRELESS_BOOLEAN:
        return
    elif HM_ANSWER == '0':
        hc_cmd2 = ['hashcat', '-m', HASH_TYPE, '-a', '0', '--username', '--session', 'all', '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME]
        subprocess.call(hc_cmd2)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
        subprocess.call('rm' + ' ' + os.path.join(L00T_POT_DIR, POT + '.format3'), shell=True)
    elif HM_ANSWER == '1' or HM_ANSWER == '2':
        hc_cmd3 = ['hashcat', '-m', HASH_TYPE, '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--session', 'all']
        subprocess.call(hc_cmd3)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
        subprocess.call('rm' + ' ' + os.path.join(L00T_POT_DIR, POT + '.format3'), shell=True)
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
    elif WIRELESS_BOOLEAN:
        cewl_hash_input = WIRELESS_INPUT + '.cewl-list.txt'
    else:
        pass
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
    global WIRELESS_INPUT
    if CEWL_BOOLEAN and FILE_HASH_BOOLEAN or SINGLE_HASH_BOOLEAN and CEWL_BOOLEAN:
        SINGLE_WORDLIST = DEFAULT_CEWL_FILE_OUTPUT
    elif WIRELESS_BOOLEAN and CEWL_BOOLEAN:
        SINGLE_WORDLIST = WIRELESS_INPUT
    else:
        raw_input("Cewl Wordlist not ran yet!, run cewl first, (Option 16)")
        crack_menu()
    pot_function()
    hc = ['hashcat', '-a', '0', '-m', HASH_TYPE, HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), SINGLE_WORDLIST, '-w', '3', '-O']
    subprocess.call(hc)
    if WIRELESS_BOOLEAN:
        return
    elif HM_ANSWER == '0':
        hc_cmd2 = ['hashcat', '-m', HASH_TYPE, '-a', '0', '--username', '--session', 'all', '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME]
        subprocess.call(hc_cmd2)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
        subprocess.call('rm' + ' ' + os.path.join(L00T_POT_DIR, POT + '.format3'), shell=True)
    elif HM_ANSWER == '1' or HM_ANSWER == '2':
        hc_cmd3 = ['hashcat', '-m', HASH_TYPE, '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--session', 'all']
        subprocess.call(hc_cmd3)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
        subprocess.call('rm' + ' ' + os.path.join(L00T_POT_DIR, POT + '.format3'), shell=True)
    else:
        return
    return

#Automated Cewl wordlist - {4 ANY Characters RIGHT --> LEFT incrementally} (could take a while dependant on size of cewl wordlist generated)
def cewl_menu_18():
    global SINGLE_WORDLIST
    global SINGLE_HASH_BOOLEAN
    global DEFAULT_CEWL_FILE_OUTPUT
    global CEWL_BOOLEAN
    global FILE_HASH_BOOLEAN
    if CEWL_BOOLEAN and FILE_HASH_BOOLEAN or SINGLE_HASH_BOOLEAN and CEWL_BOOLEAN or WIRELESS_BOOLEAN and CEWL_BOOLEAN:
        SINGLE_WORDLIST = DEFAULT_CEWL_FILE_OUTPUT
    elif WIRELESS_BOOLEAN and not CEWL_BOOLEAN:
        SINGLE_WORDLIST = WIRELESS_INPUT
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
    if WIRELESS_BOOLEAN:
        return
    elif HM_ANSWER == '0':
        hc_cmd2 = ['hashcat', '-m', HASH_TYPE, '-a', '0', '--username', '--session', 'all', '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME]
        subprocess.call(hc_cmd2)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, pot) + '.sorted ', shell=True)
        subprocess.call('rm' + ' ' + os.path.join(L00T_POT_DIR, POT + '.format3'), shell=True)
    elif HM_ANSWER == '1' or HM_ANSWER == '2':
        hc_cmd3 = ['hashcat', '-m', HASH_TYPE, '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--session', 'all']
        subprocess.call(hc_cmd3)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
        subprocess.call('rm' + ' ' + os.path.join(L00T_POT_DIR, POT + '.format3'), shell=True)
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
    if CEWL_BOOLEAN and FILE_HASH_BOOLEAN or SINGLE_HASH_BOOLEAN and CEWL_BOOLEAN or WIRELESS_BOOLEAN and CEWL_BOOLEAN:
        SINGLE_WORDLIST = DEFAULT_CEWL_FILE_OUTPUT
    elif WIRELESS_BOOLEAN and not CEWL_BOOLEAN:
        SINGLE_WORDLIST = WIRELESS_INPUT
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
        subprocess.call('rm' + ' ' + os.path.join(L00T_POT_DIR, POT + '.format3'), shell=True)
    else:
        os.system('clear')
    hc1 = ['hashcat', '-a', '0', '-m', HASH_TYPE, HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), SINGLE_WORDLIST, '-r', os.path.join(RULES_DIR, 'dive.rule'), '-w', '3', '-O']
    subprocess.call(hc1)
    hc2 = ['hashcat', '-a', '0', '-m', HASH_TYPE, HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), SINGLE_WORDLIST, '-r', os.path.join(RULES_DIR, 'OneRuleToRuleThemAll.rule'), '-w', '3', '-O']
    subprocess.call(hc2)
    if WIRELESS_BOOLEAN:
        return
    elif HM_ANSWER == '0':
        hc_cmd2 = ['hashcat', '-m', HASH_TYPE, '-a', '0', '--username', '--session', 'all', '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME]
        subprocess.call(hc_cmd2)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
    elif HM_ANSWER == '1' or HM_ANSWER == '2':
        hc_cmd3 = ['hashcat', '-m', HASH_TYPE, '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--session', 'all']
        subprocess.call(hc_cmd3)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
    else:
        return

#Any Menu - Menu c)
def any_menu():
    if ALL_MENU:
        pot_function()
    else:
        banner()
        hash_mode_menu()
        pot_function()
    os.system('clear')
    hc1 = ['hashcat', '-a', '3', '-m', HASH_TYPE, HASH_PATH_AND_NAME, '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--increment', "?a?a?a?a?a?a?a?a?a?a?a?a", '-w', '3', '-O']
    subprocess.call(hc1)
    if WIRELESS_BOOLEAN:
        return
    elif HM_ANSWER == '0':
        hc_cmd2 = ['hashcat', '-m', HASH_TYPE, '-a', '0', '--username', '--session', 'all', '--potfile-path=' + os.path.join(L00T_POT_DIR, POT), '--show', '-o', os.path.join(L00T_POT_DIR, POT + '.format3'), '--outfile-format', '3', HASH_PATH_AND_NAME]
        subprocess.call(hc_cmd2)
        subprocess.call(AWK + os.path.join(L00T_POT_DIR, POT + '.format3') + " | sort > " + os.path.join(L00T_POT_DIR, POT) + '.sorted ', shell=True)
    elif HM_ANSWER == '1' or HM_ANSWER == '2':
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
    global USER_ONLY_BOOLEAN
    global WIRELESS_BOOLEAN
    ALL_MENU = False # Needed to reset for the automatic menu.
    CEWL_BOOLEAN = False # Needed to reset for new menu settings to be applied.
    SINGLE_HASH_BOOLEAN = False # Needed to reset for new menu settings to be applied.
    FILE_HASH_BOOLEAN = False # Needed to reset for new menu settings to be applied.
    POT_BOOLEAN = False # Needed to reset for new menu settings to be applied.
    USER_ONLY_BOOLEAN = False # Needed to reset for new menu settings to be applied.
    WIRELESS_BOOLEAN = False # Needed to reset for new menu settings to be applied.
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
    global OUT
    global USER_ONLY_BOOLEAN
    global WIRELESS_BOOLEAN
    global WIRELESS_HASHES_LOADED
    os.system('clear')
    banner()
    try:
        while 1:
            if SINGLE_HASH_BOOLEAN and not CEWL_BOOLEAN:
                print""
                print'\t\t\t\t' + '\033[40m' + '--==Single Hash Cracking Menu==--' + '\033[0m'
                print""
                print""
                print" Hash file created:"
                prYellow(SINGLE_HASH_ABS_PATH)
            elif SINGLE_HASH_BOOLEAN and CEWL_BOOLEAN:
                print""
                print'\t\t\t\t' + '\033[40m' + '--==Single Hash Cewl Cracking Menu==--' + '\033[0m'
                print""
                print""
                print" Single Hash file in Use:"
                prYellow(SINGLE_HASH_ABS_PATH)
                print" Cewl Wordlist in Use:"
                prYellow(DEFAULT_CEWL_FILE_OUTPUT)
            elif FILE_HASH_BOOLEAN and USER_ONLY_BOOLEAN: #Option 2
                banner()
                if not HASH_ABS_PATH.endswith('_users'):
                    HASH_ABS_PATH += '_users'
                    POT = HASH_INPUT + '_users.pot'
                if not HASH_INPUT.endswith('_users'):
                    POT = HASH_INPUT + '_users'
                else:
                    POT = HASH_INPUT
                print""
                POT = POT.lower()
                POT += '.pot'
                pot_absolute = os.path.join(L00T_POT_DIR, POT)
                print'\t\t\t\t\t' + '\033[40m' + '--==Multi Hash Cracking Menu==--' + '\033[0m'
                print""
                print""
                print" " + "Hash File Loaded:  ",
                prYellow(HASH_USER)
                print" " + "Hashes Loaded:     ",
                prRed(HASHES_LOADED)
                if os.path.exists(pot_absolute):
                    with open(pot_absolute) as lines:
                        hashes_cracked = len(lines.readlines())
                        print' ' + "Hashes Cracked:    ",
                        print' ' + '\033[92m' + str(hashes_cracked) + '\033[0m'
                        print' ' + 'Percentage Cracked:',
                        percent_cracked = (hashes_cracked * 100.00 / HASHES_LOADED)
                        print' ' + '\033[34m' + str(percent_cracked) + ('%') + '\033[0m'
                else:
                    print' ' + "Hashes Cracked:    ",
                    prRed("0")
                    print' ' + 'Percentage Cracked:',
                    print'\033[34m' + ' ' + str(0) + ('%') + '\033[0m'
            elif FILE_HASH_BOOLEAN and not CEWL_BOOLEAN and not USER_ONLY_BOOLEAN: #Option 1
                banner()
                POT = HASH_INPUT.lower()
                POT += '.pot'
                pot_absolute = os.path.join(L00T_POT_DIR, POT)
                print'\t\t\t\t\t' + '\033[40m' + '--==Multi Hash Cracking Menu==--' + '\033[0m'
                print""
                print""
                print" " + "Hash File Loaded:  ",
                prYellow(HASH_INPUT)
                print" " + "Hashes Loaded:     ",
                prRed(HASHES_LOADED)
                if os.path.exists(pot_absolute):
                    with open(pot_absolute) as lines:
                        hashes_cracked = len(lines.readlines())
                        print' ' + "Hashes Cracked:    ",
                        print' ' + '\033[92m' + str(hashes_cracked) + '\033[0m'
                        print' ' + 'Percentage Cracked:',
                        percent_cracked = (hashes_cracked) * 100.00 / (HASHES_LOADED)
                        print' ' + '\033[34m' + str(percent_cracked) + ('%') + '\033[0m'
                else:
                    print' ' + "Hashes Cracked:    ",
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
            elif WIRELESS_BOOLEAN: #Option 3
                banner() # Currently display duplicates first time round, second time round it only shows one banner.. 
                print""
                print'\t\t\t\t\t' + '\033[40m' + '--==Multi Hash Cracking Menu==--' + '\033[0m'
                print""
                print""
                print" " + "Hash File Loaded:  ",
                prYellow(WIRELESS_INPUT)
                print" " + "Networks Detected:  ",
                print NETWORKS_DETECTED.strip()
                print" " + "SSID Loaded:     ",
                print '   ' + '\033[34m' + str(ESSID[2]).strip() + '\033[0m'
                print' Hash Status:    ',
                POT = WIRELESS_INPUT.lower()
                POT += '.pot'
                pot_absolute = os.path.join(L00T_POT_DIR, POT)
                #Clean up and any excess pot files that are 0 bytes                                  
                subprocess.check_call(['find', L00T_POT_DIR, '-type', 'f', '-size', '0b', '-delete'])
                if os.path.exists(pot_absolute):
                    with open(pot_absolute, "r") as hashes:
                        firstLine = hashes.readline()
                        hash_read = csv.reader(hashes, delimiter=':')
                        for hash_column in hash_read:
                            print'    ' + '\033[41m' + 'Cracked!' + '\033[0m'
                            print' Password:            ' + '\033[92m' + hash_column[1] + '\033[0m'
                else:
                    prRed("   Not Yet!")
            else:
                pass
            print""
            print' ' + '\033[44m' + 'Supported - NTLM -> NetNTLMv1 -> NetNTLMv2 -> MD5 -> SHA-512 -> RC4-HMAC-MD5' + '\033[0m'
            print""
            prCyan("0) A single merged list of wordlists in the public domain")
            prLightPurple("1) Common Wordlists - includes rockyou, hashkiller")
            prCyan("2) Special lists - UK and US Cities with OneRuleToRuleThemAll")
            prLightPurple("3) +8 chars + 0-9 + UCASE + LCASE (with diacritic marks, Greek & Cyrillic chars)")
            prCyan("4) All wordlists 4GB+ - {Incremental Scan}")
            prLightPurple("5) Oxford Dict Start UPPER Case + upto 3 ANY Chars on RIGHT SIDE")
            prCyan("6) Oxford Dict Start UPPER Case + upto 3 ANY Chars on LEFT SIDE")
            prLightPurple("7) Oxford Dict Start UPPER Case + upto 4 digits LEFT SIDE, upto 4 digits RIGHT SIDE")
            prCyan("8) Oxford Dict MIXED CASE + upto 3 ANY Chars on RIGHT SIDE")
            prLightPurple("9) Rule - Rockyou or cewl - d3ad0ne")
            prCyan("10) Rule - Rockyou or cewl - OneRuleToRuleThemAll")
            prLightPurple("11) Rule - Rockyou or cewl - L33t speak rules (leetspeak.rule + unix-ninja-leetspeak)")
            prCyan("12) Rule - Rocktastic or cewl -> OneRuleToRuleThemAll")
            prLightPurple("13) Rule - Rocktastic with dive rule")
            prCyan("14) Rule - Rocktastic or cewl -> Quick {hob064.rule} -> Comprehensive {d3adhob0.rule}")
            prLightPurple("15) Auto Multi Rule Test - Iterate through each rule with rockyou.txt")
            prCyan("16) Cewl Test - Enter the firms website to create a bespoke, focussed wordlist")
            prLightPurple("17) Straight Cewl wordlist - (Run option 16 first to activate)")
            prCyan("18) Auto Cewl wordlist - {4 ANY Characters RIGHT --> LEFT incrementally -> Dive Rule}")
            prLightPurple("19) Wordlist Mangling Tool - Various permutations of a specified word")
            prCyan("a) Multiple Tests - All of the above, mainly in ascending numerical order")
            prLightPurple("b) Passphrases testing - Multiple words strung together using multiple rule sets")
            prCyan("c) Auto Increment ANY combination upto 12 characters '?a?a?a?a?a?a?a?a?a?a?a?a'")
            prRed("x) Back to Main Menu")
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
                            "x": back_crack
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
    print'\033[33m' + ' ' + '\t\tWelcome to the Manual Hash upload Function' + '\033[0m'
    print'\033[33m' + ' ' + 'Please enter your hash below as prompted, an example hash is shown.' + '\033[0m'
    print''
    print' ' + '\033[44m' + 'Supported - NTLM -> NetNTLMv1 -> NetNTLMv2 -> MD5 -> SHA-512 -> RC4-HMAC-MD5' + '\033[0m'
    print''
    print'\033[34m' + ' ' + 'Example NetNTLMv2 Hash - (Password = "hashcat")' + '\033[0m'
    print' ' + 'admin::N46iSNekpT:08ca45b7d7ea58ee:88dcbe4446168966a153a0064958dac6:5c7830315c78303'
    print' ' + '10000000000000b45c67103d07d7b95acd12ffa11230e0000000052920b85f78d013c31cdb3b92f3030'
    print''
    single_hash = raw_input(' Input your hash or type ' +  '\033[31m' + '"back"' + '\033[0m' + ' to go back to the main menu' + '\n\n' + ' ')
    if single_hash == "back" or single_hash == "Back" or single_hash == "BACK":
        main_menu()
    else:
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
    global FILE_HASH_BOOLEAN
    global HASH_ABS_PATH
    global HASH_INPUT
    global HASHES_LOADED
    global HASH_UPLOAD_DIR
    global HASH_USERS_ONLY
    global HASH_USER
    global USER_ONLY_BOOLEAN
    FILE_HASH_BOOLEAN = True
    os.system('clear')
    banner()
    print'\033[33m' + ' ' + 'Add hash files into the hash upload directory shown below:' + '\033[0m'
    prCyan(HASH_UPLOAD_DIR)
    print""
    print'\033[34m' + ' ' + 'Below are the files in the hash upload directory.. (Hit Enter to Refresh) (TAB Completion On)' + '\033[0m'
    print""
    #Used for removing emacs created backup files ending with a tilde
    ignore = '~'
    for root, dirs, files in os.walk(HASH_UPLOAD_DIR):
        files.sort()
        for f in files:
            if not f.endswith(ignore):
                print" \t" + os.path.join(f)
    print""
    print'\033[33m' + ' ' + 'Select the filename from the above list to be uploaded' + 'or type ' + '\033[0m' + '\033[31m' + '"back"' + '\033[0m'
    os.chdir(HASH_UPLOAD_DIR)
    readline.parse_and_bind("tab: complete")
    HASH_INPUT = raw_input(str("------> "))
    HASH_ABS_PATH = str(os.path.join(HASH_UPLOAD_DIR, HASH_INPUT))
    HASH_USER = HASH_INPUT + '_users'
    HASH_USERS_ONLY = HASH_ABS_PATH + '_users'
    if HASH_INPUT == ('back') or HASH_INPUT == ('Back') or HASH_INPUT == ('BACK'):
        main_menu()
    try:
        if os.path.isfile(HASH_INPUT):
            if USER_ONLY_BOOLEAN == False:# and os.path.isfile(HASH_INPUT): #Option 1
                uniq = open(HASH_ABS_PATH, 'r').read()
                uniq = uniq.split()
                clean_list = []
                for word in uniq:
                    if word not in clean_list:
                        clean_list.append(word)
                HASHES_LOADED = len(uniq) 
                HASH_USER = HASH_INPUT #Take the user input and continue to crack menu.
            elif USER_ONLY_BOOLEAN and HASH_INPUT.endswith('_users'): #Option2 - If the input ends with '_users' 
                HASH_USER = HASH_INPUT
                with open(HASH_USER) as lines:
                    HASHES_LOADED = len(lines.readlines())
            elif USER_ONLY_BOOLEAN and os.path.isfile(HASH_USERS_ONLY): #Option 2 - Another File Exists with (_users)
                HASH_USER = HASH_INPUT + '_users' #Select the file that exists already with _users on the filename
                with open(HASH_USER) as lines:
                    HASHES_LOADED = len(lines.readlines())
            else:
                if USER_ONLY_BOOLEAN and not os.path.isfile(HASH_USERS_ONLY): #Option 2 - File with (_users) doesn't not exist.
                    for x in files:
                        if not x.endswith('_users') and not os.path.exists(HASH_USERS_ONLY):
                            AWK_DOLLAR_SPLIT = "'!/^[^:]*\$[^:]*:/'"
                            convert = ("awk" + " " + AWK_DOLLAR_SPLIT + " " + HASH_ABS_PATH + " > " + HASH_USERS_ONLY)
                            subprocess.call(convert, shell=True)
                            with open(HASH_USERS_ONLY) as lines:
                                HASHES_LOADED = len(lines.readlines())
        else:
            print' ' + 'Error:' + ' ' + HASH_INPUT + ' ' + 'file not found' + ' ' + 'try again or type ' + '\033[31m' + 'back' + '\033[0m' 
            time.sleep(1)
            os.system('clear')
            hash_from_file()
    except KeyError:
        os.system('clear')
        pass
    else:
        pass
    os.system('clear')
    crack_menu()

#Wireless Menu
#This menu selects either the .hccapx file or converts the .cap file to .hccapx on the fly.
def wireless_menu():
    global ESSID
    global NETWORKS_DETECTED
    global WIRELESS_ABS_PATH
    global WIRELESS_BOOLEAN
    global WIRELESS_HASHES_LOADED
    global WIRELESS_INPUT
    WIRELESS_BOOLEAN = True
    banner()
    print"Select the capture file from the capture_upload directory\n"
    print""
    #Used for removing emacs created backup files ending with a tilde
    ext1 = '.cap'
    ext2 = 'hccapx'
    for root, dirs, files in os.walk(WIRELESS_UPLOAD_DIR):
        files.sort()
        for f in files:
            if f.endswith(ext1) or f.endswith(ext2):
                print" \t" + os.path.join(f)
    print""
    print'\033[33m' + ' ' + 'Select the filename from the above list to be uploaded' + ' or type ' + '\033[0m' + '\033[31m' + '"back"' + '\033[0m'
    os.chdir(WIRELESS_UPLOAD_DIR)
    readline.parse_and_bind("tab: complete")
    WIRELESS_INPUT = raw_input("------> ")
    if WIRELESS_INPUT == ('back') or WIRELESS_INPUT == ('Back') or WIRELESS_INPUT == ('BACK'):
        main_menu()
    try:
        if os.path.isfile(WIRELESS_INPUT):
            if WIRELESS_INPUT.endswith(CAP_FILE_EXT): #If a .cap file is selected, we convert it to .hccapx
                STRIP_CAP_FILE = os.path.splitext(WIRELESS_INPUT)[0] #Strip off the file ext
                HCCAPX_FILE = STRIP_CAP_FILE + '.hccapx' #Add .hccapx
                print'You have selected the capture file' + ' ' + WIRELESS_INPUT
                time.sleep(1)
                print''
                print'We will now convert the capture file' + ' ' + '\033[33m' + WIRELESS_INPUT + '\033[0m' + ' ' + 'into' + ' ' + '\033[92m' + HCCAPX_FILE + '\033[0m' + ' ' + 'for hashcat to process.....'
                print''
                time.sleep(4)
                p = subprocess.Popen([os.path.join(TOOLS_DIR, 'cap2hccapx.bin'), WIRELESS_INPUT, HCCAPX_FILE], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
                while p.poll() is None:
                    time.sleep(0.5)
                if p.returncode == 0:
                    a = p.stdout.readlines() #Put the output into a list
                    print a
                    NETWORKS_DETECTED = a[0]
                    NETWORKS_DETECTED = str(NETWORKS_DETECTED).strip(' ')[19] #Extract the number of Networks detected for aesthetics for wireless_menu()
                    print NETWORKS_DETECTED
                    ESSID = a[2].split('=')
                    print ESSID[2]
                else:
                    print p.returncode
                    print 'File corrupted - (Invalid Pcap Header) - Returning to the main menu'
                    time.sleep(3)
                WIRELESS_ABS_PATH = (os.path.join(WIRELESS_UPLOAD_DIR, HCCAPX_FILE))
                main_menu()# Current issue workaround - we cant directly select the .hccapx due to hashcat error message.
            elif WIRELESS_INPUT.endswith(HCCAPX_FILE_EXT): #In order to get the display data, we can only get it from the cap file.
                STRIP_HCCAPX_FILE = os.path.splitext(WIRELESS_INPUT)[0] #Strip off the extension
                CAP_FILE = STRIP_HCCAPX_FILE + '.cap'
                WIRELESS_ABS_PATH = (os.path.join(WIRELESS_UPLOAD_DIR, WIRELESS_INPUT))
                p = subprocess.Popen([os.path.join(TOOLS_DIR, 'cap2hccapx.bin'), CAP_FILE, WIRELESS_INPUT], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
                while p.poll() is None:
                    time.sleep(0.5)
                if p.returncode == 0:
                    a = p.stdout.readlines() #Put the output into a list                                                                                 
                    NETWORKS_DETECTED = a[0]
                    NETWORKS_DETECTED = str(NETWORKS_DETECTED).strip(' ')[19] #Extract the number of Networks detected for aesthetics for wireless_menu()
                    print NETWORKS_DETECTED
                    ESSID = a[2].split('=')
                else:
                    print p.returncode
                    print 'File corrupted - (Invalid Pcap Header) - Returning to the main menu'
                    time.sleep(3)
                STRIP_CAP_FILE = os.path.splitext(CAP_FILE)[0] #Strip off the '.cap'
                HCCAPX_FILE = CAP_FILE + '.hccapx'# Put the file extension back on
                WIRELESS_ABS_PATH = (os.path.join(WIRELESS_UPLOAD_DIR, HCCAPX_FILE))
            else:
                print'Only .cap or .hccapx files can be used'
                time.sleep(2)
                wireless_menu()
            os.system('clear')
            crack_menu()
        else:
            print' ' + 'Error:' + ' ' + WIRELESS_INPUT + ' ' + 'file not found'  + ' ' + 'try again or type' + '\033[31m' + ' ' + 'back' + ' ' + '\033[0m'
            time.sleep(2)
            os.system('clear')
            wireless_menu()
    except KeyError:
        os.system('clear')
        pass
    os.system('clear')
    crack_menu()

#Report and Stats Menu
def report_menu():
    global HM_ANSWER
    os.system('clear')
    banner()
    print'\033[33m' + ' ' + 'Reporting and Analysis Menu' + '\033[0m'
    prCyan(L00T_POT_DIR)
    print""
    print'\033[34m' + ' ' + 'Below are the stats files created from sucessfully compromised passwords... (Hit Enter to Refresh) (TAB Completion On)' + '\033[0m'
    print''
    for root, dirs, files in os.walk(L00T_POT_DIR):
        files.sort()
        for f in files:
            if f.endswith('.pot'):
                print' \t' + os.path.join(f)
    print''
    print'\033[33m' + ' ' + 'Select the filename from the above list to be analysed, or type ' + '\033[0m' + '\033[31m' + '"back"' + '\033[0m'
    os.chdir(L00T_POT_DIR)
    readline.parse_and_bind("tab: complete")
    STAT_INPUT = raw_input(str("------> "))
    if STAT_INPUT == ('back') or STAT_INPUT == ('Back') or STAT_INPUT == ('BACK'):
        main_menu()
    else:
        os.system('clear')
        print'\033[33m' + ' ' + 'Reporting and Analysis Menu' + '\033[0m'
        print''
    banner()
    #Step 1 - Confirm the hash type
    hash_mode_menu()
    #Step 2 - Strip out just the password for the pot file
    if HM_ANSWER == "0" or HM_ANSWER == "3" or HM_ANSWER == "4" or HM_ANSWER == "7": #Used for hash:password formatting
        subprocess.call('cut -d' + ' ":" ' + '-f 2 ' + os.path.join(L00T_POT_DIR, STAT_INPUT) + ' > ' + os.path.join(L00T_POT_DIR, STAT_INPUT + '.format1 '), shell=True)
    elif HM_ANSWER == "1" or HM_ANSWER == "2": #Used for Net-NTLMv1/2 formatting
        subprocess.call('cut -d' + ' ":" ' + '-f 7 ' + os.path.join(L00T_POT_DIR, STAT_INPUT) + ' > ' + os.path.join(L00T_POT_DIR, STAT_INPUT + '.format1 '), shell=True)
    #Step 3 - Execute Stats on cut file
    subprocess.call(os.path.join(TOOLS_DIR, 'statsgen') + ' ' + '-q' + ' ' + os.path.join(L00T_POT_DIR, STAT_INPUT + '.format1') + ' | less', shell=True)
    subprocess.call(os.path.join(TOOLS_DIR, 'statsgen') + ' ' + '-q' + ' ' + os.path.join(L00T_POT_DIR, STAT_INPUT + '.format1') + ' ' + '>' + ' ' + os.path.join(STATS_DIR, STAT_INPUT) + '.stats', shell=True)
    #Step 4 - Remove the unnecessasry file as we don't need it anymore.
    subprocess.call('rm' + ' ' + os.path.join(L00T_POT_DIR, STAT_INPUT + '.format1'), shell=True)
    #(WORKS)subprocess.call(os.path.join(TOOLS_DIR, 'statsgen') + ' ' + '-q' + ' ' + os.path.join(L00T_POT_DIR, STAT_INPUT) + ' ' + '-o' + ' ' + os.path.join(STATS_DIR, STAT_INPUT) + '.stats | less', shell=True)
    os.system('clear')    
    print('Report Complete - Returning to Main Menu')
    time.sleep(2)
    main_menu()

#l00t Menu - Full dump as a bash output with standard in from 'less'                                               
def hash_menu_full():
    os.system('clear')
    banner()
    print'\033[33m' + ' ' + 'Hash Upload Menu' + '\033[0m'
    prCyan(HASH_UPLOAD_DIR)
    print""
    print'\033[34m' + ' ' + 'Below are the stats files created from sucessfully compromised passwords... (Hit Enter to Refresh) (TAB Completion On)' + '\033[0m'
    print''
    for root, dirs, files in os.walk(HASH_UPLOAD_DIR):
        files.sort()
        for f in files:
            if not f.endswith('~'):
                print' \t' + os.path.join(f)
    print''
    print'\033[33m' + ' ' + 'Select the filename from the above list to be analysed, or type' + '\033[0m' + '\033[31m' + ' "back" ' + '\033[0m'
    os.chdir(HASH_UPLOAD_DIR)
    readline.parse_and_bind("tab: complete")
    HASH_INPUT = raw_input(str("------> "))
    if HASH_INPUT == ('back') or HASH_INPUT == ('Back') or HASH_INPUT == ('BACK'):
        main_menu()
    try:
        if os.path.isfile(HASH_INPUT):
            os.system('clear')
            print'\033[33m' + ' ' + 'L00T Information' + '\033[0m'
            print''
            print''
            subprocess.call('less ' + HASH_INPUT, shell=True)
            HASH_FILE = open(HASH_INPUT, "r")
            HASH_CONTENTS = HASH_FILE.read()
            print(HASH_CONTENTS)
            HASH_FILE.close()
            print''
            raw_input('\033[33m' + ' ' + 'Press any key to return to the main menu (Scroll Up for previous results)\n' + '\033[0m')
            main_menu()
        else:
            print' ' + 'Error:' + ' ' + HASH_INPUT + ' ' + 'file not found'
            time.sleep(1)
            os.system('clear')
            hash_menu_full()
    except KeyError:
        os.system('clear')
        pass
    return
    
#l00t Menu - Full dump as a bash output with standard in from 'less'
def l00t_menu_full(): #Menu 5
    os.system('clear')
    banner()
    print'\033[33m' + ' ' + 'Reporting and Analysis Menu' + '\033[0m'
    prCyan(L00T_POT_DIR)
    print""
    print'\033[34m' + ' ' + 'Below are the stats files created from sucessfully compromised passwords... (Hit Enter to Refresh) (TAB Completion On)' + '\033[0m'
    print''
    for root, dirs, files in os.walk(L00T_POT_DIR):
        files.sort()
        for f in files:
            if f.endswith('.pot') or f.endswith('.pot.sorted'):
                print' \t' + os.path.join(f)
            else:
                pass
    print''
    print'\033[33m' + ' ' + 'Select the filename from the above list to be analysed, or type' + '\033[0m' + '\033[31m' + ' "back" ' + '\033[0m'
    os.chdir(L00T_POT_DIR)
    readline.parse_and_bind("tab: complete")
    L00T_INPUT = raw_input(str("------> "))
    if L00T_INPUT == ('back') or L00T_INPUT == ('Back') or L00T_INPUT == ('BACK'):
        main_menu()
    else:
        pass
    try:
        if os.path.isfile(L00T_INPUT):
            os.system('clear')
            print'\033[33m' + ' ' + 'L00T Information' + '\033[0m'
            print''
            wc = os.popen('wc -l ' + str(L00T_INPUT)).read()
            wc = str(wc).split(' ')[0]
            print' ' + '\033[34m' + 'Total Number of Passwords Found = ' + '\033[0m' + wc
            print''
            L00T_FILE = open(L00T_INPUT, "r")
            L00T_CONTENTS = L00T_FILE.read()
            print(L00T_CONTENTS)
            L00T_FILE.close()
            print''
            raw_input('\033[33m' + ' ' + 'Press any key to return to the main menu (Scroll Up for previous results)\n' + '\033[0m')
            main_menu()
        else:
            print' ' + 'Error:' + ' ' + L00T_INPUT + ' ' + 'file not found'
            time.sleep(1)
            os.system('clear')
            l00t_menu_full()
    except KeyError:
        os.system('clear')
        pass
    return

#l00t Menu - Simple menu that displays key info from current l00t found
def l00t_menu_key(): #Menu 6
    os.system('clear')
    banner()
    print'\033[33m' + ' ' + 'Reporting and Analysis Menu' + '\033[0m'
    prCyan(L00T_POT_DIR)
    print""
    print'\033[34m' + ' ' + 'Below are the stats files created from sucessfully compromised passwords... (Hit Enter to Refresh) (TAB Completion On)' + '\033[0m'
    print''
    for root, dirs, files in os.walk(L00T_POT_DIR):
        files.sort()
        for f in files:
            if f.endswith('.pot') or f.endswith('.pot.sorted'):
                print' \t' + os.path.join(f)
    print''
    print'\033[33m' + ' ' + 'Select the filename from the above list to be analysed, or type ' + '\033[0m' + '\033[31m' + '"back"' + '\033[0m'
    os.chdir(L00T_POT_DIR)
    readline.parse_and_bind("tab: complete")
    L00T_INPUT = raw_input(str("------> "))
    if L00T_INPUT == ('back') or L00T_INPUT == ('Back') or L00T_INPUT == ('BACK'):
        main_menu()
    try:
        if os.path.isfile(L00T_INPUT):
            os.system('clear')
            hash_mode_menu()
            os.system('clear')
            print'\033[33m' + ' ' + 'Key Compromised L00T Information' + '\033[0m'
            print''
            if HASH_TYPE == '1000': #NTLM
                print'  ' + '\033[33m' + 'Domain\Username' + '\033[0m' + '\t\t\t' + '\033[34m' + 'NTLM (NTHASH)' + '\033[0m' + '\033[31m' + '\t\t\t\t\t' 'Password' + '\033[0m'
                with open(L00T_INPUT, "r") as hashes:
                    hash_read = csv.reader(hashes, delimiter=':')
                    for hash_column in hash_read:
                        print'  ' + '\033[33m' + hash_column[0] + '\033[0m' + '\t\t' + '\033[34m' + hash_column[1] + '\033[0m' + '\t\t\t' + '\033[31m' + hash_column[2] + '\033[0m'
            elif HASH_TYPE == '5500' or HASH_TYPE == '5600': #Net-NTLMv1/v2
                print'  ' + '\033[33m' + 'Domain' + '\033[0m' + '\t\t' + '\033[34m' + 'Username' + '\033[0m' + '\033[31m' + '\t\t\t' 'Password' + '\033[0m'
                with open(L00T_INPUT, "r") as hashes:
                    hash_read = csv.reader(hashes, delimiter=':')
                    for hash_column in hash_read:
                        print'  ' + '\033[33m' + hash_column[2] + '\033[0m' + '\t\t' + '\033[34m' + hash_column[0] + '\033[0m' + '\t\t\t' + '\033[31m' + hash_column[6] + '\033[0m'
            elif HASH_TYPE == '0' or HASH_TYPE == '1800': #UNIX MD5 / SHA512
                print'  ' + '\033[33m' + 'Hash' + '\033[0m' + '\t\t\t\t\t\t' + '\033[34m' + 'Password' + '\033[0m'
                with open(L00T_INPUT, "r") as hashes:
                    hash_read = csv.reader(hashes, delimiter=':')
                    for hash_column in hash_read:
                        print'  ' + '\033[33m' + hash_column[0] + '\033[0m' + '\t\t' + '\033[34m' + hash_column[1] + '\033[0m'
                        print''
            raw_input('\033[33m' + ' ' + 'Press any key to return to the main menu (Scroll Up for previous results)\n' + '\033[0m')
            main_menu()
        else:
            print' ' + 'Error:' + ' ' + L00T_INPUT + ' ' + 'file not found'
            time.sleep(1)
            os.system('clear')
            l00t_menu_full()
    except KeyError:
        os.system('clear')
        pass
    return

#Hash Upload Menu - Full dump of the hashes uploaded for convenience - as a bash output with standard in from 'less'
def hash_menu_full(): #Menu 7                                                                                                                 
    os.system('clear')
    banner()
    print'\033[33m' + ' ' + 'Reporting and Analysis Menu' + '\033[0m'
    prCyan(HASH_UPLOAD_DIR)
    print''
    print'\033[34m' + ' ' + 'Below are the hash files in the hash upload directory.. (Hit Enter to Refresh) (TAB Completion On)' + '\033[0m'
    print''
    for root, dirs, files in os.walk(HASH_UPLOAD_DIR):
        files.sort()
        for f in files:
            if not f.endswith('~'):
                print' \t' + os.path.join(f)
    print''
    print'\033[33m' + ' ' + 'Select the filename from the above list to be analysed, or type ' + '\033[0m' + '\033[31m' + '"back"' + '\033[0m'
    os.chdir(HASH_UPLOAD_DIR)
    readline.parse_and_bind("tab: complete")
    HASH_INPUT = raw_input(str("------> "))
    if HASH_INPUT == ('back') or HASH_INPUT == ('Back') or HASH_INPUT == ('BACK'):
        main_menu()
    try:
        if os.path.isfile(HASH_INPUT):
            os.system('clear')
            print'\033[33m' + ' ' + 'Hash Information' + '\033[0m'
            print''
            print''
            wc = os.popen('wc -l ' + str(HASH_INPUT)).read()
            wc = str(wc).split(' ')[0]
            print' ' + '\033[34m' + 'Total Number of Passwords Found = ' + '\033[0m' + wc
            print''
            HASH_FILE = open(HASH_INPUT, "r")
            HASH_CONTENTS = HASH_FILE.read()
            print(HASH_CONTENTS)
            HASH_FILE.close()
            print''
            #subprocess.call('cat ' + HASH_INPUT + ' | sort -u | less', shell=True)
            print''
            raw_input('\033[33m' + ' ' + 'Press any key to return to the main menu (Scroll Up for previous results)\n' + '\033[0m')
            main_menu()
        else:
            print' ' + 'Error:' + ' ' + HASH_INPUT + ' ' + 'file not found'
            time.sleep(1)
            os.system('clear')
            HASH_menu_full()
    except KeyError:
        os.system('clear')
        pass
    return

#Exit system
def program_exit():
    sys.exit()

#MainMenu
def main_menu():
    global USER_ONLY_BOOLEAN
    try:
        while 1:
            banner()
            prCyan("\t(0) Input OS - Singluar Hash - (MD5, NTLM, NetNTLMv1/2, Kerberos)")
            prLightPurple("\t(1) Input OS - Hashes From File - (MD5, NTLM, NetNTLMv1/2, Kerberos)")
            prCyan("\t(2) Input Hash Dump & filter out usernames - e.g. useful for NTDS.dit")
            prLightPurple("\t(3) Input Wireless - Capture From File - (WPA-EAPOL-PBKDF2) {*.cap, *.hccapx}")
            prCyan("\t(4) Run Statistical Analysis on l00t")
            prLightPurple("\t(5) Display l00t - Full Dump")
            prCyan("\t(6) Display l00t - Key Information Summary (BETA)")
            prLightPurple("\t(7) Display Hashes Uploaded - Full Dump")
            prRed("\t(x) Exit")
            options = {"0": single_hash_menu,
                       "1": hash_from_file,
                       "2": hash_from_file, #not a typo
                       "3": wireless_menu,
                       "4": report_menu,
                       "5": l00t_menu_full,
                       "6": l00t_menu_key,
                       "7": hash_menu_full,
                       "x": program_exit,
                      }
            try:
                task = raw_input("\n Choose an Option: ")
                if task == "2":
                    USER_ONLY_BOOLEAN = True
                options[task]()
            except KeyError:
                os.system('clear')
    except KeyboardInterrupt:
        sys.exit()

if __name__ == '__main__':
    main_menu()

