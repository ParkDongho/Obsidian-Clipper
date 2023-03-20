from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from bs4 import BeautifulSoup
import os

def translate(input):
  text = input
  text = text.replace(" ", "%20")
  text = text.replace("/", "%5C%2F")

  deepl_tran_korean = '//*[@id="panelTranslateText"]/div[1]/div[2]/section[2]/div[3]/div[1]/d-textarea/div/p'

  driver.get('https://www.deepl.com/translator#en/ko/' + text)
  sleep(2)
  reult = driver.find_element(By.XPATH, deepl_tran_korean).text
  sleep(2)
  return reult

def parsing(line):
    if line[0] == "#":
        return 1
    elif line [0:4] == "![](":
        return 1
    elif line == "\n" or line == " \n" or line == "  \n":
        return 1
    elif line [0:6]  == "Figure" or line [0:5]  == "Fig. ":
        return 1
    elif line [0:5] == "Table" or line [0:6]  == "TABLE ":
        return 1
    elif line == "$$\n":
        return 2
    else:
        return 0

def Equation2P(strInput):
    eqStart = False
    result = ""
    inline = []
    inline_num = 0
    tmp = ""
    for data in strInput:
        if data == "$" and eqStart == False:
            eqStart = True
            tmp = data
        elif data != "$" and eqStart == True:
            tmp = tmp + data
        elif data == "$" and eqStart == True:
            tmp = tmp + data

            inline.append([tmp, "{inline_num_" + str(inline_num) + "}"])
            result = result + "{inline_num_" + str(inline_num) + "}"

            eqStart = False
            inline_num = inline_num + 1
        elif data != "$" and eqStart == False:
            result = result + data

    return [result, inline]

def P2Equation(inputList):
    [result, inline] = inputList
    for i in inline:
        result = result.replace(i[1], i[0])
    return result


driver = webdriver.Chrome('../chromedriver')
directory = os.listdir("../result/IEEEXplore/")

for doc_name in directory:
    english = open("../result/IEEEXplore/"     + str(doc_name), 'r')
    korean  = open("../translated/IEEEXplore/" + str(doc_name), 'w')
    englishList = english.readlines()
    equationStart = 0
    textStart = 0

    for line in englishList:
        parsed = parsing(line)
        if line[0] == "#" and equationStart == 0:
            korean.write(line)
            textStart = 1

        elif(textStart):
            if parsed == 1 and equationStart == 0:
                korean.write(line)

            elif parsed == 1 and equationStart == 1:
                print("ERROR")

            elif parsed == 2 and equationStart == 0:
                korean.write(line)
                print(equationStart)
                equationStart = 1
                
            elif parsed == 2 and equationStart == 1:
                korean.write(line)
                print(equationStart)
                equationStart = 0

            elif parsed == 0 and equationStart == 1:
                korean.write(line)
                print(equationStart)

            elif parsed == 0 and equationStart == 0:
                [result, inline] = Equation2P(line)
                translated = translate(result)
                converted = P2Equation([translated, inline])
                korean.write(converted + "\n")
        else:
            korean.write(line)

    english.close()
    korean.close()

    
    

