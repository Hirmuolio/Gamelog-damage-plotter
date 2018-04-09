#!/usr/bin/env python3

import math
import os
import re
import datetime
import time
import calendar
from datetime import datetime
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import matplotlib.pyplot as plt
import numpy as np

regex_damageout = re.compile('<color=0xff00ffff><b>(\d*).*')
regex_damagein = re.compile('<color=0xffcc0000><b>(\d*).*')


def read_log(*args):

	selected_color = colorselector.get()
	if selected_color == 'Blue':
		color = 'b-'
	elif selected_color == 'Green':
		color = 'g-'
	elif selected_color == 'Red':
		color = 'r-'
	elif selected_color == 'Cyan':
		color = 'c-'
	elif selected_color == 'Magenta':
		color = 'm-'
	elif selected_color == 'Yellow':
		color = 'y-'
	elif selected_color == 'Black':
		color = 'k-'
	else:
		color = 'b-'
		
	draw_outgoing = outgoing_checkbox.get()
	draw_incoming = incoming_checkbox.get()
	
	draw_out_dps = dps_checkbox.get()
	draw_in_dps = incomingdps_checkbox.get()
	
	filename =  filedialog.askopenfilename(initialdir = os.path.dirname(os.path.realpath(__file__)),title = "Select file",filetypes = (("txt files","*.txt"),("all files","*.*")))
	
	in_date_list = []
	out_date_list = []
	
	cumulative_in=0
	cumulative_out = 0
	cumulative_out_list = []
	cumulative_in_list = []
	
	
	#These shouldn't match with anything
	date_in = 99999
	date_out = 99999
	
	#Track number of lines
	line_number = 0
	
	with open(filename) as log:

		for line in log:
			#The character name is on third line
			if line_number == 2:
				name = line[11:]
				print('Name: ' + name)
				
			#Only care about combat lines
			if line[24:32] == '(combat)':
				
				#You deal damage
				if '<color=0xff00ffff><b>' in line:
				
					
					timestamp = line[2:21]
					
					date_old = date_out
					date_out = datetime.strptime(timestamp, "%Y.%m.%d %H:%M:%S")
					
					hit = int(regex_damageout.findall(line)[0])
					cumulative_out = cumulative_out + hit
					
					#Fix for hits that happen on same second
					if date_old == date_out:
						cumulative_out_list[-1] = cumulative_out
						
							
					else:
						out_date_list.append(date_out)
						cumulative_out_list.append(cumulative_out)
						
						
					
					
				#You take damage
				if '<color=0xffcc0000><b>' in line:
					
					timestamp = line[2:21]
					
					date_old = date_in
					date_in = datetime.strptime(timestamp, "%Y.%m.%d %H:%M:%S")
					
					hit = int(regex_damagein.findall(line)[0])
					cumulative_in = cumulative_in + hit
					
					#Fix for hits that happen on same second
					if date_old == date_in:
						cumulative_in_list[-1] = cumulative_in
					else:
						in_date_list.append(date_in)
						cumulative_in_list.append(cumulative_in)
						
			line_number = line_number + 1

		if draw_out_dps:
			print('Calculating and drawing outgoing dps')
			#Calculate outgoing DPS
			dps_out_list = []
			dpsout_times = []

			#Need to convert the datetimes to seconds
			time_array = []

			for i in out_date_list:
				time_array.append(calendar.timegm(i.timetuple()))

			#Iterate every second
			#Find starting and ending boundaries to data point so that they include time from -5s to +5s
			#Calculate DPS with the data points in these boundaries
			#If can't find boundaries don't calculate for this point. DPS=0
			starting_time = time_array[0]
			end_time = time_array[-1]

			index_list = list(range(0, len(time_array)))
			for current_time in range(starting_time, end_time):
				
				dpsout_times.append(time.strftime('%m/%d/%Y %H:%M:%S', time.gmtime(current_time)))
				indexes = [ j for (i,j) in zip(time_array,index_list) if i >= current_time-12 and i <= current_time+12 ]
				
				if len(indexes) >= 5:
					start = min(indexes)
					end = max(indexes)
					dps = np.polyfit(time_array[start:end], cumulative_out_list[start:end], 1)[0]
					dps_out_list.append(dps)
					
				else:
					dps_out_list.append(0)
			plt.plot_date(dpsout_times, dps_out_list, 'b-')
		
		if draw_in_dps:
			print('Calculating and drawing incoming dps')
			#Calculate incoming  DPS
			dps_in_list = []
			dpsin_times = []

			#Need to convert the datetimes to seconds
			time_array = []

			for i in out_date_list:
				time_array.append(calendar.timegm(i.timetuple()))

			#Iterate every second
			#Find starting and ending boundaries to data point so that they include time from -5s to +5s
			#Calculate DPS with the data points in these boundaries
			#If can't find boundaries don't calculate for this point. DPS=0
			starting_time = time_array[0]
			end_time = time_array[-1]

			index_list = list(range(0, len(time_array)))
			for current_time in range(starting_time, end_time):
				
				dpsin_times.append(time.strftime('%m/%d/%Y %H:%M:%S', time.gmtime(current_time)))
				indexes = [ j for (i,j) in zip(time_array,index_list) if i >= current_time-12 and i <= current_time+12 ]
				
				if len(indexes) >= 5:
					start = min(indexes)
					end = max(indexes)
					dps = np.polyfit(time_array[start:end], cumulative_in_list[start:end], 1)[0]
					dps_in_list.append(dps)
					
				else:
					dps_in_list.append(0)
			plt.plot_date(dpsin_times, dps_in_list, 'r-')

				

		
		if draw_outgoing:
			print('Drawing outgoing damage')
			#Plot outgoing damage
			plt.plot_date(out_date_list, cumulative_out_list, color)
		
		if draw_incoming:
			print('Drawing incoming damage')
			#Plot incoming damage
			plt.plot_date(in_date_list, cumulative_in_list, 'r-')
		
		
		plt.ylabel('Damage/dps')
		plt.xlabel('Time')
		plt.grid(True)
		#axes = plt.gca()
		#axes.set_xlim([out_date_list[0],out_date_list[-1]])
		#axes.set_ylim([0,max(cumulative_in, cumulative_out)*1.1])
		plt.show()


#Clear all things
def clear_all(*args):
	plt.clf()
	plt.show()
	
#Control window
root = Tk()
root.title("Game log damage plotter")

window = ttk.Frame(root, padding="3 3 12 12")
window.grid(column=0, row=0, sticky=(N, W, E, S))

#Checkboxes
incoming_checkbox = IntVar()
incomingdps_checkbox = IntVar()
Checkbutton(window, text="Plot incoming damage", variable=incoming_checkbox).grid(row=3, sticky=W)
Checkbutton(window, text="Plot incoming dps", variable=incomingdps_checkbox).grid(row=4, sticky=W)

outgoing_checkbox = IntVar()
dps_checkbox = IntVar()
Checkbutton(window, text="Plot damage", variable=outgoing_checkbox).grid(row=1, sticky=W)
Checkbutton(window, text="Plot dps", variable=dps_checkbox).grid(row=2, sticky=W)

#Color selection
colors = [
"Blue",
"Green",
"Red",
"Cyan",
"Magenta",
"Yellow",
"Black"
]

colorselector = StringVar()
colorselector.set(colors[0])
color_menu = OptionMenu(window, colorselector, *colors)

#Buttons
ttk.Button(window, text="Open log", command=read_log).grid(column=2, row=3, sticky=W)
ttk.Button(window, text="Clear", command=clear_all).grid(column=3, row=3, sticky=W)

for child in window.winfo_children(): child.grid_configure(padx=5, pady=5)

root.bind('<Return>', read_log)

root.mainloop()
