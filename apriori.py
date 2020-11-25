import re
import sys
import time
from collections import defaultdict
singles = defaultdict(int)
#make sure the file exists and the correct arguments were supplied
def check_input():
	if(len(sys.argv) != 3):
		return False
	try:
		f = open(sys.argv[1],"r")
		f.close()
		return True
	except IOError:
		return False

'''
this method has 3 main tasks
		1. count up ocurrences of each item
		2. find and return the minimimum support(min_supp) given the confidence param(c)
		3. check each item to see if it is frequent and return frequent singles
''' 
def find_candidates(c):
	f = open(sys.argv[1],"r")
	#first line is num transactions
	trans_num = int(f.readline())
	for line in f:
		#take out transaction number and number of items
		line = re.sub('\t','x',line)
		partitions = line.split('x')
		line = str(partitions[2])
		items = line.split()
		for item in items:
			singles[item] += 1
	
	min_supp = (trans_num * c)/100
	freq_singles = prune(singles, min_supp)
	
	f.close()
	return min_supp,freq_singles

#make sure each candidate is frequent
def prune(c_tab, min_supp):
	freq_cand = []
	for key in c_tab:
		if c_tab[key] >= min_supp:
			freq_cand.append(key)
	return freq_cand

#create next table
def gen_next(items,freq_singles):
	c_tab = []
	c_tab_cmp = set()
	for item in items:
		for s in freq_singles:
			if s in item:
				continue
			
			to_add = item + ',' + s
			to_add_nums = str(to_add).split(',')
			to_add_nums = sorted(to_add_nums)
			to_add_cmp = ''
			for idx,num in enumerate(to_add_nums):
				if idx == len(to_add_nums) -1:
					to_add_cmp += num
				else:
					to_add_cmp += num + ','
			if to_add_cmp in c_tab_cmp:
				continue
			
			c_tab_cmp.add(to_add_cmp)
			c_tab.append(to_add)
	return c_tab			

# count all items
def count_items(cand,length):
	L_k = defaultdict(int)
	f = open(sys.argv[1],"r")
	f.readline()
	for line in f:
		#gets rid of first 2 cols
		line = re.sub('\t','x',line)
		partitions = line.split('x')
		line = str(partitions[2])
		items = line.split()
		for i in range(0,length):
			key_str = cand[i]
			key = str(cand[i]).split(',')
			#if new item
			if key_str not in L_k:
				L_k[key_str] = 0
			add_item = True
			for k in key:
				#if any item not in items do not count
				if k not in items:
					add_item = False
					break
			if add_item == True:
				L_k[key_str] += 1
	
	f.close()
	return L_k	
				
#writes fp to first line not all that efficiently	
def write_fp_file(out_file,tot_freq):
	first_line = "|FPs| = {total}\n"
	data = out_file.readlines()
	data[0] = first_line.format(total=tot_freq)
	out = open("output.txt", 'w')
	out.writelines(data)
	out.close()
	
def write_to_file(out_file,freq_items,c_tab,end = False):
	if end == True:
		out_file.close()
	out_file.write('----------\n')
	to_write = "{key} : {val}\n"
	for item in freq_items:
		out_file.write(to_write.format(key = item, val = c_tab[item]))

#driver code, checks to make sure correct input given then runs through subroutines to find association
def main():
	correct_input = check_input()	
	out_file = open("output.txt","w")
	if(correct_input):
		confidence = float(sys.argv[2])
		k = 1
		min_supp,freq_singles = find_candidates(confidence)
		L_table = gen_next(freq_singles,freq_singles)
		write_to_file(out_file,freq_singles, singles)
		k += 1
		candidates = True
		total_frequent = len(freq_singles)
		print('frequent singles found: {}'.format(total_frequent))
		while candidates:
			c_tab = defaultdict(int)
			c_tab = count_items(L_table,len(L_table))	
			freq_items = []
			freq_items = prune(c_tab,min_supp)
			write_to_file(out_file,freq_items, c_tab)
			total_frequent += len(freq_items)
			print('still running now at: {} freq items'.format(total_frequent))
			L_table = gen_next(freq_items,freq_singles)
			if not L_table:
				candidates = False
			k += 1
		out_file.close()
		out_file = open("output.txt","r")
		write_fp_file(out_file,total_frequent)
		print("minimum support threshold is: {}".format(min_supp))
		print ("total frequent count: {}".format(total_frequent))
	else:
		print ("Input format is: apr.py file.txt confidence")

main()
