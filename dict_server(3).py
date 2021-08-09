from socket import *
import sys
import os
import signal
import pymysql
import re
from time import sleep

# define global variables
dict_path = './dict.txt' 
HOST = '127.0.0.1'
PORT = 8888
ADDR = (HOST,PORT)


def do_search(cursor,c,word):
	# the method of database searching
	#search_word = 'select * from words where Words=%s'
	#cursor.execute(search_word,[word])
	#thing = cursor.fetchone()
	#if thing is None:
	#	msg = 'No this word.'
	#	c.send(msg.encode())
	#elif thing[1] ==  word:
	#	basket.append(word)
	#	msg = 'Okay '+thing[2]
	#	c.send(msg.encode())
	#	return

	# the method of document searching
	try:
		f = open(dict_path)
	except :
		c.send('Failed'.encode())
		return
	
	for line in f:
		pattern = r'\s+'
		string = line
		lis = re.split(pattern,string)
		words = lis[0]               
		pos_meanings = ' '.join(lis[1:]) 
		if word == None:
			f.close()
			return
		elif  words == word :
			msg = 'Okay '+ pos_meanings
			c.send(msg.encode())
			return
	msg = 'No this word.'
	c.send(msg.encode())
			

# Log in to the dictionary process : with correct name & password to verity
def do_login(cursor,c,db,name,password):
	exist_info = "select * from user where Name=%s;" 
	cursor.execute(exist_info,[name])
	thing = cursor.fetchone()
	if (thing[1],thing[2]) == (name,password):
		print('%s logged in successfully.'%name)
		c.send('LOkay'.encode())
		return
	c.send('Wrong'.encode())
	

# Register user registration process : with no duplicate name
def do_register(cursor,c,db,name,password):
	exist_info = "select * from user where Name=%s;" 
	cursor.execute(exist_info,[name])
	thing = cursor.fetchone()
	if thing != None:
		c.send('RE'.encode())
		return
	
	try:
		insert_info = 'insert into user(Name,password) values(%s,%s);'
		cursor.execute(insert_info,[name,int(password)]  )
		db.commit()
		print('%s registered successfully.'%name)
		c.send('ROkay'.encode())
	except Exception as e :
		print('Failed.',e)
		c.send('F'.encode())
		db.rollback()
	print('%s registered successfully.'%name)


# Insert words to user own note(my_vocabs) process: with no duplicate word
def insert_vocabs(cursor,c,db,name,word,pos):
	sql1 = "select count(*) from my_vocabs where Name=%s and Words=%s;"
	cursor.execute(sql1,[name,word])
	thing = cursor.fetchone()
	for i in thing:
		#if i is equal 1 means [word] is saved in note(my_vocabs).
		if i == 1:
			#send message to inform client this word cannot be saved twice.
			c.send('R'.encode())
			return
	#if i is not equal 1 or else(0) means [word] isn't saved in note(my_vocabs), insert word.
	try:
		sql0 = "insert into my_vocabs(Name,Words,POS) values(%s,%s,%s);"
		cursor.execute(sql0,[name,word,pos])
		db.commit()
		#send message to inform client this word is saved.
		c.send('Okay'.encode())
	except:
		db.rollback()


# Browse history of user own note process : word, part of speech
def do_history(cursor,c,db,name):
	sql = 'select * from my_vocabs where Name=%s;'
	cursor.execute(sql,[name])
	db.commit()
	thing = cursor.fetchall()
	# if nothing return means no data in history to browse.
	if thing == ():
		c.send('N'.encode())
		return
	else:
		c.send('Okay'.encode())
	sleep(0.5)
	for line in thing:
		msg = ' Word:%s , Part of speech:%s' %(line[1],line[2])
		c.send(msg.encode())
		sleep(0.1)
	sleep(1)
	c.send('Finish'.encode())


#Game of Word Challenge process : Hangman
def do_GOWC(cursor,c,db):
	c.send('S'.encode())
	

def recv_msg(c,db,cursor):
	while True:
		data = c.recv(1024)
		data_list = data.decode().split(' ')
		if (data.decode() == 'Q') or (not data):
			c.close()
			sys.exit('Byebye')
		elif  data_list[0] == 'L' :
			do_login(cursor,c,db,data_list[1],data_list[2])
		elif  data_list[0] == 'R' :
			do_register(cursor,c,db,data_list[1],data_list[2])
		elif data_list[0] == 'search':
			do_search(cursor,c,data_list[1])
		elif data_list[0] == 'y':
			insert_vocabs(cursor,c,db,data_list[1],data_list[2],data_list[3])
		elif data_list[0] == 'H':
			do_history(cursor,c,db,data_list[1])
		elif data_list[0] == 'G':
			do_GOWC(cursor,c,db)


def main():
	db = pymysql.connect(host=HOST,user='root',password='a123456',database='dict',charset='utf8')
	cursor =db.cursor()

	S = socket(AF_INET,SOCK_STREAM)
	S.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
	S.bind(ADDR)
	S.listen(5)
	print('Waiting for connection...')

	# Deal with child process status(quit)
	signal.signal(signal.SIGCHLD,signal.SIG_IGN)

	while True:
		try:
			client,addr = S.accept()
		except KeyboardInterrupt:
			S.close()
			sys.exit('Server quit, Byebye.')
		except Exception as error:
			print('Oops, server went wrong.',error)
			sys.exit(0)
			continue
		print('Connecting from :',client.getpeername())
		
		pid = os.fork()
		if pid == 0:
			S.close()
			recv_msg(client,db,cursor)
		else:
			client.close()
			continue


if __name__=="__main__":
	main()
