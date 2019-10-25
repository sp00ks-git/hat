#!/usr/bin/python2.7
'''
#Release Date - 14/10/2019
#Latest update - Pre-Release
#Last Modified - 14/10/2019
#Python Hashcat Automated Password Recovery
#Version 0.1
#Currenty working in python 2.7
#Update to python 3 (to do)
'''


#Module Imports
import datetime
import fnmatch
import os
import platform
import shlex
import subprocess
import sys
import time
from os import listdir
from os.path import isfile, join

#Define Colours
def prRed(prt): print("\033[91m {}\033[00m" .format(prt))
def prGreen(prt): print("\033[92m {}\033[00m" .format(prt))
def prYellow(prt): print("\033[93m {}\033[00m" .format(prt))
def prLightPurple(prt): print("\033[94m {}\033[00m" .format(prt))
def prPurple(prt): print("\033[95m {}\033[00m" .format(prt))
def prCyan(prt): print("\033[96m {}\033[00m" .format(prt))
def prLightGray(prt): print("\033[97m {}\033[00m" .format(prt))

'''
#More Colours Reference Table
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



#Python2/3 compatability
try:
    input = raw_input
except NameError:
    pass

all_menu = False

#Both Values are set to false on program start. This is used to trigger the pot file and hash upload functionality.
file_hash_boolean = False
single_hash_boolean = False

#Used to allow multiple tests via the menu with the same pot file already selected.
#Note Global pot_boolean resides inside the pot_function() function block. 
pot_boolean = False

#Used for supporting the cewl wordlists if standard wordlists are not getting results
cewl_boolean = False

#Initally Clear the Screen
os.system('clear')

#Hash Mode Boolean - Added so that you can run Cewl lists without neededing to run other tests firsts. Mainly for Selecting th hash type
hash_mode_boolean = False

#Awk command - awkward command that doesn't sit well when called idrectly.
awk = " awk '!x[$0]++' " 

#Declare Paths
#First make the hat absolute path dynamic and go up one level to accomodate each related path
hashcat_path = os.getcwd()
#Set the wordlist directory to where you're wordlists are...
wordlist_directory = "/opt/wordlists/"
l00t_pot_dir = os.path.join(hashcat_path, 'l00t')
rules_dir = os.path.join(hashcat_path, 'rules')
hash_upload_dir = os.path.join(hashcat_path, 'hash_upload')
cewl_upload_dir = os.path.join(hashcat_path, 'cewl_wordlists')
tools_dir = os.path.join(hashcat_path, 'tools')
rsmangler_upload_dir = os.path.join(hashcat_path, 'rsmangler')
rsmangler_input_dir = os.path.join(rsmangler_upload_dir, 'input')
rsmangler_output_dir = os.path.join(rsmangler_upload_dir, 'output')


#Banner
def banner():
    print("")
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
    prGreen(" @@@@@@@@@@@@@@&&                                                               ")
    prGreen("  %@@@@@@@@&                                                                    ")
    print("")
    

#Pot File - Create a New Potfile when using a Single wordlist or the File Upload Functionality.
def pot_function():
    global pot_absolute
    global pot_boolean
    global pot_file
    global pot_formatted
    global pot_path
    global pot_sorted
    global hash_path_and_name
    global single_hash_file_name
    global hash_abs_path
    global cewl_boolean
    global file_hash_boolean
    global hash_input
    global hm_answer
    if single_hash_boolean == True and pot_boolean == True: #Re-check the value of the hash file and pot name as these may of changed since the last run. Handy to change hashes without exiting the program.
        return
    elif cewl_boolean == True:
        pot = hash_input.lower()
        pot = pot + '.pot'
        hash_path_and_name = hash_abs_path
        pot_file = '--potfile-path=' + os.path.join(l00t_pot_dir, pot)
        pot_boolean = True
        return
    elif single_hash_boolean == True and pot_boolean == False:
        pot = single_hash_file_name.lower()
        pot = pot + '.pot' #No need to create a file here as hashcat will automajically make one and therefore we will have duplicates
        hash_path_and_name = os.path.join(os.getcwd(), single_hash_file_name)
        pot_file = '--potfile-path=' + os.path.join(l00t_pot_dir, pot)
        pot_boolean = True
        return
    elif file_hash_boolean == True and pot_boolean == False and hm_answer == "0": # NT HASH
        pot = hash_input.lower()
        pot = pot + '.pot'
        pot_format_extension = pot + '.format3 '
        pot_sorted = os.path.join(l00t_pot_dir, pot) + '.sorted '
        hash_path_and_name = hash_abs_path
        pot_file = '--potfile-path=' + os.path.join(l00t_pot_dir, pot)
        pot_absolute = os.path.join(l00t_pot_dir, pot)
        pot_formatted = os.path.join(l00t_pot_dir, pot_format_extension)
        pot_boolean = True
        return
    elif file_hash_boolean == True and pot_boolean == False and hm_answer == "1": # Net-NTLMv1 
        pot = hash_input.lower()                                              
        pot = pot + '.pot'                                                    
        pot_sorted = os.path.join(l00t_pot_dir, pot) + '.sorted '             
        hash_path_and_name = hash_abs_path                                    
        pot_file = ' ' + os.path.join(l00t_pot_dir, pot)
        pot_boolean = True
        return
    elif file_hash_boolean == True and pot_boolean == False and hm_answer == "2": # Net-NTLMv2
        pot = hash_input.lower()
        pot = pot + '.pot'
        pot_format_extension = pot + '.format3 '
        pot_sorted = os.path.join(l00t_pot_dir, pot) + '.sorted '
        hash_path_and_name = hash_abs_path
        pot_file = '--potfile-path=' + os.path.join(l00t_pot_dir, pot)
        pot_path = os.path.join(l00t_pot_dir, pot)
        pot_formatted = os.path.join(l00t_pot_dir, pot_format_extension)
        pot_boolean = True
        return
    elif file_hash_boolean == True and pot_boolean == False and hm_answer == "3": # MD5
        pot = hash_input.lower()
        pot = pot + '.pot'
        pot_format_extension = pot + '.format3 '
        pot_sorted = os.path.join(l00t_pot_dir, pot) + '.sorted '
        #hash_path_and_name = hash_abs_path
        pot_file = '--potfile-path=' + os.path.join(l00t_pot_dir, pot)
        pot_formatted = os.path.join(l00t_pot_dir, pot_format_extension)
        pot_boolean = True
        return
    elif file_hash_boolean == True and pot_boolean == False and hm_answer == "4": # SHA-512
        pot = hash_input.lower()
        pot = pot + '.pot'
        pot_format_extension = pot + '.format3 '
        pot_sorted = os.path.join(l00t_pot_dir, pot) + '.sorted '
        hash_path_and_name = hash_abs_path
        pot_file = '--potfile-path=' + os.path.join(l00t_pot_dir, pot)
        pot_formatted = os.path.join(l00t_pot_dir, pot_format_extension)
        pot_boolean = True
        return
    elif file_hash_boolean == True and pot_boolean == False and hm_answer == "5": # Kerberos
        pot = hash_input.lower()
        pot = pot + '.pot'
        pot_format_extension = pot + '.format3 '
        pot_sorted = os.path.join(l00t_pot_dir, pot) + '.sorted '
        hash_path_and_name = hash_abs_path
        pot_file = '--potfile-path=' + os.path.join(l00t_pot_dir, pot)
        pot_formatted = os.path.join(l00t_pot_dir, pot_format_extension)
        pot_boolean = True
        return
    elif file_hash_boolean == True and pot_boolean == True:
        return
    else:
        print(pot_name)
        pot = pot_name.lower()
        pot = pot + '.pot '
        hashcat_command_line_menu()

#Hashcat Command Line Menu
def hashcat_command_line_menu():
    global awk
    os.system('clear')
    awk = " awk '!x[$0]++' " # dont remove, parsing through zsh causes issues

#Hash Mode Selection Menu
def hash_mode_menu():
    hash_mode_boolean = True
    loop = True
    global hash_type
    global hm_answer
    while loop:
        print("Input Hash Mode To Crack")
        prCyan("\t(0) NTLM {AKA NTHASH} - A SAM Database Hash - NTDS.dit File Accessed from the Domain Controller file - {PTH Possible}")
        prGreen("\t\tNTLM Example - 49a9a1e1f0127c7d70d750349d0bc09a - Only the NTHASH is Needed - order (LM-NT)")
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
        hm_answer = input(": ")
        if hm_answer == "0":
            hash_type = '1000'
            return
        elif hm_answer == "1":
            hash_type = '5500'
            return
        elif hm_answer == "2":
            hash_type = '5600'
            return
        elif hm_answer == "3":
            hash_type = '0'
            return
        elif hm_answer == "4":
            hash_type = '1800'
            return
        elif hm_answer == "5":
            hash_type = '13100'
            return
        elif hm_answer == "6":
            crack_menu()
        else:
            input("You did not give a valid answer, press any key to try again \n")
            os.system('clear')
            print('')
            banner()

#Straight Wordlist_walk
def wordlist_walk():
    exten = ''
    for dirpath, dirnames, files in os.walk(wordlist_directory):
        for wordlist_filename in files:
            if wordlist_filename.endswith(exten):
                abs_wordlist = (os.path.join(dirpath, wordlist_filename))
                hc_cmd = ['hashcat', '-a', '0', '-m', hash_type, hash_abs_path, pot_file, abs_wordlist, '-w', '3', '-O']
                input(hc_cmd)
                subprocess.call(hc_cmd)
    wordlist_directory = '/opt/wordlists/'
    if hm_answer == '0' or hm_answer == '1' or hm_answer  == '2':
        subprocess.call(awk + pot_formatted + " | sort > " + pot_sorted, shell=True)
        os.system('clear')
    else:
        os.system('clear')
    #wordlist_directory = '/opt/wordlists/'
    #single_wordlist = '/opt/wordlists/'

#Rule Set Walk
def rule_set_walk():
    exten = '*.rule'
    for root, dirs, files in os.walk(rules_dir):
        for filename in fnmatch.filter(files, exten):
            abs_rule_set = (os.path.join(root, filename))
            hc_cmd = ['hashcat', '-a', '0', '-m', hash_type, hash_abs_path, '-w', '3', '-O', pot_file, single_wordlist, '-r', abs_rule_set]
            subprocess.call(hc_cmd)
            if hm_answer == '0' or hm_answer == '1' or hm_answer  == '2':
                subprocess.call(awk + pot_formatted + " | sort > " + pot_sorted, shell=True)
                os.system('clear')
            else:
                os.system('clear')
                
#Single Wordlist
def singular_wordlist():
    global hash_type
    if single_hash_boolean == True:
        hc = ['hashcat', '-a', '0', '-m', hash_type, hash_abs_path, pot_file, single_wordlist, '-w', '3', '-O']
        subprocess.call(hc)
        os.system('clear')
    elif cewl_boolean == True and hash_mode_boolean == True:
        hc = ['hashcat', '-a', '0', '-m', hash_type, hash_abs_path, pot_file, single_wordlist, '-w', '3', '-O']
        subprocess.call(hc)
    elif cewl_boolean == True and hash_mode_boolean == False:
        os.system('clear')
        banner()
        hc = ['hashcat', '-a', '0', '-m', hash_type, hash_abs_path, pot_file, single_wordlist, '-w', '3', '-O']
        subprocess.call(hc)
    else:
        hash_answer()
    wordlist_directory = '/opt/wordlists'
    os.system('clear')
    return

def hash_answer(): # Split out from single wordlist so that all rules and wordlists can use this function block
    #global wordlist_directory
    wordlist_directory = '/opt/wordlists/'
    input(wordlist_directory)
    input('hm_answer ' + ' = ' + hm_answer)
    if hm_answer == "0": # NTHASH
        hc_cmd1 = ['hashcat', '-a', '0', '-m', hash_type, hash_abs_path, pot_file, single_wordlist, '-w 3', '-O']
        subprocess.call(hc_cmd1)
        hc_cmd2 = ['hashcat', '-m', hash_type, '-a', '0', '--username', '--session', 'all', pot_file, '--show', '-o', pot_formatted, '--outfile-format', '3', hash_abs_path]
        subprocess.call(hc_cmd2)
    elif hm_answer == "1": # Net-NTLMv1
        hc_cmd1 = ['hashcat', '-a', '0', '-m', hash_type, hash_abs_path, pot_file, single_wordlist, '-w', '3', '-O']
        subprocess.call(hc_cmd1)
        hc_cmd2 = ['hashcat', hash_type, '-a', '0', '--username', '--session', 'all', pot_file, '--show', '-o', pot_formatted, '--outfile-format', '3', hash_path_and_name]
        subprocess.call(hc_cmd2)
        subprocess.call(awk + pot_formatted + " | sort > " + pot_sorted, shell=True)
    elif hm_answer == "2": # Net-NTLMv2
        hc_cmd1 = ['hashcat', '-a', '0', '-m', hash_type, hash_abs_path, pot_file, single_wordlist,'-w', '3', '-O']
        subprocess.call(hc_cmd1)
        hc_cmd2 = ['hashcat', '-m', hash_type, '--show', '-o', pot_formatted, '--outfile-format', '3', hash_abs_path, pot_file, '--session', 'all']
        subprocess.call(hc_cmd2)
        subprocess.call(awk + pot_formatted + " | sort > " + pot_sorted, shell=True)
    elif hm_answer == "3": # MD5
        hc_cmd = ['hashcat', '-a', '0', '-m', hash_type, hash_abs_path, pot_file, os.path.join(wordlist_directory, '4GB+/crackstation.txt'), '-w', '3', '-O']
        input(hc_cmd)
        subprocess.call(hc_cmd)
    elif hm_answer == "4": # SHA-512
        hc_cmd = ['hashcat', '-a', '0', '-m', hash_type, hash_abs_path, pot_file, single_wordlist, '-w', '3', '-O']
        subprocess.call(hc_cmd)
    elif hm_answer == "5": # Kerberos
        hc_cmd = ['hashcat', '-a', '0', '-m', hash_type, hash_abs_path, pot_file, single_wordlist,'-w', '3', '-O']
        subprocess.call(hc_cmd)
    else:
        input('return')
        return
    input('return1')
    os.system('clear')
    return

#File Unique menu - used to remove any duplicate entries in files - also helps to keep down the .format3 file
def file_unique_menu():
    lines_seen = set() # holds lines already seen
    outfile = open("out.txt", "w")
    for line in open("input.txt", "r"):
        if line not in lines_seen: # if not a duplicate
            outfile.write(line)
            lines_seen.add(line)
            outfile.close()

'''
#Hashcat with Rule Sets
def singular_wordlist_rule_set():
    global hash_type
    hash_answer()
    hc = [os.popen('which hashcat').read().strip(), '-a', '0', '-m', hash_type, hash_abs_path, pot_file, single_wordlist, '-r', rule_set_directory, '-w', '3', '-O']
    subprocess.call(hc)
    if hm_answer == '0' or hm_answer == '1' or hm_answer  == '2':
        subprocess.call(awk + pot_formatted + " | sort > " + pot_sorted, shell=True)
        os.system('clear')
    else:
        os.system('clear')
'''

#Rsmangler Rule Set - {5 ANY Characters RIGHT --> LEFT incremental}
def rsmangler_rule_set():
    global rule_set_directory
    rule_set_directory = os.path.join(rules_dir, 'OneRuleToRuleThemAll.rule')
    hash_answer()
    hc = ['hashcat', '-a', '0', '-m', hash_type, hash_abs_path, pot_file, single_wordlist, '-r', rule_set_directory, '-w', '3', '-O']
    subprocess.call(hc)
    #Right Side
    hc1 = ['hashcat', attack_mode_inc_right, hash_type, hash_path_and_name, pot_file, single_wordlist, '?a?a?a?a', '-w', '3', '-O', '--increment']
    subprocess.call(hc1)
    if hm_answer == '0' or hm_answer == '1' or hm_answer  == '2':
        subprocess.call(awk + pot_formatted + " | sort > " + pot_sorted, shell=True)
        os.system('clear')
    else:
        os.system('clear')
    #LeftSide
    hc2 = ['hashcat', attack_mode_inc_left, '-m', hash_type, hash_abs_path, pot_file, '?a?a?a?a', single_wordlist, '-w', '3', '-O', '--increment']
    subprocess.call(hc2)
    if hm_answer == '0' or hm_answer == '1' or hm_answer  == '2':
        subprocess.call(awk + pot_formatted + " | sort > " + pot_sorted, shell=True)
        os.system('clear')
    else:
        os.system('clear')

#Crack Menu 0 - Try all words lists merged List -  Common Credentials
#Updated and merged all smaller wordlists into one file for more effcient testing (find . -name "*.txt" | xarg cat >> ./mergedfile.txt)
def crack_menu_0():
    global default_cewl_file_output
    global cewl_boolean
    global file_hash_boolean
    global pot_boolean
    global single_wordlist
    #wordlist_directory = '/opt/wordlists'
    input('crack_menu_0() ' + wordlist_directory)
    if cewl_boolean == True and file_hash_boolean == True:
        single_wordlist = default_cewl_file_output
    elif single_hash_boolean == True and cewl_boolean == True:
        single_wordlist = default_cewl_file_output
    else:
        single_wordlist = os.path.join(wordlist_directory, 'merged_list/sp00ks_merged_file_uniq.txt')
        input('stop 1 ' + single_wordlist)
    if all_menu == True:
        pot_function()
        hashcat_command_line_menu()
    else:
        hash_mode_menu()    
        pot_function()
        hashcat_command_line_menu()
    if single_hash_boolean == True:
        hc = ['hashcat', '-a', '0', '-m', hash_type, hash_abs_path, pot_file, single_wordlist, '-w', '3', '-O']
        subprocess.call(hc)
        os.system('clear')
    elif cewl_boolean == True and hash_mode_boolean == True:
        hc = ['hashcat', '-a', '0', '-m', hash_type, hash_abs_path, pot_file, single_wordlist, '-w', '3', '-O']
        subprocess.call(hc)
    elif cewl_boolean == True and hash_mode_boolean == False:
        os.system('clear')
        banner()
        hc = ['hashcat', '-a', '0', '-m', hash_type, hash_abs_path, pot_file, single_wordlist, '-w', '3', '-O']
        subprocess.call(hc)
    else:
        input('pre hash_answer()')
        hash_answer()
        os.system('clear')

    
#Crack Menu 1 - Try all words lists between 1GB < 4GB                  
def crack_menu_1():
    global wordlist_directory
    wordlist_directory = '/opt/wordlists'
    wordlist_directory = os.path.join(wordlist_directory, '1GB-4GB')
    if all_menu == True:
        pot_function()
        hashcat_command_line_menu()
        wordlist_walk()
        os.system('clear')
        return
    else:
        hash_mode_menu()
        pot_function()
        hashcat_command_line_menu()
        wordlist_walk()
        os.system('clear')
        return

#Crack Menu 2 - Try crackstation list (15GB)
def crack_menu_2():
    single_wordlist = os.path.join(wordlist_directory, '4GB+/crackstation.txt')
    if all_menu == True:
        pot_function()
        hashcat_command_line_menu()
    else:
        hash_mode_menu()
        pot_function()
        hashcat_command_line_menu()
    if single_hash_boolean == True:
        hc = ['hashcat', '-a', '0', '-m', hash_type, hash_abs_path, pot_file, os.path.join(wordlist_directory, '4GB+/crackstation.txt'), '-w', '3', '-O']
        subprocess.call(hc)
        os.system('clear')
    elif cewl_boolean == True and hash_mode_boolean == True:
        hc = ['hashcat', '-a', '0', '-m', hash_type, hash_abs_path, pot_file, os.path.join(wordlist_directory, '4GB+/crackstation.txt'), '-w', '3', '-O']
        subprocess.call(hc)
    elif cewl_boolean == True and hash_mode_boolean == False:
        os.system('clear')
        banner()
        hc = ['hashcat', '-a', '0', '-m', hash_type, hash_abs_path, pot_file, os.path.join(wordlist_directory, '4GB+/crackstation.txt'), '-w', '3', '-O']
        subprocess.call(hc)
    else:
        hash_answer()
        os.system('clear')




#Crack_Menu 3
def crack_menu_3():
    single_wordlist = os.path.join(wordlist_directory, '4GB+/weakpass_2p')
    if all_menu == True:
        pot_function()
        hashcat_command_line_menu()
    else:
        hash_mode_menu()
        pot_function()
        hashcat_command_line_menu()
    if single_hash_boolean == True:
        hc = ['hashcat', '-a', '0', '-m', hash_type, hash_abs_path, pot_file, single_wordlist, '-w', '3', '-O']
        subprocess.call(hc)
        os.system('clear')
    elif cewl_boolean == True and hash_mode_boolean == True:
        hc = ['hashcat', '-a', '0', '-m', hash_type, hash_abs_path, pot_file, single_wordlist, '-w', '3', '-O']
        subprocess.call(hc)
    elif cewl_boolean == True and hash_mode_boolean == False:
        os.system('clear')
        banner()
        hc = ['hashcat', '-a', '0', '-m', hash_type, hash_abs_path, pot_file, single_wordlist, '-w', '3', '-O']
        subprocess.call(hc)
    else:
        hash_answer()
    os.system('clear')



    

#Crack Menu 4 - Try all words lists 4GB+ - (will take a while to cache each wordlist prior to testing)
def crack_menu_4():
    global wordlist_directory
    wordlist_directory = os.path.join(wordlist_directory, '4GB+')
    if all_menu == True:
        pot_function()
        hashcat_command_line_menu()
        wordlist_walk()
        os.system('clear')
        return
    else:
        hash_mode_menu()
        pot_function()
        hashcat_command_line_menu()
        wordlist_walk()
        os.system('clear')
        return

#Crack Menu 5 - Oxford Dic, capital letter, upto 4 characters, incrementally - RIGHT SIDE 
def crack_menu_5():
    single_wordlist = os.path.join(wordlist_directory, 'english-words/words.txt')
    if all_menu == True:
        pot_function()
        hashcat_command_line_menu()
        os.system('clear')
    else:
        hash_mode_menu()
        pot_function()
        hashcat_command_line_menu()
        os.system('clear')
    hc = ['hashcat', '-a', '6', '-m', hash_type, hash_abs_path, pot_file, single_wordlist, '?a?a?a?a', '-w', '3', '-O', '--increment']
    subprocess.call(hc)
    if hm_answer == '0' or hm_answer == '1' or hm_answer  == '2':
        subprocess.call(awk + pot_formatted + " | sort > " + pot_sorted, shell=True)
        os.system('clear')
    else:
        os.system('clear')
    os.system('clear')
    return

#Crack Menu 6 - Oxford Dic, capital letter, upto 4 characters, incrementally - LEFT SIDE           
def crack_menu_6():
    single_wordlist = os.path.join(wordlist_directory, 'english-words/words_first_letter_upper.txt')
    if all_menu == True:
        pot_function()
        hashcat_command_line_menu()
        os.system('clear')
    else:
        hash_mode_menu()
        pot_function()
        hashcat_command_line_menu()
        os.system('clear')
    hc = ['hashcat', '-a', '7', '-m', hash_type, hash_abs_path, pot_file, '?a?a?a?a', single_wordlist, '-w', '3', '-O', '--increment']
    subprocess.call(hc)
    if hm_answer == '0' or hm_answer == '1' or hm_answer  == '2':
        subprocess.call(awk + pot_formatted + " | sort > " + pot_sorted, shell=True)
        os.system('clear')
    else:
        os.system('clear')
    os.system('clear')
    return

#Crack Menu 7 - Try Oxford Dictionary Starting with UPPER Case + {upto 4 Numbers LEFT SIDE, upto 4 numbers RIGHT SIDE}
def crack_menu_7():
    single_wordlist = os.path.join(wordlist_directory, 'english-words/words_first_letter_upper.txt')
    if all_menu == True:
        pot_function()
        hashcat_command_line_menu()
        os.system('clear')
    else:
        hash_mode_menu()
        pot_function()
        hashcat_command_line_menu()
        os.system('clear')
    #Four Numbers (Left Side)
    hc1 = ['hashcat', '-a', '7', '-m', hash_type, hash_abs_path, pot_file, '?d?d?d?d', single_wordlist, '-w', '3', '-O', '--increment']
    subprocess.call(hc1)
    if hm_answer == '0' or hm_answer == '1' or hm_answer  == '2':
        subprocess.call(awk + pot_formatted + " | sort > " + pot_sorted, shell=True)
        os.system('clear')
    else:
        os.system('clear')                                                                                                                                             
    #Four Numbers (Right Side)
    hc2 = ['hashcat', '-a', '6', '-m', hash_type, hash_abs_path, pot_file, single_wordlist, '?d?d?d?d', '-w', '3', '-O', '--increment']
    subprocess.call(hc2)
    if hm_answer == '0' or hm_answer == '1' or hm_answer  == '2':
        subprocess.call(awk + pot_formatted + " | sort > " + pot_sorted, shell=True)
        os.system('clear')
    else:
        os.system('clear')
    os.system('clear')                       
    return

#Crack Menu 8 - Automated Testing - Oxford Dictionary MIXED CASE + upto 3 ANY Characters on RIGHT SIDE - {Corporate Scan}
def crack_menu_8():
    single_wordlist = os.path.join(wordlist_directory, 'english-words/words.txt')
    if all_menu == True:
        pot_function()
        hashcat_command_line_menu()
        os.system('clear')
    else:
        hash_mode_menu()
        pot_function()
        hashcat_command_line_menu()
        os.system('clear')
    hc = ['hashcat', '-a', '6', '-m', hash_type, hash_abs_path, pot_file, single_wordlist, '?a?a?a?a', '-w', '3', '-O', '--increment']
    subprocess.call(hc)
    if hm_answer == '0' or hm_answer == '1' or hm_answer  == '2':
        subprocess.call(awk + pot_formatted + " | sort > " + pot_sorted, shell=True)
        os.system('clear')
    else:
        os.system('clear')
    os.system('clear')
    return

#Crack Menu 9 - Rockyou with rule - d3ad0ne                                                        
def crack_menu_9():
    #global single_wordlist
    global single_hash_boolean
    global file_hash_boolean
    global rule_set_directory
    if single_hash_boolean == True and cewl_boolean == False:
        single_wordlist = os.path.join(wordlist_directory, 'rockyou.txt')
    elif single_hash_boolean == True and cewl_boolean == True:
        single_wordlist = default_cewl_file_output
    elif file_hash_boolean == True and cewl_boolean == False:
        single_wordlist = os.path.join(wordlist_directory, 'rockyou.txt')
    elif file_hash_boolean == True and cewl_boolean == True:
        single_wordlist = default_cewl_file_output
    rule_set_directory = os.path.join(rules_dir, 'd3ad0ne.rule')
    if all_menu == True:
        pot_function()
        hashcat_command_line_menu()
        os.system('clear')
    else:
        hash_mode_menu()
        pot_function()
        hashcat_command_line_menu()
        os.system('clear')
    hash_answer()
    hc = ['hashcat', '-a', '0', '-m', hash_type, hash_abs_path, pot_file, single_wordlist, '-r', rule_set_directory, '-w', '3', '-O']
    subprocess.call(hc)
    os.system('clear')
    return

#Crack Menu 10 - Rockyou with rule - OneRuleToRuleThemAll
def crack_menu_10():
    #global single_wordlist
    global single_hash_boolean
    global file_hash_boolean
    global rule_set_directory
    if single_hash_boolean == True and cewl_boolean == False:
        single_wordlist = os.path.join(wordlist_directory, 'rockyou.txt')
    elif single_hash_boolean == True and cewl_boolean == True:
        single_wordlist = default_cewl_file_output
    elif file_hash_boolean == True and cewl_boolean == False:
        single_wordlist = os.path.join(wordlist_directory, 'rockyou.txt')
    elif file_hash_boolean == True and cewl_boolean == True:
        single_wordlist = default_cewl_file_output
    rule_set_directory = os.path.join(rules_dir, 'OneRuleToRuleThemAll.rule')
    if all_menu == True:
        pot_function()
        hashcat_command_line_menu()
        os.system('clear')
    else:
        hash_mode_menu()
        pot_function()
        hashcat_command_line_menu()
        os.system('clear')
    #singular_wordlist_rule_set()
    hash_answer()
    hc = ['hashcat', '-a', '0', '-m', hash_type, hash_abs_path, pot_file, single_wordlist, '-r', rule_set_directory, '-w', '3', '-O']
    subprocess.call(hc)
    os.system('clear')
    return

#Crack Menu 11 - Rockyou with rule - # Changed to add leet speak rules
def crack_menu_11():
    global default_cewl_file_output
    global hash_abs_path
    if single_hash_boolean == True and cewl_boolean == False:
        single_wordlist = os.path.join(wordlist_directory, 'rockyou.txt')
    elif single_hash_boolean == True and cewl_boolean == True:
        single_wordlist = default_cewl_file_output
    elif file_hash_boolean == True and cewl_boolean == False:
        single_wordlist = os.path.join(wordlist_directory, 'rockyou.txt')
    elif file_hash_boolean == True and cewl_boolean == True:
        single_wordlist = default_cewl_file_output
    if all_menu == True:
        pot_function()
        hashcat_command_line_menu()
        os.system('clear')
    else:
        hash_mode_menu()
        pot_function()
        hashcat_command_line_menu()
        os.system('clear')
    hash_answer()
    hc1 = ['hashcat', '-a', '0', '-m', hash_type, hash_abs_path, pot_file, single_wordlist, '-r', os.path.join(rules_dir, 'leetspeak.rule'), '-w', '3', '-O']
    subprocess.call(hc1)
    hc2 = ['hashcat', '-a', '0', '-m', hash_type, hash_abs_path, pot_file, single_wordlist, '-r', os.path.join(rules_dir, 'unix-ninja-leetspeak.rule'), '-w', '3', '-O']
    subprocess.call(hc2)
    if hm_answer == '0' or hm_answer == '1' or hm_answer  == '2':
        subprocess.call(awk + pot_formatted + " | sort > " + pot_sorted, shell=True)
    else:
        os.system('clear')
    os.system('clear')
    return

#Crack Menu 12 - Rockyou with rule - oscommerce
def crack_menu_12():
    global single_hash_boolean
    global file_hash_boolean
    global rule_set_directory
    if single_hash_boolean == True and cewl_boolean == False:
        single_wordlist = os.path.join(wordlist_directory, 'rockyou.txt')
    elif single_hash_boolean == True and cewl_boolean == True:
        single_wordlist = default_cewl_file_output
    elif file_hash_boolean == True and cewl_boolean == False:
        single_wordlist = os.path.join(wordlist_directory, 'rockyou.txt')
    elif file_hash_boolean == True and cewl_boolean == True:
        single_wordlist = default_cewl_file_output
    rule_set_directory = os.path.join(rules_dir, 'oscommerce.rule')
    if all_menu == True:
        pot_function()
        hashcat_command_line_menu()
        os.system('clear')
    else:
        hash_mode_menu()
        pot_function()
        hashcat_command_line_menu()
        os.system('clear')
    hash_answer()
    hc = ['hashcat', '-a', '0', '-m', hash_type, hash_abs_path, pot_file, single_wordlist, '-r', rule_set_directory, '-w', '3', '-O']
    subprocess.call(hc)
    os.system('clear')
    return

#Crack Menu 13 - Rockyou with rule - rockyou-30000
def crack_menu_13():
    #global single_wordlist
    global single_hash_boolean
    global file_hash_boolean
    global rule_set_directory
    if single_hash_boolean == True and cewl_boolean == False:
        single_wordlist = os.path.join(wordlist_directory, 'rockyou.txt')
    elif single_hash_boolean == True and cewl_boolean == True:
        single_wordlist = default_cewl_file_output
    elif file_hash_boolean == True and cewl_boolean == False:
        single_wordlist = os.path.join(wordlist_directory, 'rockyou.txt')
    elif file_hash_boolean == True and cewl_boolean == True:
        single_wordlist = default_cewl_file_output
    rule_set_directory = os.path.join(rules_dir, 'rockyou-30000.rule')
    if all_menu == True:
        pot_function()
        hashcat_command_line_menu()
        os.system('clear')
    else:
        hash_mode_menu()
        pot_function()
        hashcat_command_line_menu()
        os.system('clear')
    hash_answer()
    hc = ['hashcat', '-a', '0', '-m', hash_type, hash_abs_path, pot_file, single_wordlist, '-r', rule_set_directory, '-w', '3', '-O']
    subprocess.call(hc)
    os.system('clear')
    return

#Crack Menu 14 - Rockyou with Hob0Rules -> Quick Test {hob064.rule} -> Comprenensive Test {d3adhob0.rule}
def crack_menu_14():
    #global single_wordlist
    global single_hash_boolean
    global file_hash_boolean
    global rule_set_directory
    if single_hash_boolean == True and cewl_boolean == False:
        single_wordlist = os.path.join(wordlist_directory, 'rockyou.txt')
    elif single_hash_boolean == True and cewl_boolean == True:
        single_wordlist = default_cewl_file_output
    elif file_hash_boolean == True and cewl_boolean == False:
        single_wordlist = os.path.join(wordlist_directory, 'rockyou.txt')
    elif file_hash_boolean == True and cewl_boolean == True:
        single_wordlist = default_cewl_file_output
    if all_menu == True:
        pot_function()
        hashcat_command_line_menu()
        os.system('clear')
    else:
        hash_mode_menu()
        pot_function()
        hashcat_command_line_menu()
        os.system('clear')
    hc1 = ['hashcat', '-a', '0', '-m', hash_type, hash_abs_path, pot_file, single_wordlist, '-r', os.path.join(rules_dir, 'hob064.rule'), '-w', '3', '-O']
    subprocess.call(hc1)
    if hm_answer == '0' or hm_answer == '1' or hm_answer  == '2':
        subprocess.call(awk + pot_formatted + " | sort > " + pot_sorted, shell=True)
        os.system('clear')
    else:
        os.system('clear')
    hc2 = ['hashcat', '-a', '0', '-m', hash_type, hash_abs_path, pot_file, single_wordlist, '-r', os.path.join(rules_dir, 'd3adhob0.rule'), '-w', '3', '-O']
    subprocess.call(hc2)
    if hm_answer == '0' or hm_answer == '1' or hm_answer  == '2':
        subprocess.call(awk + pot_formatted + " | sort > " + pot_sorted, shell=True)
        os.system('clear')
    else:
        os.system('clear')
    return

#Crack Menu 15 - Auto Multi Rule Test - Iterate through each rule with rockyou.txt - {Corporate Scan}
def crack_menu_15():
    global single_wordlist
    global default_cewl_file_output
    global hash_abs_path
    global rule_set_directory
    if single_hash_boolean == True and cewl_boolean == False:
        single_wordlist = os.path.join(wordlist_directory, 'rockyou.txt')
    elif single_hash_boolean == True and cewl_boolean == True:
        single_wordlist = default_cewl_file_output
    elif file_hash_boolean == True and cewl_boolean == False:
        single_wordlist = os.path.join(wordlist_directory, 'rockyou.txt')
    elif file_hash_boolean == True and cewl_boolean == True:
        single_wordlist = default_cewl_file_output
    if all_menu == True:
        pot_function()
        hashcat_command_line_menu()
        os.system('clear')
    else:
        hash_mode_menu()
        pot_function()
        hashcat_command_line_menu()
        os.system('clear')
    rule_set_walk()
    return

#Rsmangler - Create multiple permutations of a word 
def rsmangler_menu():
    global single_hash_boolean
    global single_wordlist
    global cewl_boolean
    global file_hash_boolean
    os.system("clear")
    banner()
    firmname = input("What is the name of the firm to be mangled?" + "\n")
    os.chdir(rsmangler_input_dir)
    sh = open(firmname, "w+")
    sh.write(firmname + "\n")
    sh.close()
    rsmangler = os.path.join(tools_dir, 'rsmangler.rb')
    rsmangler_output_dir_and_firmname = os.path.join(rsmangler_output_dir, firmname)
    rsmangler_input_dir_and_firmname = os.path.join(rsmangler_input_dir, firmname)
    rs = [rsmangler, '--file', rsmangler_input_dir_and_firmname, '--output', rsmangler_output_dir_and_firmname]
    subprocess.cal(rs)
    hashcat_command_line_menu()
    banner()
    hash_mode_menu()
    pot_function()
    if single_hash_boolean == True and cewl_boolean == False:
        single_wordlist = rsmangler_output_dir_and_firmname # Space added for correct argument spacing
    elif single_hash_boolean == True and cewl_boolean == True:
        single_wordlist = default_cewl_file_output
    elif file_hash_boolean == True and cewl_boolean == False:
        single_wordlist = rsmangler_output_dir_and_firmname # Space added for correct argument spacing
    elif file_hash_boolean == True and cewl_boolean == True:
        single_wordlist = default_cewl_file_output
    os.system('clear')
    singular_wordlist()
    rsmangler_rule_set()
    
#Cewl menu - Ran first before 17 or 18 can be activated
def cewl_menu_16():
    global hash_input
    global wordlist_directory
    global cewl_boolean
    global default_cewl_file_output
    global single_hash_abs_path
    global cewl_wordlist_size
    cewl_boolean = True
    os.system('clear')
    banner()
    print(" We will now make a wordlist based on the given website address")
    cewl_url_input = input(" Specify the website for collecting the wordlist in full including protocols and ports numbers if non standard:" + '\n')
    if single_hash_boolean == True:
        hash_input = single_hash_abs_path + '.cewl-wordlist.txt'
    elif file_hash_boolean == True:
        hash_input = hash_input + '.cewl-wordlist.txt'
        default_cewl_file_output = os.path.join(cewl_upload_dir, hash_input)
    cm1 = ['cewl', '--depth', '2','--min_word_length', '5', cewl_url_input, '-v', '-w', default_cewl_file_output]
    subprocess.call(cm1)
    cm2 = ['cewl', '--depth', '2', '--min_word_length', '5', cewl_url_input, '-v', '-w', default_cewl_file_output]
    subprocess.call(cm2)
    cewl_wordlist_size = os.popen('wc -l ' + default_cewl_file_output).read()
    os.system('clear')
    banner()
    hash_mode_menu()
    os.system('clear')
    return

#Run straight Cewl Wordlist
def cewl_menu_17():
    global single_wordlist
    global default_cewl_file_output
    global cewl_boolean
    global file_hash_boolean
    if cewl_boolean == True and file_hash_boolean == True:
        single_wordlist = default_cewl_file_output
    elif cewl_boolean == True and single_hash_boolean == True:
        single_wordlist = default_cewl_file_output
    else:
        input("Cewl Wordlist not ran yet!, run cewl first, (Option 16)")
        crack_menu()
    hashcat_command_line_menu()
    pot_function()
    singular_wordlist()
    return

#Automated Cewl wordlist - {5 ANY Characters RIGHT --> LEFT incrementally} (could take a while dependant on size of cewl wordlist generated)
def cewl_menu_18():
    global single_wordlist
    global default_cewl_file_output
    global cewl_boolean
    global file_hash_boolean
    if single_hash_boolean == True and cewl_boolean == True:
        single_wordlist = default_cewl_file_output
    elif file_hash_boolean == True and cewl_boolean == True:
        single_wordlist = default_cewl_file_output
    else:
        input("Cewl Wordlist not ran yet!, run cewl first, (Option 16)")
        crack_menu()
    hashcat_command_line_menu()
    pot_function()
    #Right Side
    hc1 = ['hashcat', '-a', '6', '-m', hash_type, hash_abs_path, pot_file, single_wordlist, '?a?a?a?a?a', '-w', '3', '-O', '--increment']
    subprocess.call(hc1)
    #Left Side
    hc2 = ['hashcat', '-a', '7', '-m', hash_type, hash_abs_path, pot_file, '?a?a?a?a?a', single_wordlist, '-w', '3', '-O', '--increment']
    subprocess.call(hc2)
    os.system('clear')
    return


#All Menus
#This will increment the menus from 1 - Useful when leaving on the go..
def increment_menu():
    global all_menu
    global single_wordlist
    global single_hash_boolean
    global wordlist_walk
    global wordlist_directory
    all_menu = True
    os.system('clear')
    banner()
    hash_mode_menu()
    pot_function()
    hashcat_command_line_menu()
    #wordlist_directory = "/opt/wordlists/" # Added to re-establish the base directory.
    crack_menu_0()
    #wordlist_directory = "/opt/wordlists/" # Added to re-establish the base directory.
    crack_menu_1()
    #wordlist_directory = "/opt/wordlists/" # Added to re-establish the base directory.
    crack_menu_2()
    #wordlist_directory = "/opt/wordlists/" # Added to re-establish the base directory.
    crack_menu_3()
    #wordlist_directory = "/opt/wordlists/" # Added to re-establish the base directory.
    crack_menu_4()
    #wordlist_directory = "/opt/wordlists/" # Added to re-establish the base directory.
    crack_menu_5()
    #wordlist_directory = "/opt/wordlists/" # Added to re-establish the base directory.
    crack_menu_6()
    crack_menu_7()
    crack_menu_8()
    crack_menu_9()
        
#Crack Menu (Back Crack) - go back one stage...
def back_crack():
    global all_menu
    global cewl_boolean
    global single_hash_boolean
    global file_hash_boolean
    global pot_boolean
    os.system('clear')
    all_menu = False # Needed to reset for the automatic menu. 
    cewl_boolean = False # Needed to reset for new menu settings to be applied.
    single_hash_boolean = False # Needed to reset for new menu settings to be applied.
    file_hash_boolean = False # Needed to reset for new menu settings to be applied.
    pot_boolean = False # Needed to reset for new menu settings to be applied.
    main_menu()
    return


#Cracking Menu
def crack_menu():
    global hash_abs_path
    global default_cewl_file_output
    global cewl_boolean
    global cewl_wordlist_size
    global l00t_pot_dir
    global hash_input
    wordlist_directory = "/opt/wordlists/" # Added to re-establish the base directory.
    single_wordlist = "/opt/wordlists/"
    os.system('clear')
    try:
        while 1:
            if single_hash_boolean == True and not cewl_boolean == True:
                banner()
                print("")
                print('\t\t\t\t' + '\033[40m' + '--==Single Hash Cracking Menu==--' + '\033[0m')
                print("")
                print("")
                print(" Hash file created:")
                prYellow(single_hash_abs_path)
            elif single_hash_boolean == True and cewl_boolean == True:
                banner()
                print("")
                print('\t\t\t\t' + '\033[40m' + '--==Single Hash Cewl Cracking Menu==--' + '\033[0m')
                print("")
                print("")
                print(" Single Hash file in Use:")
                prYellow(single_hash_abs_path)
                print(" Cewl Wordlist in Use:")
                prYellow(default_cewl_file_output)
            elif file_hash_boolean == True and not cewl_boolean:
                banner() # Currently display duplicates first time round, second time round it only shows one banner.. 
                print("")
                print('\t\t\t\t' + '\033[40m' + '--==Multi Hash Cracking Menu==--' + '\033[0m')
                print("")
                print("")
                print(" Hash File Loaded: "),
                prYellow(hash_abs_path)
                print(" Hashes Loaded:    "),
                prRed(hashes_loaded)
                print(" Hashes Cracked:   "),
                pot = hash_input.lower()
                pot = pot + '.pot'
                pot_absolute = os.path.join(l00t_pot_dir, pot)
                if os.path.exists(pot_absolute):
                    with open(pot_absolute) as lines:
                        hashes_cracked = len(lines.readlines())
                        prGreen(hashes_cracked)
                else:
                    prRed("0")
            elif file_hash_boolean == True and cewl_boolean == True:
                banner() # Added after the call as still in the loop for aesthtics.
                print("")
                print('\t\t\t\t' + '\033[40m' + '--==Multi Hash Cewl Cracking Menu==--' + '\033[0m')
                print("")
                print("")
                print(" Hash file in use:")
                prYellow(hash_abs_path)
                print("")
                print(" Amount of Cewl words written + Absolute Path: ")
                prYellow(cewl_wordlist_size)
            print("")
            print('\033[44m' + 'Supported - NTLMv2 (NTHASH) -> NetNTLMv1 -> NetNTLMv2 -> MD5 -> SHA-512 -> RC4-HMAC-MD5 (Kerberoasting)' + '\033[0m')
            print("")
            prCyan("0) A single merged list of wordlists in the public domain - {Comprehensive Scan}")
            prLightPurple("1) Common Wordlists - includes rockyou, hashkiller - {Corporate Scan}")
            prCyan("2) Crackstation list - {Corporate Scan}")
            prLightPurple("3) +8 chars + 0-9 + UCASE + LCASE (with diacritic marks, Greek and Cyrillic characters)- {Corporate Scan}")
            prCyan("4) All words lists 4GB+ - (will take a while to cache each wordlist prior to testing) - {Comprehensive Scan}")
            prLightPurple("5) Oxford Dictionary + Starting with UPPER Case + upto 3 ANY Characters on RIGHT SIDE - {Corporate Scan}")
            prCyan("6) Oxford Dictionary + Starting with UPPER Case + upto 3 ANY Characters on LEFT SIDE {Corporate Scan}")
            prLightPurple("7) Oxford Dictionary + Starting with UPPER Case + upto 4 Numbers LEFT SIDE, upto 4 numbers RIGHT SIDE - {Corporate Scan}")
            prCyan("8) Oxford Dictionary MIXED CASE + upto 3 ANY Characters on RIGHT SIDE - {Corporate Scan}")
            prLightPurple("9) Rule Based - Rockyou or cewl - d3ad0ne -(Runtime ~1hr 43sec)")
            prCyan("10) Rule Based - Rockyou or cewl - OneRuleToRuleThemAll - (Runtime ~2hr 30sec)")
            prLightPurple("11) Rule Based - Rockyou or cewl - L33t speak rules (leetspeak.rule + unix-ninja-leetspeak.rule)")
            prCyan("12) Rule Based - Rockyou or cewl - oscommerce - (Runtime ~1sec)")
            prLightPurple("13) Rule Based - Rockyou or cewl - rockyou-30000 - (Runtime ~1sec)")
            prCyan("14) Rule Based - Rockyou or cewl -> Quick Test {hob064.rule} -> Comprehensive Test {d3adhob0.rule}")
            prLightPurple("15) Auto Multi Rule Test - Iterate through each rule with rockyou.txt - {Corporate Scan}")
            prCyan("16) Cewl Test - Enter the firms website to create a bespoke, focussed wordlist")
            prLightPurple("17) Run a straight Cewl wordlist test - (Run option 16 first to activate)")
            prCyan("18) Auto Cewl wordlist - {5 ANY Characters RIGHT --> LEFT incrementally} - (can take a while)")
            prLightPurple("19) Wordlist Mangling Tool - Various permutations of a specified name")
            prCyan("a) Multiple Tests - All of the above, mainly in ascending numerical order (~40 runs) - {Comprehensive Overnight Test}")
            prRed("b) Back to Main Menu")
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
                            "b": back_crack
                           }
            try:
                selection = input("\n Select an Option: ")
                crack_option[selection]()
            except KeyError:
                os.system('clear')
                banner()
                pass
    except KeyboardInterrupt:
                sys.exit()
                
                  
#Single Hash Menu
def single_hash_menu():
    global single_hash_file_name
    global single_hash_boolean
    global single_hash_abs_path
    single_hash_boolean = True
    os.system('clear')
    banner()
    print("Example NetNTLMv2 Hash")
    print("admin::N46iSNekpT:08ca45b7d7ea58ee:88dcbe4446168966a153a0064958dac6:5c7830315c7830310000000000000b45c67103d07d7b95acd12ffa11230e0000000052920b85f78d013c31cdb3b92f5d765c783030")
    print("Password - hashcat")
    print("")
    single_hash = input(" Add your hash" + '\n')
    single_hash_string = str(single_hash)
    print("")
    print(" You entered : " + '\n') + single_hash_string
    print(" OK - Need to put the hash into a file...") # Put hash into a file
    single_hash_file_name = input("Enter a logical filename: ")
    single_hash_abs_path = (os.path.join(hash_upload_dir, single_hash_file_name))
    os.chdir(hash_upload_dir)
    sh = open(single_hash_file_name, "w+")
    sh.write(single_hash_string)
    print("File Created")
    sh.close()
    crack_menu()
    return

    
#Hash File Upload Menu
def hash_from_file():
    global hash_abs_path
    global hash_input
    global hashes_loaded
    global file_hash_boolean
    global hash_upload_dir
    file_hash_boolean = True
    os.system('clear')
    banner()
    print('\033[33m' + ' Add hash files into the hash upload directory shown below:' + '\033[0m')
    prCyan(hash_upload_dir)
    print("")
    print('\033[34m' + ' Below are the files currently available in the hash upload directory.. (Hit Enter to Refresh)' + '\033[0m')
    print("")
    #Used for removing emacs created backup files ending with a tilde
    ignore = '~'
    for root, dirs, files in os.walk(hash_upload_dir):
        files.sort()
        for f in files:
            if not f.endswith(ignore):
                print(" \t" + os.path.join(f))
    print("")
    print('\033[33m' + ' Select the filename from the above list to be uploaded:' + '\033[0m')
    hash_input = input("-----> ")
    os.chdir(hash_upload_dir)
    try:
        if (os.path.isfile(hash_input)):
            print(" Hash File %s found and accepted..." % hash_input)
            hash_abs_path = (os.path.join(hash_upload_dir, hash_input))
            print(" Absolute Path of hash file is: \n") + hash_abs_path
            with open(hash_abs_path) as lines:
                hashes_loaded = len(lines.readlines())
            os.system('clear')    
            crack_menu()
        else:
            print(" Error: %s file not found" % hash_input)
            os.system('clear')
            hash_from_file()
    except KeyError:
        os.system('clear')
        pass
    except Exception:
        os.system('clear')
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
                task = input("\n Choose an Option: ")
                options[task]()
            except KeyError:
                os.system('clear')
                pass
    except KeyboardInterrupt:
                sys.exit()

if __name__ == '__main__':
    main_menu()

    
