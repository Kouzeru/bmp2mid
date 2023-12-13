##########################
# KOUZERUMATSUITE
# 12 DECEMBER 2023

# BMP TO MIDI PROGRAM

##########################
# INCLUDES
import os, sys
from PIL import Image
from math import log2

##########################
# FILE INPUT
i = os.getcwd()
if len(sys.argv)>1:
 i = os.path.join(sys.argv[1])
 print("inputfile : "+i)
else:
 i = os.path.join(input("inputfile: "))
infile  = i

inp = Image.open(infile)
img = inp.convert("L")
inp.close()

out = open("out.mid","wb")

##########################
# Defining functions to have life easier

buffdata = bytearray()

def midi_WriteVLQ(value):
    buffer = [value&127] 
    value //= 128
    while value>0:
        buffer.append((value&127)|0x80)
        value //= 128
    buffer.reverse()
    for k in buffer:
        buffdata.append(k)
    
def midi_WriteArray(array):
    for k in array:
        buffdata.append(k)

##########################
# MIDI PROCESSING

# Define MIDI header chunk
header_chunk = b'MThd' + \
    b'\x00\x00\x00\x06' + \
    b'\x00\x01' + \
    b'\x00\x02' + \
    b'\x00\x14'  # 2 tracks, 50 ticks per quarter note

out.write(header_chunk)

track1_chunk = b'MTrk' + \
    b'\x00\x00\x00\x0B' + \
    b'\x00\xFF\x51\x03\x02\xF0\x50' + \
    b'\x00\xFF\x2F\x00'

out.write(track1_chunk)

midiTriggers = [0]*128
midiLast = [0]*128
midiLastDelta = 0
midiNowDelta = 50
ctable = [0,1,2,3,4,5,6,7,8,10,11,12,13,14,15]
#vtable = [9,11,13,16,19,22,26,32,38,45,53,64,76,90,107]
#vtable = [1, 4, 7, 12, 17, 24, 31, 40, 49, 60, 71, 83, 97, 111, 127]
#vtable = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
vtable = [32, 45, 55, 64, 71, 78, 84, 90, 96, 101, 106, 110, 115, 119, 123]
#vtable = [10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,]


from random import random

for c in ctable:
    midi_WriteVLQ(0)
    midi_WriteArray([0xC0|c,79])
    
for c in ctable:
    midi_WriteVLQ(0)
    midi_WriteArray([0xE0|c,int(random()*128),64+int((random()-.5)*16)])

for x in range(img.size[0]):
    for y in range(img.size[1]):
        n = y
        p = img.getpixel((x,img.size[1]-y-1))
        midiLast[y] += (p-midiLast[y])/2
        p = midiLast[y]
        trig_last = midiTriggers[y]
        if p > 0:
            #trig_new  = int(min(log2(8*p/256)*4+15,15))
            trig_new  = int(min((p/256*4)**0.5*15,15))
            #trig_new  = int(min((p/256*4)**1*15,15))
            if trig_new < 0: trig_new = 0
        else:
            trig_new = 0
        
        if trig_new != trig_last:
            while trig_last < trig_new:
                diff = midiNowDelta - midiLastDelta 
                midiLastDelta = midiNowDelta
                midi_WriteVLQ(diff)
                c = ctable[trig_last]
                v = vtable[trig_last]
                midi_WriteArray([0x90|c,n,v])
                trig_last += 1
                ...
            while trig_last > trig_new:
                diff = midiNowDelta - midiLastDelta 
                midiLastDelta = midiNowDelta
                midi_WriteVLQ(diff)
                trig_last -= 1
                c = ctable[trig_last]
                v = vtable[trig_last]
                midi_WriteArray([0x80|c,n,v])
                ...
            midiTriggers[y] = trig_last
        
    midiNowDelta += 1
    #l = ""
    #for k in midiTriggers:
    #    l += "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"[k]
    #print(l)
    print("Progress:",100*x/img.size[0],"%")

midi_WriteArray(b'\x00\xFF\x2F\x00')

out.write(b'MTrk')
out.write((len(buffdata)).to_bytes(4, 'big'))
out.write(buffdata)
out.close()