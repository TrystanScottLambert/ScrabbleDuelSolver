###################
#
# Scrabble Cheat
#
###################

import numpy as np 
import pylab as plt
import itertools
from itertools import combinations
from itertools import permutations
from tqdm import tqdm
import fnmatch
from compiler.ast import flatten
import subprocess 
import datetime
import time
import os


letter_scores = {'A': 1,  'B': 3,  'C': 3, 'D': 2,
                 'E': 1,  'F': 4,  'G': 2, 'H': 4,
                 'I': 1,  'J': 8, 'K': 5, 'L': 1,
                 'M': 3,  'N': 1,  'O': 1, 'P': 3,
                 'Q': 10, 'R': 1,  'S': 1, 'T': 1,
                 'U': 1,  'V': 4,  'W': 4, 'X': 8,
                 'Y': 4,  'Z': 10}

reduce_tiles = {'N' :6, 'R' :6, 'T' :6, 'L' :4, 'S' :4, 'U' :4,
				'D' :4, 'G' :3, 'B' :2, 'C' :2, 'M' :2, 'P' :2, 
				'F' :2, 'H' :2, 'V' :2, 'W' :2, 'Y' :2, 'K' :1,
				'J' :1, 'X' :1, 'Q' :1, 'Z' :1}


# Getting the double and tripple letter tiles
def get_dltl(letter_board):
	f=open('Scrabble_dltl.csv')
	dltl = np.array([np.array(line.split()[0].split(',')) for line in f]).astype(float)
	x,y = np.where(letter_board <> '_')
	for i in range(len(x)):
		for j in range(len(y)):
			dltl[x[i],y[j]]=1
	f.close()
	return dltl


infile = '/home/trystan/Downloads/dict.txt'
f = open(infile)
words = np.array([line.split()[0] for line in f])
words_len = np.array([len(word) for word in words])
cut = np.where(words_len<12)[0]

words=words[cut]


#words = [word for word in words ]
Bad_words=[]
for char in reduce_tiles.keys():
	Bad_words.append([word for word in words if word.count(char) > reduce_tiles[char]])

words = np.setdiff1d(words,np.concatenate(Bad_words))
set_words = set(words)

#read in the csv board
def read_board():
	infile = 'Scrabble.csv'
	f = open(infile)
	board = np.array([np.array(line.split()[0].split(',')) for line in f])
	return board

def all_letters(tiles,length):
	tiles_sep = list(tiles)
	combos = list(combinations(tiles,length))
	all_words=[]
	for i in range(len(combos)):
		var=list(permutations(combos[i]))
		for j in range(len(var)):
			all_words.append(''.join(var[j]))
	return all_words

def full_word_list(tiles):
	all_words=[]
	for i in range(7):
		all_words+=all_letters(tiles,i+1)
	return np.array(all_words)

def get_real(word_list):
	var = words[np.in1d(words,word_list)]
	return var

nptime=[]
settime =[]
def get_real_fast(word_list):
	#var = words[np.in1d(words,word_list,assume_unique=True)]
	var = set_words.intersection(set(word_list))
	return var

def all_words(tiles):
	return get_real(full_word_list(tiles))

def simple_score(word):
	split_word=list(word)
	score = np.sum(np.array([letter_scores[letter] for letter in split_word]))
	return score

def get_score(word):
	split_word = list(word)
	score = np.sum(np.array([letter_scores[letter] for letter in split_word]))

	if len(split_word)==7:
		score += 50
	return score

def All_Options(tiles):
	place = '_'*11
	options = all_words(tiles)
	scores = np.array([get_score(word) for word in options])

	arg = np.argsort(scores)[::-1]
	options,scores = options[arg],scores[arg]
	for i in range(len(options)):
		print '{} \t {}'.format(options[i],scores[i])
	print

	all_placements = []
	for i in range(len(options)):
		all_placements += [place[:j] + options[i] + place[j+len(options[i]):] for j in range(12-len(options[i])) ]
	return all_placements

def Highest_tile_word(tiles):
	options = all_words(tiles)
	scores = np.array([get_score(word) for word in options])

	arg = np.argsort(scores)[::-1]
	options,scores = options[arg][0:5],scores[arg][0:5]
	print 'Highest 5 tiles: '
	for i in range(len(options)):
		print '{} \t {}'.format(options[i],scores[i])
	print
##########################################

def has_letters(array):
	if len(array) == len(np.where(array=='_')[0]):
		return False
	else:
		return True

def get_anchors(array_before,array,array_after):
	anchors=[]
	### Start by gettting all the anchor points from the letters in the array
	local_lets  = np.where(array <> '_')[0]
	#local_anchors = np.append(local_lets+1,local_lets-1)
	#local_anchors = np.intersect1d(np.arange(len(array)),local_anchors) ## remove ones "out the board"
	#anchors.append(local_anchors)

	if array_after <>0:
		after_lets = np.where(array_after <> '_')[0]
		anchors.append(after_lets)

	if array_before <>0:
		before_lets = np.where(array_before <> '_')[0]
		anchors.append(before_lets)

	anchors = np.unique(np.concatenate(anchors))
	anchors = np.setdiff1d(anchors,local_lets)

	return anchors

def reduce_array(array,pattern):
	reduction = [word for word in array if fnmatch.fnmatch(word,pattern)]
	return reduction

def check_patterns(array,pattern_list):
	all_ops = []
	for pattern in pattern_list:
		all_ops+=reduce_array(array,pattern)
	return all_ops


def generate_patterns(string):
	pattern = []
	local_string = '?'+string.replace('_','?')+'?' 
	for j in range(len(local_string)):
		for i in range(len(local_string)-1):
			if local_string[i+1] == '?' and local_string[j-1] =='?':
				var = local_string[j:i+1]
				
				if len(var)>1 and len(var) <> len(np.where(np.array(list(var)) == '?')[0]) and var.find('?') <> -1:
					pattern.append(local_string[j:i+1])

	return pattern

def gen_all_perms(combination_list):
	combo_list=[]
	for i in range(len(combination_list)):
		combo_list+=list(permutations(combination_list[i]))
	return combo_list

def gen_all_combos(tiles,pattern_list):
	combos = []
	for i in range(len(pattern_list)):
		
		empty = np.where(np.array(list(pattern_list[i]))=='?')[0]
		full = np.where(np.array(list(pattern_list[i]))<>'?')[0]
		n = len(empty)
		if n <8:

			variables = list(combinations(tiles,n))
			perms = gen_all_perms(variables)
			perms = [''.join(perm) for perm in perms]

			
			for perm in perms:
				word=''
				counter=0
				for j in range(len(pattern_list[i])):
					if (j in empty) == True:
						word+=perm[counter]
						counter+=1
					else:
						word+=pattern_list[i][j]
				combos.append(word)
	return np.array(combos)



def place_some_words(tiles,array):
	string = ''.join(array)
	board_tiles = ''.join(''.join(array).split('_'))
	key_words = np.array(filter(None,''.join(array).split('_')))

	patterns = generate_patterns(string)
	local_tiles = tiles+board_tiles
	all_combos = gen_all_combos(tiles,patterns)
	real_possible = get_real(all_combos)
	more_reduction = check_patterns(real_possible,patterns)
	more_reduction = np.setdiff1d(more_reduction,key_words)

	placements=[]
	for reduction in more_reduction:
		for key_word in key_words:
			pos_key_in_red = reduction.find(key_word)
			if pos_key_in_red <> -1:
				pos_key_in_key = string.find(key_word)
				placement = string[:pos_key_in_key-pos_key_in_red] + reduction + string[pos_key_in_key-pos_key_in_red+len(reduction):]
				placements.append(placement)

	placements = [placement for placement in placements if len(placement) < 12]
	return placements
 
def words_on_rows(tiles):
	print 'checking rows'
	global high_score
	playable_words = []
	rows_pos =[]
	for i in range(len(d)):
		if i == 0:
			anchors = get_anchors(0,d[0],d[1])
		elif i == len(d)-1:
			anchors = get_anchors(d[i-1],d[i],0)
		else:
			anchors = get_anchors(d[i-1],d[i],d[i+1])

		if len(anchors) <> 0:
			if ''.join(np.unique(d[i])) == '_':
				possible = reduce_standard_set(anchors)
			else:
				possible = place_some_words(tiles,d[i])

			for poss in possible:
				c = read_board()
				c[i] = np.array(list(poss))
				score = check_board_valid(c)
				if score>high_score:
					print poss+':'
					print c 
					print
					high_score = score
					playable_words.append(poss)
					rows_pos.append(i)
	print 
	print
	print 
	print '##############################'
	return playable_words,rows_pos

def words_on_columns(tiles):
	global high_score
	print 'Checking Columns'
	playable_words = []
	columns_pos=[]
	for i in range(len(dt)):
		if i == 0:
			anchors = get_anchors(0,dt[0],dt[1])
		elif i == len(dt)-1:
			anchors = get_anchors(dt[i-1],dt[i],0)
		else:
			anchors = get_anchors(dt[i-1],dt[i],dt[i+1])

		if len(anchors) <> 0:
			if ''.join(np.unique(dt[i])) == '_':
				possible = reduce_standard_set(anchors)
			else:
				possible = place_some_words(tiles,dt[i])

			for poss in possible:
				c = read_board()
				c=c.T
				c[i] = np.array(list(poss))
				score = check_board_valid(c,inverse=True)
				if score>high_score:
					print poss+': '
					print c.T
					print

					high_score = score
					playable_words.append(poss)
					columns_pos.append(i)
	print 
	print
	return playable_words,columns_pos

def plays_rows_columns(tiles):
	Highest_tile_word(tiles)
	rows,rpos = words_on_rows(tiles)
	columns ,cpos= words_on_columns(tiles)

	if len(columns)==0:
		highest_word = rows[-1], rpos[-1], 'R'
	else:
		highest_word = columns[-1], cpos[-1],'C'

	return highest_word
	#plays = np.array(rows+columns)


def subtract_strings(string1,string2):
	minus_string = ''
	for i in range(len(string1)):
		if string2[i] == '_':
			minus_string += string1[i]
		else:
			minus_string+='_'
	return minus_string


def tile_place(tiles,word_play,rc,idx):
	if rc == 'C':
		already_placed = ''.join(d[:,idx])
	elif rc == 'R':
		already_placed = ''.join(d[idx])

	placement = subtract_strings(word_play,already_placed)
	word_play_list = np.array(list(subtract_strings(word_play,already_placed)))

	tile_list = np.array(list(tiles))
	unique_tile_list = np.unique(tile_list)

	board_pos =[]
	tile_pos=[]
	counter=0
	for letter in unique_tile_list:
		var = np.where(word_play_list == letter)[0]
		another_var = np.where(tile_list == letter)[0]
		if len(var) == 0:
			tile_pos.append(-9)
			board_pos.append(counter)
		else:
			for k in range(len(var)):
				tile_pos.append(var[k])
				board_pos.append(another_var[k])
		counter+=1

	board_adb_pos =[]
	if rc == 'C':
		for i in tile_pos:
			board_adb_pos.append((i,idx))
	elif rc == 'R':
		for i in tile_pos:
			board_adb_pos.append((i,idx))

	return board_adb_pos,board_pos


			
check_board_time = []
in_time = []
def check_board_valid(board,inverse=False):
	row_words = np.concatenate([filter(None,''.join(row).split('_')) for row in board])
	column_words = np.concatenate([filter(None,''.join(row).split('_')) for row in board.T])
	board_words = np.unique(np.concatenate([row_words,column_words]))
	
	board_words_len  = np.array([len(word) for word in board_words])
	cut = np.where(board_words_len>1)[0]
	board_words = board_words[cut]

	real_board_words = get_real_fast(board_words)
	if len(real_board_words) == len(board_words):
		if inverse == False:
			score = get_points_total(board)

		elif inverse == True:
			score = get_points_total(board.T)
		return score
	else:
		return -1


### Scoring Stuff ###############################
# function to turn all letters on a board to points 
def get_point_board(letter_board):
	point_board=np.array([np.array([letter_scores[arr]  if arr <> '_' else 0 for arr in row]) for row in letter_board])
	return point_board

def get_points_total(letter_board):
	point_board = get_point_board(letter_board)
	point_board=np.array([np.array([point_board[i][j]*dltl[i,j]+anchor_points[i,j] for j in range(len(point_board[i]))]) for i in range(len(point_board))])
	score = np.sum(point_board)
	if len(np.where(np.concatenate(point_board)==0)[0]) - len(np.where(np.concatenate(d)=='_')[0]) == 7:
		score += 50  
	return score 

def get_anchor_point_board_row(point_board):
	anchor_point_board = []
	for i in range(len(point_board)):
		local_point_board = point_board[i].copy()
		local_point_board_score = np.zeros(len(local_point_board))
		#get the inline anchor points 
		local_lets = np.where(local_point_board <> 0)[0]
		local_anchors = np.intersect1d(np.arange(len(local_point_board)),np.append(local_lets-1,local_lets+1))
		local_anchors = np.setdiff1d(local_anchors,local_lets)
		local_score = []

		if len(local_anchors)>1:
			for j in range(len(local_anchors)):
				if j == 0:
					score = np.sum(local_point_board[:local_anchors[j]]) + np.sum(local_point_board[local_anchors[j]+1:local_anchors[j+1]])
					local_point_board_score[local_anchors[j]] = score
				if j <> len(local_anchors)-1 and j <> 0:
					score = np.sum(local_point_board[local_anchors[j-1]+1:local_anchors[j]])+np.sum(local_point_board[local_anchors[j]+1:local_anchors[j+1]])
					local_point_board_score[local_anchors[j]] = score
				elif j == len(local_anchors)-1:
					score = np.sum(local_point_board[local_anchors[j]+1:])
					local_point_board_score[local_anchors[j]] = score
		elif len(local_anchors)==1:
			score = np.sum(local_point_board)
			local_point_board_score[local_anchors[0]] = score

		anchor_point_board.append(local_point_board_score)
	return np.array(anchor_point_board)

def get_anchor_point_board_column(point_board):
	columns = point_board.T
	anchor_point_board = []
	for i in range(len(point_board)):
		local_point_board = columns[i].copy()
		local_point_board_score = np.zeros(len(local_point_board))
		#get the inline anchor points 
		local_lets = np.where(local_point_board <> 0)[0]
		local_anchors = np.intersect1d(np.arange(len(local_point_board)),np.append(local_lets-1,local_lets+1))
		local_anchors = np.setdiff1d(local_anchors,local_lets)
		local_score = []

		if len(local_anchors)>1:
			for j in range(len(local_anchors)):
				if j == 0:
					score = np.sum(local_point_board[:local_anchors[j]]) + np.sum(local_point_board[local_anchors[j]+1:local_anchors[j+1]])
					local_point_board_score[local_anchors[j]] = score
				if j <> len(local_anchors)-1 and j <> 0:
					score = np.sum(local_point_board[local_anchors[j-1]+1:local_anchors[j]])+np.sum(local_point_board[local_anchors[j]+1:local_anchors[j+1]])
					local_point_board_score[local_anchors[j]] = score
				elif j == len(local_anchors)-1:
					score = np.sum(local_point_board[local_anchors[j]+1:])
					local_point_board_score[local_anchors[j]] = score
		elif len(local_anchors)==1:
			score = np.sum(local_point_board)
			local_point_board_score[local_anchors[0]] = score


		anchor_point_board.append(local_point_board_score)
	return np.array(anchor_point_board).T

def get_anchor_point_board(point_board):
	first_instance = get_anchor_point_board_row(point_board)
	second_instance = get_anchor_point_board_column(point_board)
	anchored = first_instance + second_instance
	return anchored

##################################################################


def reduce_standard_set(anchors):
	letters = np.array([''.join(np.unique(np.array(list(standard))[anchors])) for standard in standard_set])
	cut = np.where(letters<>'_')[0]
	return list(np.array(standard_set)[cut])


def place_word(i,poss):
	c = d.copy()
	c[i] = np.array(list(poss))
	return c

##########################################

tile_coords = [(80,2000),(230,2000),(390,2000),(540,2000),(695,2000),(852,2000),(1000,2000)]

x_start = 60
y_start = 880
box_width = 200-103
def get_coords(i,j,cr):
	if i >-1 and j > -1:
		if cr =='C':
			x_pos = x_start + box_width*i
			y_pos = y_start + box_width*j
		elif cr =='R':
			x_pos = x_start + box_width*j
			y_pos = y_start + box_width*i
		return (x_pos,y_pos)



while True:
	tiles = input('Tiles: ')
	tiles = tiles.upper()
	standard_set = All_Options(tiles.upper())  # use if row is empty 
	d = read_board()
	dltl = get_dltl(d)
	dt = d.T
	anchor_points = get_anchor_point_board(get_point_board(d))
	high_score = 0
	highest_play  = plays_rows_columns(tiles)	
	moves = tile_place(tiles,highest_play[0],highest_play[-1],highest_play[1])
	for i in range(len(moves[0])):
		translated = get_coords(moves[0][i][1],moves[0][i][0],highest_play[-1])
		if translated <> None:
			print 'adb shell input touchscreen swipe {} {} {} {} 250 '.format(tile_coords[moves[1][i]][0],tile_coords[moves[1][i]][1],translated[0],translated[1])
			os.system('adb shell input touchscreen swipe {} {} {} {} 250 '.format(tile_coords[moves[1][i]][0],tile_coords[moves[1][i]][1],translated[0],translated[1])) 


