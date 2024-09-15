#!/bin/python

import base64
from datetime import datetime
import drawsvg as draw
import os
from PIL import ImageFont
import re
import surrogates
import textwrap
import untangle
from wand.image import Image
import matplotlib.pyplot as plt; plt.rcdefaults()
import matplotlib.dates as mdates
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import pandas as pd
import random
from wordcloud import WordCloud, STOPWORDS
plt.style.use('fivethirtyeight')

inputpath = './sms.xml'
outputpath = './sms-fixed.xml'
imgpath = './book.svg'
dpi = 400
margin = 24
screensPerPage = 3
screenHeight = dpi*(8.5)-margin*2
screenWidth = (dpi*(11)-margin*5+margin*screensPerPage)/screensPerPage
imageSize = 600
yOffset = 0
screen = 1
background = '#222222'
bobcolor = '#3d6070'
cancolor = '#734978'
fontColor = '#DDDDDD'
fontName='Helvetica'
fontSize = 40
font=ImageFont.truetype('./Helvetica-emoji.ttf', size=fontSize)
lasttime=0
lastsender=""
max_timeskip=1000*60*2


def grey_color_func(word, font_size, position, orientation, random_state=None,
            **kwargs):
    if 'love' in word:
        return 'red'
    else:
        return "hsl(0, 0%%, %d%%)" % random.randint(60, 100)

def fixSurrogatePairs():
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

def parseSMS():
    chat = untangle.parse(outputpath)
    messages = chat.smses.children

    messages_sorted = dict()
    for message in messages:
        timestamp = int(message['date'])/1000
        messages_sorted[timestamp] = message
    return messages_sorted

def createPlots(messages: dict):
    allTimes = np.array([time - 14400 for time in messages.keys()])
    bobTextTimes = []
    bobTextWords = ""
    canTextTimes = []
    canTextWords = ""
    for time,sms in messages.items():
        if sms.__hasattribute__('parts'):
            sender = list(filter(lambda x: x['type'] == '137', sms.addrs.addr))[0]
            if '6604' in sender['address']:
                bobTextTimes.append(time)
                for part in sms.parts.part:
                    if (part['ct'].startswith('text')):
                        bobTextWords += " "+part['text']
            elif '4378' in sender['address']:
                canTextTimes.append(time)
                for part in sms.parts.part:
                    if (part['ct'].startswith('text')):
                        canTextWords += " "+part['text']
            else:
                print("who is "+sender['address'])
        else:
            if '2' in sms['type']:
                bobTextTimes.append(time)
                bobTextWords += " "+sms['body']
            else:
                canTextTimes.append(time)
                canTextWords += " "+sms['body']
    # bobTimes = np.array([time - 14400 for time in bobTextTimes])
    # canTimes = np.array([time - 14400 for time in canTextTimes])
    # fig1, ax1 = plt.subplots(1)
    # ax1.set_title('Text Messages Sent / Week (11DEC2014 to 11DEC2015)')
    # ax1.title.set_color('white')
    # ax1.set_xlabel('date')
    # ax1.set_ylabel('nMsg')
    # ax1.set_facecolor('black')
    # ax1.xaxis.label.set_color('white')
    # ax1.tick_params(axis='x', colors='white', which='both')
    # ax1.tick_params(axis='y', colors='white', which='both')
    # ax1.yaxis.label.set_color('white')
    # fig1.patch.set_color('black')
    # bobTimeArray = np.asarray(bobTimes, dtype='datetime64[s]')
    # canTimeArray = np.asarray(canTimes, dtype='datetime64[s]')
    # startDay = np.datetime64(int(min(allTimes) / 86400) * 86400, 's')
    # endDay = np.datetime64(int(max(allTimes) / 86400) * 86400, 's')
    # startHalf = np.datetime64(int(min(allTimes) / 86400) * 86400 + 60*60*84, 's')
    # endHalf = np.datetime64(int(max(allTimes) / 86400) * 86400 + 60*60*84, 's')
    # bins = np.arange(startDay, endDay, 60*60*24*7)
    # bobBins = np.arange(startHalf, endHalf, 60*60*24*7)
    # print(str(bins[2]))
    # print(str(bobBins[2]))
    # # canBins = np.arange(startDay+np.datetime64(6,'h'), endDay+np.datetime64(6,'h'), 60*60*24)
    # bobHist,edges = np.histogram(bobTimeArray, bins=bins)
    # canHist,edges = np.histogram(canTimeArray, bins=bins)
    # bobbar = ax1.bar(bobBins[1:], bobHist, color=bobcolor, width=25000*7)
    # canbar = ax1.bar(bins[1:], canHist, color=cancolor, width=25000*7)
    # ax1.xaxis_date()
    # ax1.xaxis.set_major_locator(mdates.MonthLocator())
    # ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%y'))
    # ax1.legend( (bobbar[0], canbar[0]), ('bob', 'candice') )

    # labels = 'bob', 'candice'
    # sizes = [len(bobTimes), len(canTimes)]
    # colors = [bobcolor, cancolor]
    # fig2, ax2 = plt.subplots()
    # _, _, autotexts = ax2.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90, textprops={'color':"w"})
    # # for autotext in autotexts:
    # #     autotext.set_color('white')
    # ax2.set_facecolor('black')
    # fig2.patch.set_color('black')

    stopwords = set(STOPWORDS)
    stopwords.add("the")
    stopwords.add("and")
    stopwords.add("is")
    stopwords.add("at")

    # wc = WordCloud(stopwords=stopwords).generate_from_frequencies(counts[0]);
    print(bobTextWords+canTextWords)
    wc = WordCloud(stopwords=stopwords, width=1080, height=8).generate(bobTextWords+canTextWords)
    # fig3, ax3 = plt.subplots()
    plt.title("Bob's WordCloud")
    plt.imshow(wc.recolor(color_func=grey_color_func, random_state=3),
            interpolation="bilinear")
    plt.axis("off")

    plt.show()

def addScreen():
    global d
    global screen
    global yOffset
    d.save_svg("screen"+str(screen)+".svg")
    screen = screen + 1
    yOffset = 0
    d = draw.Drawing(screenWidth, screenHeight, origin=(0,0))
    d.append(draw.Rectangle(0, 0, screenWidth, screenHeight, fill=background,rx='40',ry='40'))

def checkPage(timestamp, yNeeded, sender):
    global yOffset
    global lasttime
    global lastsender
    # skip to a new page if there isn't enough space
    if (yOffset+yNeeded > screenHeight):
        addScreen()
    # print the date at the top of the page or when it's been a while
    if (yOffset == 0 or timestamp - lasttime > max_timeskip):
        yOffset += fontSize
        # checkPage(timestamp, fontSize*1.5, sender)
        timestring = datetime.fromtimestamp(timestamp).strftime('%B %d - %H:%m')
        d.append(draw.Text(timestring, fontSize*0.8, x=screenWidth/2, y=yOffset, text_anchor='middle', font_family=fontName, fill='#BBBBBB'))
        yOffset += fontSize*3
        lasttime = timestamp
    # use less space between texts from the same person
    if (lastsender in sender):
        yOffset -= margin*0.5
    lastsender = sender[2:] # skip country code and stuff
    

def addText(timestamp, address, text):
    global yOffset
    text = textwrap.fill(text, 60)
    if (text.count('\n') > 0):
        width = screenWidth*.81
    else:
        width = font.getlength(surrogates.encode(text))+margin*2

    textOffset = margin + 20
    rectOffset = margin
    align = 'start'
    rectColor = cancolor
    if ('6604' in address):
        textOffset = screenWidth-margin-20
        rectOffset = screenWidth-margin-width
        align = 'end'
        rectColor = bobcolor
    height = fontSize*text.count('\n')
    checkPage(timestamp, height+fontSize+margin*3, address)

    d.append(draw.Rectangle(rectOffset, yOffset+margin, width, height+fontSize+margin*1.75, fill=rectColor, rx='20', ry='20'))
    d.append(draw.Text(text, fontSize, x=textOffset, y=yOffset+margin+fontSize*1.5, text_anchor=align, font_family=fontName, fill='white'))
    yOffset += height+fontSize+margin*3

def addImage(timestamp, address, imageData):
    global yOffset
    checkPage(timestamp, imageSize+margin*2, address)
    xOffset = (margin, screenWidth-imageSize-margin) ['6604' in address]
    image = draw.Image(xOffset, yOffset, imageSize, imageSize, data=imageData,rx='24',ry='24')
    d.append(image)
    yOffset += imageSize

def addMMS(timestamp, address, parts):
    for part in parts.part:
        # print("adding at yOffset=",yOffset)
        if (part['ct'].startswith('text')):
            addText(timestamp, address, part['text'])
        elif (part['ct'].startswith('image')):
            addImage(timestamp, address, base64.b64decode(part['data']))
        elif (part['ct'].startswith('video')):
            addText(timestamp, address, "<VIDEO>")
        # else:
        #     print(part)

def createScreens(messages: dict):
    for timestamp,message in sorted(messages.items()):
        timestamp = int(message['date'])/1000
        if message.__hasattribute__('parts'):
            sender = list(filter(lambda x: x['type'] == '137', message.addrs.addr))[0]
            addMMS(timestamp, sender['address'], message.parts)
        else:
            # print(message['type']+" "+message['body'])
            address = ('4104464378', '4109036604') ['2' in message['type']]
            addText(timestamp, address, message['body'])
    addScreen()
    print("created "+str(screen)+" screens")

def convertSVGtoPNG():
    files = os.listdir("./")
    files.sort(key=lambda x: os.path.getmtime(x))
    for file in files:
        filename = os.fsdecode(file)
        if filename.startswith("screen") and filename.endswith(".svg"):
            print("converting "+filename)
            # try npm svgexport, seems to work most of the time
            retval = 1
            while (retval != 0):
                retval = os.system("svgexport "+filename+" "+filename.rsplit(".",1)[0]+".png")
                print("return value: "+str(retval))

def createPages():
    page = 1
    screensThisPage = 0
    pageWidth = margin*3 + (screenWidth+margin)*screensPerPage + margin*2
    pageHeight = margin*3 + screenHeight + margin*3
    print("page width: "+str(pageWidth))
    print("page height: "+str(pageHeight))
    d = draw.Drawing(pageWidth, pageHeight, origin=(0, 0))
    d.append(draw.Rectangle(0, 0, pageWidth, pageHeight, fill="#000000"))

    files = os.listdir("./")
    files.sort(key=lambda x: os.path.getmtime(x))

    for file in files:
        filename = os.fsdecode(file)
        if filename.startswith("screen") and filename.endswith(".png"):
            print("adding "+filename+" to page "+str(page))
            print("        x = "+str((screenWidth*screensThisPage)+margin))
            print("        y = "+str(margin))
            print("    width = "+str(screenWidth))
            print("   height = "+str(screenHeight))
            print("     path = "+str(file))
            d.append(draw.Image(
                margin*3 + ((screenWidth+margin)*screensThisPage),
                margin*3,
                screenWidth, screenHeight,
                path=file, embed=True))
            screensThisPage += 1
        if screensThisPage == screensPerPage:
            d.save_png("page"+str(page)+".png")
            d = draw.Drawing(pageWidth, pageHeight, origin=(0, 0))
            d.append(draw.Rectangle(0, 0, pageWidth, pageHeight, fill="#000000"))
            screensThisPage = 0
            page += 1
    d.save_png("page"+str(page)+".png")


d = draw.Drawing(screenWidth, screenHeight, origin=(0, 0))
d.append(draw.Rectangle(0, 0, screenWidth, screenHeight, fill=background,rx='40',ry='40'))

#fixSurrogatePairs()
messages = parseSMS()
#createPlots(messages)
createScreens(messages)
convertSVGtoPNG()
createPages()
