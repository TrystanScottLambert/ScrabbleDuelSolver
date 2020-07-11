##################################################
#
# Read Board and tiles
# Python script to automatically 
# read scrabble bord and tiles 
# and generate Scrabble.csv, Scrabble_dltl.csv,
# and tiles.csv
#
#################################################


import numpy as np 
from ppadb.client import Client
import time
from mss import mss 
from PIL import ImageEnhance
from PIL import Image
import pytesseract


adb = Client(host = '127.0.0.1',port = 5037)
devices = adb.devices()

if len(devices)==0:
	print('no device attached')
	quit()
device = devices[0]

def take_screenshot(device):
	image = device.screencap()
	with open('screen.png','wb') as f:
		f.write(image)

def process_image(image):
	image = image.convert('L')
	image = image.point(lambda x: 255 if x > 50 else 0,mode='L')
	image = ImageEnhance.Contrast(image).enhance(10)
	image = ImageEnhance.Sharpness(image).enhance(2)
	return image

def crop_tiles(image):
	image = image.crop((0,1953,1080,2069))
	return image

def crop_board(image):
	image = image.crop((0,825,1080,1893))
	return image

x_tile = 60
y_tile = 850
x_cor = 60
y_cor = 849
box_width = 200-103
boxs = 11

tw = (237,28,121,255)
dw = (255,139,113,255)
tl = (19,120,178,255)
dl = (144,204,255,255)
empty = (232,234,241,255)


def get_dltl(image):
	dltl = []
	for i in range(11):
		row = []
		for j in range(11):

			var = image.getpixel((x_tile+ box_width*j,y_tile+ box_width*i))
			print((x_tile+ box_width*j,y_tile+ box_width*i))
			if var == tw:
				row.append('10')
			elif var == dw:
				row.append('6')
			elif var == tl:
				row.append('3')
			elif var == dl:
				row.append('2')
			else:
				row.append('1')
		dltl.append(','.join(row)+' \n')
	f = open('Scrabble_dltl.csv','w')
	for line in dltl:
		f.write(line)
	f.close()

tile_coords = [(80,2000),(230,2000),(390,2000),(540,2000),(695,2000),(852,2000),(1000,2000)]

x_start = 60
y_start = 880
box_width = 200-103
def get_coords(i,j):
	x_pos = x_start + box_width*i
	y_pos = y_start + box_width*j
	return (x_pos,y_pos)



screen_shot = take_screenshot(device)
image = Image.open('screen_duels.png')
dltl = get_dltl(image)


tiles = crop_tiles(image)
tiles = process_image(tiles)
tile_letters = pytesseract.image_to_string(tiles)

board = crop_board(image)
#board = process_image(board)

#tiles.show()
#board.show()

print(tile_letters)