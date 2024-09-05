#!/bin/python

import base64
from datetime import datetime
import drawsvg as draw
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

print('Number of Messages: ',chat.smses['count'])

messages = chat.smses.children
times = [int(msg['date'])/1000 for msg in messages]
print('Start: ',datetime.fromtimestamp(min(times)))
print('End: ',datetime.fromtimestamp(max(times)))

messages_sorted = dict()
for message in messages:
    timestamp = int(message['date'])/1000
    messages_sorted[timestamp] = message

pageWidth = 500
pageHeight = 1000
fontSize = 10
imageSize = 200
margin = 10
yOffset = 0
page = 1
background = '#222222'
bobcolor = '#3d6070'
cancolor = '#734978'
font='Arial'
lasttime=0
max_timeskip=1000*60*2
d = draw.Drawing(pageWidth, pageHeight, origin=(0, 0))
d.append(draw.Rectangle(0, 0, pageWidth, pageHeight, fill=background,rx='10',ry='10'))

def addPage():
    global d
    global page
    global yOffset
    d.save_svg("page"+str(page)+".svg")
    page = page + 1
    yOffset = 0
    d = draw.Drawing(pageWidth, pageHeight, origin=(0,0))
    d.append(draw.Rectangle(0, 0, pageWidth, pageHeight, fill=background,rx='10',ry='10'))

def checkPage(timestamp, yNeeded):
    global yOffset
    global lasttime
    if (yOffset+yNeeded > pageHeight):
        addPage()
    # if (yOffset == 0):
    #     timestring = datetime.fromtimestamp(timestamp).strftime('%x - %X')
    #     d.append(draw.Text(timestring, fontSize*1.5, x=pageWidth/2, y=fontSize*2, text_anchor='middle', font_family=font, fill='white'))
    #     yOffset += fontSize*3
    print(datetime.fromtimestamp(timestamp).strftime('%x - %X'))
    print(datetime.fromtimestamp(lasttime).strftime('%x - %X'))
    print(timestamp - lasttime)
    if (timestamp - lasttime > max_timeskip):
        lasttime = timestamp
        checkPage(timestamp, fontSize*1.5)
        timestring = datetime.fromtimestamp(timestamp).strftime('%x - %X')
        d.append(draw.Text(timestring, fontSize*1.5, x=pageWidth/2, y=yOffset+fontSize*2, text_anchor='middle', font_family=font, fill='white'))
        yOffset += fontSize*3


def addText(timestamp, address, text):
    global yOffset
    text = textwrap.fill(text, 74)
    if (text.count('\n') > 0):
        width = 350
    else:
        width = margin*2+len(text)*5

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
    checkPage(timestamp, height+fontSize+margin*2)

    d.append(draw.Rectangle(rectOffset, yOffset, width, height+fontSize+margin, fill=rectColor, rx='3', ry='3'))
    d.append(draw.Text(text, fontSize, x=textOffset, y=yOffset+fontSize*1.5, text_anchor=align, font_family=font, fill='white'))
    yOffset += height+fontSize+margin*2

def addImage(timestamp, address, imageData):
    global yOffset
    checkPage(timestamp, imageSize)
    xOffset = (margin, pageWidth-imageSize-margin) ['6604' in address]
    image = draw.Image(xOffset, yOffset, imageSize, imageSize, data=imageData,rx='10',ry='10')
    d.append(image)
    yOffset += imageSize

def addMMS(timestamp, address, parts):
    for part in parts.part:
        print("adding at yOffset=",yOffset)
        if (part['ct'].startswith('text')):
            addText(timestamp, address, part['text'])
        elif (part['ct'].startswith('image')):
            addImage(timestamp, address, base64.b64decode(part['data']))
        elif (part['ct'].startswith('video')):
            print("video here")
        else:
            print(part)

for timestamp,message in sorted(messages_sorted.items()):
    timestamp = int(message['date'])/1000
    if message.__hasattribute__('parts'):
        sender = list(filter(lambda x: x['type'] == '137', message.addrs.addr))[0]
        addMMS(timestamp, sender['address'], message.parts)
    else:
        print(message['type']+" "+message['body'])
        address = ('candice', '6604') ['2' in message['type']]
        addText(timestamp, address, message['body'])

addPage()
#print('  Text: ',len(realtext))
#print('  Image: ',len(image))
#print('  Reactions: ',len(faketext))
#print('  Video: ',len(video))
#print('  Other: ',len(other))

#d = draw.Drawing(200, 100, origin=(0, 0))
#
#for sms in chat.smses:
#  text = dw.Text(sms., fontSize, x=None, y=None, *, center=False,
#        line_height=1, line_offset=0, path=None,
#        start_offset=None, path_args=None, tspan_args=None,
#        cairo_fix=True, **kwargs)


