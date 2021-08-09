from socket import *
import sys
import os
import string
from time import sleep
import getpass
import random


def do_GOWC():
    l = [['a','p','p','l','e'] ,['g','o','o','d','s'], ['l','o','c','a','l']]
    mask = ['-','-','-','-','-']
    all_charts = string.punctuation + string.whitespace
    computer = random.choice(l[0:3])
    # basket to use for putting the words user guess.
    basket = [] 
    for tt in range(9): 
        n = input('\nEnter a word to guess, you only have 9 times to guess:')
        if n in basket:
            print('Repeated word,\033[31m %s \033[0m'% n)
        basket.append(n)
        if n in computer:
            for y in range(len(computer)):
                if computer[y] == n:
                   mask[y] = n
            print("\033[32m Current:\033[0m", mask)
        else:
            print('\033[32m Nothing correct, guess again! \033[0m')
        if len(n) > 1: 
            print('Enter only one word.')
        if n in all_charts:
        	print('Do not enter whitespace or punctuation marks.')
        if n.isalpha() is False:
            print('Enter an English word.')
        if mask == computer: 
            print('\033[31m You WIN! \033[0m')
            break
    print('Game over.')


def do_search(c,name):
	while True:
		action = input('\n1.Search English Words.\n2.Search My_Vocabs.\n3.Game of Word Challenge.\n(or "Enter" be back to re_level.): ')
		if not action:
			return
		elif action == '1':
			while True:
				search = input('\nSearch English Words\n(or "Enter" be back to re_level.):  ')
				if not search :
					break
				msg = 'search ' + search
				c.send(msg.encode())
				data = c.recv(1024)
				data_list = data.decode().split(' ')
				pos = data_list[1]
				meaning = ' '.join(data_list[2:])
				
				if data.decode() == 'No this word.':
					print('No this word.')
				elif data_list[0] == 'Okay':
					print('The word [%s] meaning is:\n%s.'%(search,meaning))
					#to save word in user own note by choosing yes/no
					note = input('Note word [%s] down or not ? y/n: '% search)
					if note == 'y':
						msg = 'y '+ name + ' ' + search + ' ' + pos
						c.send(msg.encode())
						data = c.recv(1024).decode()
						# receive ('R') from server means the word is in noted can't be saved twice.
						if data == 'R':
							print('Already in note.')
						else:
							print('Saved.')
					elif note == 'n':
						continue
				elif data.decode() == 'Failed':
					print('Document opened failed.')
		elif action == '2':
			msg = 'H '+ name
			c.send(msg.encode())
			data = c.recv(1024).decode()
			if data == 'N':
				print('No history.')
			elif data == 'Okay':
				while True:
					data = c.recv(1024).decode()
					if data == 'Finish':
						break
					else:
						print(data)
		elif action == '3':
			c.send('G'.encode())
			data = c.recv(1024).decode()
			if data == 'S':
				print("Let's get started!")
				do_GOWC()


def do_login(c):
	while True:
		try :
			name = input('\nEnter your name to log in:\n(or "Enter" be back to re_level.): ')
			if not name:
				return 'back'
			password = getpass.getpass('Enter your passowrd (six-digits): ')
			if 6 != len(password) or not int(password):
				print('Invalid passwords, please enter six-digits.')
				continue
		except Exception as e :
			print('Please enter six-digits.',e)
			continue
		except KeyboardInterrupt as e :
			sys.exit('Force to quit.')

		msg = 'L '+name+' '+password
		c.send(msg.encode())
		data = c.recv(1024).decode()
		if data == 'LOkay':
			print('Logged in successfully.')
			b = do_search(c,name)
			if b is None:
				return
		elif data == 'Wrong':
			print("Doesn't match." )
			continue


def do_register(c):
	all_charts = string.punctuation + string.whitespace
	while True:
		try :
			name = input('\nEnter your name to register:\n(or "Enter" be back to re_level.): ')
			for i in name:  
				if i in all_charts:
					print('Please do not enter whitespace or punctuation marks.')
					return
			if name.isalpha() is True:
				print('Hello, %s!' % name)
			elif not name:
				return 'back'
			elif name.isdigit():
				print('Invalid name, please enter alphabets.')
				continue
			#use getpass to hide the passowrd entering
			password = getpass.getpass('Enter your passowrd (six-digits): ')
			if 6 != len(password) or not int(password):
				print('Invalid passwords, please enter six-digits.')
				continue
			# to verify password to avoid the first one is wrong
			password2 = getpass.getpass('Verify passowrd again: ')
			if	password != password2:
				print('Does not match.')
				continue
		except Exception as e :
			print('Please enter six-digits.',e)
			continue
		except KeyboardInterrupt as e :
			sys.exit('Force to quit.')

		msg = 'R '+name+' '+password
		c.send(msg.encode())
		data = c.recv(1024).decode()
		if data == 'ROkay':
			print('Registered successfully.')
			return
		elif data == 'RE':
			print("Someone used this name, please enter other name to register." )
			continue
		elif data == 'F':
			continue


def snd_msg(c,cmd):
		if cmd == int(1):
			b = do_login(c)
			if b == 'back':
				return
		elif cmd == int(2):
			b = do_register(c)
			if b == 'back':
				return
			

def recv_msg(c):
	pass


def main():
	if len(sys.argv) < 3:
		print('Please enter full(py_file_name/ip/port): ')
		return

	HOST = sys.argv[1]
	PORT = int(sys.argv[2])
	ADDR = (HOST,PORT)

	client = socket(AF_INET,SOCK_STREAM)

	try:
		client.connect(ADDR)
	except Exception as e:
		print('Connection failed.',e)
		return 
	print('Connected!')

	while True:
		print('\nExplore the Dora Dictionary!')
		try:
			cmd = int(input('Enter you action(1.Log_in 2.Sign_up 3.Quit): '))
		except KeyboardInterrupt:
			sys.exit('Force to quit.')
		except ValueError:
			continue

		if cmd in [1,2] :
			snd_msg(client,cmd)
		elif cmd == int(3):
			client.send('Q'.encode())
			sleep(1)
			sys.exit('Thanks for using the Dora Dictionary.')
		else:
			# to close buffer
			sys.stdin.flush()
			continue

	pid = os.fork()
	if pid < 0:
		sys.exit('Failed.')
	elif pid == 0:
		snd_msg(client,ADDR)
	else:
		recv_msg(client)


if __name__=="__main__":
	main()
