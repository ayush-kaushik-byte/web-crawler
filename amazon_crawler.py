import urllib.request
from bs4 import BeautifulSoup as soup
import sys
from PyQt5.QtWidgets import (QApplication, QPushButton, QDesktopWidget, QMainWindow, 
                                QHBoxLayout, QVBoxLayout, QWidget, QLabel)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import webbrowser

class amazon_crawler():

    def __init__(self):
        self.url = 'https://www.amazon.in/s'
        self.headers = {'User-Agent':"Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"}
    
    def get_response(self):

        item = input("Enter product name : ")
        data = {'k':item}

        self.query = urllib.parse.urlencode(data)
        self.query.encode('utf-8')

        req = urllib.request.Request('{}?{}'.format(self.url,self.query), headers = self.headers)
        #req = urllib.request.Request(url, headers = headers)
        resp = urllib.request.urlopen(req)

        #f = open('response_data.html','w',encoding='utf-8')
        #f.write(resp.read().decode('utf-8'))
        #f.close()


        page_html = resp.read().decode('utf-8')
        page_soup = soup(page_html,'html.parser')
        resp.close()

        products = page_soup.find('div', {'class' : 'a-section a-spacing-medium'})
        #products = page_soup.find('div', {'class' : 'a-section a-spacing-medium'})
        #print(len(products))

        if(products == None):
            print('No object found')
            sys.exit()

        #print(products)
        return products
    
    def extract_details(self,products):

        prod_details_temp = []

        details = products.findAll('span')
        ref_detail = products.find('a',{'class' : 'a-link-normal a-text-normal'})
        #print(ref_detail['href'])
        #details.append(product.find('a', {'class' : 'a-link-normal'})['href'][0])
        #print(details)
        temp_details = [detail.get_text().strip() for detail in details]
        temp_details.append(f"https://www.amazon.in{ref_detail['href']}")
        indiv_prod_details = []
        for temp_detail in temp_details:
            if( temp_detail not in indiv_prod_details):
                indiv_prod_details.append(temp_detail)
        prod_details_temp.append(indiv_prod_details)

        prod_details = []

        #print(prod_details_temp[0])

        for i in range(len(prod_details_temp)):
            index = -1
            for j in range(len(prod_details_temp[i])):
                if('out of' in prod_details_temp[i][j]):
                    index = j
                    break
            if(index == -1):
                continue
            temp_detail = []
            temp_detail.append(prod_details_temp[i][1])
            if(prod_details_temp[i][-2] == 'Currently unavailable.'):
                temp_detail.append('Currently unavailable.')
                temp_detail.append('')
            else:
                temp_detail.append('Available')
                x = prod_details_temp[i][index+2]
                #print(x)
                #print(x[0:x[1:].find(u'₹')])
                temp_detail.append(x[0:x[1:].find('₹')])
            temp_detail.append(prod_details_temp[i][index])
            temp_detail.append(prod_details_temp[i][index+1])
            temp_detail.append(prod_details_temp[i][-1])

            prod_details.append(temp_detail)

        return prod_details
    def crawl(self):

        products = self.get_response()
        prod_details = self.extract_details(products)
        #print(prod_details)
        return prod_details

    def print_details(self,prod_details):

        for i in range(len(prod_details)):
            print("\nProduct no. {}\n".format(i+1))
            #print(prod_details[i])
            print('Poduct Name : {}'.format(prod_details[i][0]))
            print('Availability : {}'.format(prod_details[i][1]))
            print('Price : {}'.format(prod_details[i][2]))
            print('Rating : {}'.format(prod_details[i][3]))
            print('Reviews : {}'.format(prod_details[i][4]))

class item_box(QMainWindow):

    def __init__(self):
        super().__init__()
        self.crawler = amazon_crawler()
        self.prod_details = self.crawler.crawl()
        self.url = self.prod_details[0][-1]
        if(len(self.prod_details) == 0):
            print('no item found')
            sys.exit()
        self.style_sheet = '''.QMainWindow { background-color : black;
                                            border-style : solid;
                                            border-width : 3px;
                                            border-color : grey;
                                            border-radius : 8px;}
                                .QPushButton { background-color : black;
                                                color : yellow;
                                                border : black;
                                                border-width : 1px;
                                                border-style : solid;
                                                border-radius : 8px;}
                                .QWidget { background-color : black;
                                        border-style : solid;
                                        border-color : grey;
                                        border-width : 5px;
                                        border-radius : 8px; }
                                .QLabel { color : yellow;
                                        font-size : 14;
                                        font-style : verdana;
                                        padding : 3}'''
        self.font = QFont('Verdana',8)
        self.font.setBold(True)
        self.init_UI()
    
    def init_UI(self):
        
        #print(self.prod_details)
        self.prod_details_txt = 'Product Name : {}\nAvailability : {}\nPrice : {}\nRating : {}\nReviews : {}\n'
        self.prod_details_txt = self.prod_details_txt.format(self.prod_details[0][0],self.prod_details[0][1],self.prod_details[0][2],self.prod_details[0][3],self.prod_details[0][4])
        
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        #self.setWindowFLags(Qt.WindowStaysOnTopHint)
        self.setStyleSheet(self.style_sheet)

        self.central_widget = QWidget()
        
        self.buy_button = QPushButton('BUY',self)
        self.buy_button.setFont(self.font)
        self.buy_button.clicked.connect(self.buy_product)

        self.dismiss_button = QPushButton('DISMISS',self)
        self.dismiss_button.setFont(self.font)
        self.dismiss_button.clicked.connect(self.close)

        #print(self.prod_details_txt)
        #print(self.prod_details[0])
        self.product_review_lbl = QLabel()
        self.product_review_lbl.setFont(self.font)
        self.product_review_lbl.setText(self.prod_details_txt)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.buy_button)
        hbox.addWidget(self.dismiss_button)

        vbox = QVBoxLayout()
        #vbox.addStretch(1)
        vbox.addWidget(self.product_review_lbl)
        vbox.addLayout(hbox)
        
        self.central_widget.setLayout(vbox)
        self.setCentralWidget(self.central_widget)
        self.resize(self.sizeHint())
        self.setWindowOpacity(0.8)
        self.bottom_right()
    
    def bottom_right(self):

        qr = self.frameGeometry()
        br = QDesktopWidget().availableGeometry().bottomRight()
        qr.moveBottomRight(br)
        self.move(qr.topLeft())
    
    def buy_product(self):

        chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
        webbrowser.get(chrome_path).open(self.url)
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    item = item_box()
    item.show()
    sys.exit(app.exec_())