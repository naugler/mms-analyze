#!/bin/python

import base64
from datetime import datetime
import drawsvg as draw
from PIL import ImageFont
import re
import surrogates
import textwrap
import untangle

inputpath = './sms.xml'
outputpath = './sms-fixed.xml'
imgpath = './book.svg'
'''
pattern = re.compile("&#([0-9][0-9][0-9][0-9][0-9]);&#([0-9][0-9][0-9][0-9][0-9]);")

with open(outputpath, 'a') as output:
    for i, line in enumerate(open(inputpath)):
        match = re.search(pattern, line)
        while match is not None:
            print('Found on line %s: %s' % (i+1, match.group()))
            print('line: '+line)
            code1 = chr(int(match.group(1)))
            code2 = chr(int(match.group(2)))
            codepoint = surrogates.decode(''.join([code1,code2]))
            line = ''.join([line[:match.start()],codepoint,line[match.end():]])
            print('fixed: '+line)
            match = re.search(pattern, line)
        output.write(line)
'''
chat = untangle.parse(outputpath)

messages = chat.smses.children

messages_sorted = dict()
for message in messages:
    timestamp = int(message['date'])/1000
    messages_sorted[timestamp] = message

pageWidth = 400
pageHeight = 1000
imageSize = 200
margin = 10
yOffset = 0
page = 1
background = '#222222'
bobcolor = '#3d6070'
cancolor = '#734978'
fontColor = '#DDDDDD'
fontName='Helvetica'
fontSize = 10
font=ImageFont.truetype('./Helvetica-emoji.ttf', size=fontSize)
lasttime=0
lastsender=""
max_timeskip=1000*60*2
d = draw.Drawing(pageWidth, pageHeight, origin=(0, 0))
d.append(draw.Rectangle(0, 0, pageWidth, pageHeight, fill=background,rx='10',ry='10'))

def addPage():
    global d
    global page
    global yOffset
    d.save_svg("page"+str(page)+".svg")
    
    d.save_png("page"+str(page)+".png")
    page = page + 1
    yOffset = 0
    d = draw.Drawing(pageWidth, pageHeight, origin=(0,0))
    d.append(draw.Rectangle(0, 0, pageWidth, pageHeight, fill=background,rx='10',ry='10'))

def checkPage(timestamp, yNeeded, sender):
    global yOffset
    global lasttime
    global lastsender
    # skip to a new page if there isn't enough space
    if (yOffset+yNeeded > pageHeight):
        addPage()
    # print the date at the top of the page or when it's been a while
    if (yOffset == 0 or timestamp - lasttime > max_timeskip):
        yOffset += fontSize
        # checkPage(timestamp, fontSize*1.5, sender)
        timestring = datetime.fromtimestamp(timestamp).strftime('%B %d - %H:%m')
        d.append(draw.Text(timestring, fontSize*0.7, x=pageWidth/2, y=yOffset, text_anchor='middle', font_family=fontName, fill='#BBBBBB'))
        yOffset += fontSize*3
        lasttime = timestamp
    # use less space between texts from the same person
    if (lastsender in sender):
        yOffset -= margin*0.5
    lastsender = sender[2:] # skip country code and stuff
    

def addText(timestamp, address, text):
    global yOffset
    text = textwrap.fill(text, 70)
    if (text.count('\n') > 0):
        width = 350
    else:
        width = font.getlength(surrogates.encode(text))+margin*2

    textOffset = margin + 10
    rectOffset = margin
    align = 'start'
    rectColor = cancolor
    if ('6604' in address):
        textOffset = pageWidth-margin-10
        rectOffset = pageWidth-margin-width
        align = 'end'
        rectColor = bobcolor
    height = fontSize*text.count('\n')
    checkPage(timestamp, height+fontSize+margin*2, address)

    d.append(draw.Rectangle(rectOffset, yOffset, width, height+fontSize+margin, fill=rectColor, rx='3', ry='3'))
    d.append(draw.Text(text, fontSize, x=textOffset, y=yOffset+fontSize*1.5, text_anchor=align, font_family=fontName, fill='white'))
    yOffset += height+fontSize+margin*2

def addImage(timestamp, address, imageData):
    global yOffset
    checkPage(timestamp, imageSize+margin, address)
    xOffset = (margin, pageWidth-imageSize-margin) ['6604' in address]
    image = draw.Image(xOffset, yOffset, imageSize, imageSize, data=imageData,rx='10',ry='10')
    d.append(image)
    yOffset += imageSize

def addMMS(timestamp, address, parts):
    for part in parts.part:
        # print("adding at yOffset=",yOffset)
        if (part['ct'].startswith('text')):
            addText(timestamp, address, part['text'])
        elif (part['ct'].startswith('image')):
            addImage(timestamp, address, base64.b64decode(part['data']))
        # elif (part['ct'].startswith('video')):
        #     print("video here")
        # else:
        #     print(part)

for timestamp,message in sorted(messages_sorted.items()):
    timestamp = int(message['date'])/1000
    if message.__hasattribute__('parts'):
        sender = list(filter(lambda x: x['type'] == '137', message.addrs.addr))[0]
        addMMS(timestamp, sender['address'], message.parts)
    else:
        # print(message['type']+" "+message['body'])
        address = ('4104464378', '4109036604') ['2' in message['type']]
        addText(timestamp, address, message['body'])

addPage()
