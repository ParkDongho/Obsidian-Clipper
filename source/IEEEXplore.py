from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from bs4 import BeautifulSoup

ieee_personal_sign_in =        '//*[@id="LayoutWrapper"]/div/div/div[3]/div/xpl-root/xpl-meta-nav/div/div/div/div[2]/ul/li/div[3]/ul/li[2]/a'
ieee_personal_sign_in_email =  '//*[@id="LayoutWrapper"]/div/div/div[3]/div/xpl-root/xpl-meta-nav/div/div/div/div[2]/ul/li/xpl-personal-signin/div/div/form/div[1]/input'
ieee_personal_sign_in_passwd = '//*[@id="LayoutWrapper"]/div/div/div[3]/div/xpl-root/xpl-meta-nav/div/div/div/div[2]/ul/li/xpl-personal-signin/div/div/form/div[2]/input'
ieee_personal_sign_in_click =  '//*[@id="LayoutWrapper"]/div/div/div[3]/div/xpl-root/xpl-meta-nav/div/div/div/div[2]/ul/li/xpl-personal-signin/div/div/form/div[3]/button/span'
ieee_title =                   '//*[@id="LayoutWrapper"]/div/div/div[3]/div/xpl-root/div/xpl-document-details/div/div[1]/section[2]/div/xpl-document-header/section/div[2]/div/div/div[1]/div/div[1]/h1'
ieee_abstract =                '//*[@id="LayoutWrapper"]/div/div/div[3]/div/xpl-root/div/xpl-document-details/div/div[1]/div/div[2]/section/div[2]/div/xpl-document-abstract/section/div[2]/div[1]/div/div/div'
ieee_date =                    '//*[@id="LayoutWrapper"]/div/div/div[3]/div/xpl-root/div/xpl-document-details/div/div[1]/div/div[2]/section/div[2]/div/xpl-document-abstract/section/div[2]/div[3]/div[1]/div[1]'
ieee_published_in =            '//*[@id="LayoutWrapper"]/div/div/div[3]/div/xpl-root/div/xpl-document-details/div/div[1]/div/div[2]/section/div[2]/div/xpl-document-abstract/section/div[2]/div[2]'
ieee_doi =                     '//*[@id="LayoutWrapper"]/div/div/div[3]/div/xpl-root/div/xpl-document-details/div/div[1]/div/div[2]/section/div[2]/div/xpl-document-abstract/section/div[2]/div[3]/div[2]/div[2]/a'


def dateConverter(date):
  result = date.replace("Date of Conference: ", "")
  strln = len(result)
  year = result[strln - 4 : strln]
  month = ""
  monthList = [["January", "01"], ["February", "02"], ["March", "03"], ["April", "04"], ["May", "05"], ["June", "06"], ["July", "07"], ["August", "08"], ["September", "09"], ["October", "10"], ["November", "11"], ["December", "12"]]
  for m in monthList:
    if result.find(m[0]) > 0:
      month = m[1]
      break
  day = result[0:result.find("-")]
  return year +"-"+ month +"-"+ day

def getBody(input):
  a = []
  for j in input.contents:
    # title & text
    # h1, h2, h3, h4, h5 : Title
    # kicker :
    # li :
    # p :
    if j.name == 'h1' or j.name == 'h2' or j.name == 'h3' or j.name == 'h4'\
            or j.name == 'h5' or j.name == 'kicker' or j.name == 'li' \
            or (j.name == 'p' and len(j.contents)) or (j.name == 'div' and j.attrs['class'][0] == 'figure'):
      a.append(j)

    # inline equation
    elif j.name == 'div' or j.name == 'ul' or j.name == 'ol':
      a = a + getBody(j)

  return a

def getTitle(i):
  if i.name == 'h2':  # 제목
    return [i.text, '# ']
  elif i.name == 'h3':  # 제목
    return [i.text, '## ']
  elif i.name == 'h4':  # 제목
    return [i.text, '### ']
  elif i.name == 'h5':  # 제목
    return [i.text, '#### ']
  else:
    return ['a', 'error']

def getFig(i):
  # Figure
  if i.name == 'div' and (i.attrs['class'][0] == 'figure') and len(i.attrs['class']) == 2:
    addr = i.contents[1].contents[0].attrs['href']
    type = "figure"
    if (len(i.contents) == 4): #일반적인...
      title =       i.contents[2].contents[0].text
      if (len(i.contents[2].contents[1].contents[0].contents) > 2):  # text에 수식 포함
        tmp = i.contents[2].contents[1].contents[0].contents
        [text, inline_formula, disp_formula] = getText(tmp)
        description = replaceEquation(text, inline_formula, disp_formula)
      else:
        description = i.contents[2].contents[1].text
    elif(len(i.contents) == 5): #copy본(흑백 칼라)
      title =       i.contents[3].contents[0].text
      if (len(i.contents[3].contents[1].contents[0].contents) > 2):  # text에 수식 포함
        tmp = i.contents[3].contents[1].contents[0].contents
        [text, inline_formula, disp_formula] = getText(tmp)
        description = replaceEquation(text, inline_formula, disp_formula)
      else:
        description = i.contents[3].contents[1].text
    else:
      print("getFig - Figure - ERROR")
      title = "ERROR : getFig - Figure - ERROR"
      description = "ERROR : getFig - Figure - ERROR"
      type = "figure"
    return [description, 'https://ieeexplore.ieee.org' + addr, title, type]
  # Table
  elif i.name == 'div' and (i.attrs['class'][2] == 'table'):
    addr = i.contents[1].contents[0].attrs['href']
    if(len(i.contents) == 2): #일반적인...
      title = i.contents[0].contents[0].text
      if(len(i.contents[0].contents) > 2): #inline 수식
        tmp = i.contents[1].contents[0].contents[0].attrs['data-alt']
        tmp = tmp.replace(title + "-", "")
        tmp = tmp.replace("\n", "")
        description = tmp
      else:
        description = i.contents[0].contents[1]
      type = "table"
    elif(len(i.contents) == 3): #text가 없음
      title = i.contents[1].contents[0].text
      if (len(i.contents[1].contents) > 2): #inline 수식
        tmp = i.contents[1].contents[0].contents[0].attrs['data-alt']
        tmp = tmp.replace(title + "-", "")
        tmp = tmp.replace("\n", "")
        description = tmp
      else:
        description = i.contents[1].contents[1]
      type = "table"
    else:
      title = "ERROR : getFig - Table - ERROR"
      description = "ERROR : getFig - Table - ERROR"
      type = "table"
    return [description, 'https://ieeexplore.ieee.org' + addr, title, type]
  else:
    return ['error', 'a', 'a']

def getText(i):
    text = ''
    ref_cont = 0
    ref_start = 0
    inline_formula_num = 0
    disp_formula_num = 0
    inline_formula = []
    disp_formula = []
    for j in i:
      if j.name == 'disp-formula':
        text = text + '{disp-formula_' + str(disp_formula_num) + '}'
        disp_formula.append("\n\n$$\n" + str(j.contents[1].contents[2].contents[0]) + "\n$$\n\n")
        disp_formula_num = disp_formula_num + 1
      elif j.name == 'inline-formula':
        text = text + '{inline_formula_' + str(inline_formula_num) + '}'
        inline_formula.append("$" + str(j.contents[0].contents[2].contents[0]) + "$")
        inline_formula_num = inline_formula_num + 1

      elif (j.name == 'b'): # Bold
        text = text + j.text
      elif (j.name == 'monospace'):
        text = text + j.text

      # anchor
      elif j.name == 'a' and j.attrs['ref-type'] == 'table': #table
        text = text + '{' + str(j.attrs['anchor']) + '}'
      elif j.name == 'a' and j.attrs['ref-type'] == 'sec':  # ref
        text = text + '{' + str(j.attrs['anchor']) + '}'
      elif j.name == 'a' and j.attrs['ref-type'] == 'disp-formula':  # ref
        text = text + '{' + str(j.attrs['anchor']) + '}'
      elif j.name == 'a' and j.attrs['ref-type'] == 'fig':  # ref
        text = text + '{' + str(j.attrs['anchor']) + '}'
      elif j.name == 'a' and j.attrs['ref-type'] == 'bibr': #ref
        if ref_start == 0:
          text = text + str(j.contents[0])
        ref_cont = 0
      elif j.name == 'a' and j.attrs['ref-type'] == 'fn':
        text = text
      elif (j == '–' or j == ', ') and ref_start == 1:
        ref_cont = 1
      elif (j.name == 'i'):
        text = text + j.text
      else:
        if ref_cont == 1:
          text = text + '//'
        ref_start = 0
        text = text + str(j)
    return [text, inline_formula, disp_formula]

def isTitle(str):
  if str == 'h1' or str == 'h2' or str == 'h3' or str == 'h4' or str == 'h5':
    return True
  else:
    return False

def isFig(str):
  if str == 'div':
    return True
  else:
    return False

def isText(str):
  if str == 'p':
    return True
  else:
    return False

def isLi(str):
  if str == 'li':
    return True
  else:
    return False

def translate(input):
  if(False):
    text = input
    text = text.replace(" ", "%20")
    text = text.replace("/", "%5C%2F")

    deepl_tran_korean = '//*[@id="panelTranslateText"]/div[1]/div[2]/section[2]/div[3]/div[1]/d-textarea/div/p'

    sleep(3)
    driver.get('https://www.deepl.com/translator#en/ko/' + text)
    sleep(3)
    reult = driver.find_element(By.XPATH, deepl_tran_korean).text
    sleep(3)
  if(True):
    reult = str(input)

  return reult

def replaceEquation(translatedStr, inline_formula, disp_formula):
  convertedStr = translatedStr

  # Inline formula
  for inline_formula_num in range(0, len(inline_formula)):
    formula_text = '{inline_formula_' + str(inline_formula_num) + '}'
    convertedStr = convertedStr.replace(formula_text, inline_formula[inline_formula_num])

  # Disp Formula
  for disp_formula_num in range(0, len(disp_formula)):
    formula_text = '{disp-formula_' + str(disp_formula_num) + '}'
    convertedStr = convertedStr.replace(formula_text, disp_formula[disp_formula_num])

  return convertedStr

def login2IEEEXplore():
  id_ieee = input("IEEE ID : ")
  pw_ieee = input("PASSWD : ")

  driver.get("https://ieeexplore.ieee.org/Xplore/home.jsp")
  sleep(2)
  driver.find_element(By.XPATH, ieee_personal_sign_in).click()
  sleep(2)
  driver.find_element(By.XPATH, ieee_personal_sign_in_email).send_keys(id_ieee)
  sleep(2)
  driver.find_element(By.XPATH, ieee_personal_sign_in_passwd).send_keys(pw_ieee)
  sleep(2)
  driver.find_element(By.XPATH, ieee_personal_sign_in_click).click()
  sleep(2)

  print("login complete")


driver = webdriver.Chrome('../chromedriver')
# login2IEEEXplore()

while (True):
  nextWork = input("contuinue?? : ")
  while(not(nextWork != "no" or nextWork != "yes" )):
    nextWork = str(input("contuinue?? : "))

  if(nextWork == "no"):
    break

  # driver.get("https://ieeexplore.ieee.org/document/" + str(input("site num : ")))
  sleep(3)

  html = driver.page_source
  soup = BeautifulSoup(html, 'html.parser')

  title = driver.find_element(By.XPATH, ieee_title).text
  abstract = driver.find_element(By.XPATH, ieee_abstract).text
  date = dateConverter(driver.find_element(By.XPATH, ieee_date).text)
  published_in = (driver.find_element(By.XPATH, ieee_published_in).text).replace("Published in: ", "")
  doi = driver.find_element(By.XPATH, ieee_doi).text

  file_name = title.replace(':', '')
  file_name = "../result/IEEEXplore/" + file_name + '.md'
  print(file_name)
  file = open(file_name, 'w')

  text_result = ""

  frontmeter =              "---\n"
  frontmeter = frontmeter + "title : "        + title + "\n"
  frontmeter = frontmeter + "date  : "        + date + "\n"
  frontmeter = frontmeter + "published_in : " + published_in + "\n"
  frontmeter = frontmeter + "doi : "          + doi + "\n"
  frontmeter = frontmeter + "tags : []" + "\n"
  frontmeter = frontmeter + "---\n\n"

  frontmeter = frontmeter + "> ** LINKS **\n"
  frontmeter = frontmeter + "> index: \n"
  frontmeter = frontmeter + "> baseline: [[]]\n\n\n"

  text_result = text_result + frontmeter

  accum = "**" + title + "**\n===============\n\n\n\n"
  text_result = text_result + accum
  accum = "# Abstract\n\n" + abstract + "\n\n"
  text_result = text_result + accum

  section_length = len(driver.find_elements(By.CLASS_NAME,'section'))
  for sec_num in range(1, section_length+1):
    section = getBody(soup.select_one('#sec' + str(sec_num)))
    for data in section:
      name = data.name
      if (isTitle(name)): #title
        [text, prefix] = getTitle(data)
        accum = prefix + text + "\n\n"
        text_result = text_result + accum
        # print(accum)
      elif (isFig(name)): #figure & table
        [description, addr, title, type] = getFig(data)
        accum = '![](' + addr + ")\n\n" + title + "\n" + translate(description) + "\n\n"
        text_result = text_result + accum
        # print(accum)
      elif (isText(name)):
        [text, inline_formula, disp_formula] = getText(data.contents)
        translated = replaceEquation(translate(text), inline_formula, disp_formula)
        # print(translated + "  \n\n")
        text_result = text_result + translated + "  \n\n"
      elif (isLi(name)):
        [text, inline_formula, disp_formula] = getText(data.contents[0].contents)
        translated = replaceEquation(translate(text), inline_formula, disp_formula)
        # print(translated + "  \n\n")
        text_result = text_result + "- " + translated + "  \n\n"

  file.write(text_result)
  file.close()

print("finish")
