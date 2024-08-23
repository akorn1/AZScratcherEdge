#Must have an open empty chrome window
#Must have the file with FILE_NAME created in this directory
#VSCode must be used, terminal must be opened and window aligned to the bottom right corner of the screen
import requests
#import os
import mouse
import time
import keyboard
#import KeyKuts
from bs4 import BeautifulSoup
from PIL import Image, ImageGrab
import pyperclip
import getpixelcolor
from tkinter import * 
from tkinter.ttk import *
from fastapi import FastAPI 
from google.oauth2 import service_account
from google.cloud import datastore
import json

#WINDOW_LBOUND = 815
#TRUE_LBOUND = 863
#WARNING: THIS SOFTWARE WILL CONTROL YOUR KEYBOARD AND MOUSE FOR UP TO 2 MINUTES.
#   ONCE THE PROGRAM RUNS AND YOU CLICK ON THE APPROPRIATE APPLICATIONS IN
#   THE APPROPRIATE ORDER, DO NOT TOUCH YOUR COMPUTER UNTIL THE FILE CLOSES
#   IF A PROBLEM ARISES, CLICK CTRL+ALT+DEL AND WAIT FOR THE PROGRAM TO END
#Returns a list of scratchers still running
#Need to update the constants to your machine's equivalent
#Need to have relevant file open and an empty full screen chrome tab
#pay_coord: where the price is: in between dollar sign and actual price, without highliting the dollar sign dragging right
#chrome_coord: when scrolled down so that the table is all that is visible, left of max prize but within table
#file coord: bottom-right of file tab, still able to select text

FILE_NAME = 'azscratcherdata.txt'
COMMIT_STRING = 'https://datastore.googleapis.com/v1/projects/rock-springs:commit'
#API_KEYFILE = 'rock-springs-key.json'
SCRATCHER_PATH = 'C:/Users/akorn/Documents/VSCode Files/Python/Scratcher/'

def main():
    data_populater = AZScratcherGatherer()
    gaming = ProcessGame()
    #Comment line below if data file is already accurately populated
    data_populater.GatherScratcherData()
    #time.sleep(1)
    #Process Textfile
    #open textfile
    magic_path = SCRATCHER_PATH+FILE_NAME
    scratch_file = open(magic_path, 'r')
    scratch_data = scratch_file.read()  #puts all info in scratch_data
    #Convert string data to lists
    scratch_list = gaming.convert_scratcher_string(scratch_data)
    #consts to access variables within scratchlist
    N = 0
    PR = 1
    OO = 2
    PA = 3
    T = 4
    #populate total remaining tickets
    total_tic_list = []
    sobj_list = []  #6-List of game objects
    id_list = []
    for game in scratch_list:
        total_tix_left = gaming.project_remaining_tix(game[T], game[OO])
        total_tic_list.append(total_tix_left)

        p_ev, d_ev, p_pool, c_pool = gaming.calculate_ev(game[PA], game[T], game[PR], total_tix_left)
        vary = gaming.calculate_var(d_ev, game[PA], game[T], game[PR], total_tix_left)
        scratch = ScratchObj(game[N], game[PR], game[OO], round_to(p_ev, 5), round_to(d_ev, 3), vary, p_pool, c_pool, total_tix_left)
        id_list.append(game[N][0:5])
        #STANDARD COMMAND, UNCOMMENT THIS CODE!!!
        #stat_list.append((game[N], game[PR], game[OO], p_ev, d_ev, vary)) 
        #TEST COMMAND, COMMENT THIS CODE!!!
        sobj_list.append(scratch)
    
    sobj_list.sort(key = lambda z:z.d_ev, reverse=True)
    #print(stat_list)
    game_dict = []
    game_list = []
    for game in sobj_list: 
        game_dict.append(game.get_dict())
        game_list.append(game.short_string())
    for game in game_list:
        print(game)
    #convert dictionary of games into json string
#    scratch_json = json.dumps(game_dict)
#    ans = send_data(game_dict)
#    print(ans)
    #requests.post(stat_list)
#place=0 is round to whole, place=2 round to hundredths, etc. num is number to round
def round_to(num, place):
    shifter = pow(10, place)
    return (round(num*shifter))/shifter
'''
def send_data(data_json):
    api_location = SCRATCHER_PATH + API_KEYFILE
    service_credentials = service_account.Credentials.from_service_account_file(api_location)
    client = datastore.Client(credentials=service_credentials, database=data_json)
    query: datastore.Entity
    query = client.get(key='#1451 Spicy Hot Cash')
    return query
    #entity_list = []
    
  #  for i in range(0, len(data), 1):
  #      game_name = data[i]['name']
  #      del data[i]['name']
  #      store_dict = data[i]
  #      entity_list.append(datastore.Entity(client.key(game_name, store_dict)))
  #      entity_list[len(entity_list-1)]['name'] = game_name
  #  client.put_multi(entity_list)
  #  query = client.get(key='#1451 Spicy Hot Cash')
  #  return query

    #Turn each dictionary element into
    #query = client.query()
    #agg_query = client.aggregation_query(query)
    #test = agg_query.fetch()
    #print(test)
'''

class ScratchObj(object):
    def __init__(self, name=None, price=None, oo=None, p_ev=None, d_ev=None, vary=None, total_prize=None, total_cost=None, proj_tix=None):
        self.name: str
        self.price: int
        self.overall_odds: float
        self.p_ev: float
        self.d_ev: float
        self.vary: float
        self.total_prize: int
        self.total_cost: int
        self.proj_tix: int
        self.name = name
        self.price = price
        self.overall_odds = oo
        self.p_ev = p_ev
        self.d_ev = d_ev
        self.vary = vary
        self.total_prize = total_prize
        self.total_cost = total_cost
        self.proj_tix = proj_tix
    def short_string(self):
        printstr = '('+self.name+', '+str(self.price)+', '+str(self.overall_odds)+', '+str(self.p_ev)+', '+str(self.d_ev)+')'
        return printstr
    def visual_string(self):
        printstr = '('+self.name+', '+str(self.price)+', '+str(self.overall_odds)+', '+str(self.p_ev)+', '+str(self.d_ev)+', '+str(self.vary)+')'
        return printstr
    def full_string(self):
        printstr1 = '('+self.name+', '+str(self.price)+', '+str(self.overall_odds)+', '+str(self.p_ev)+', '+str(self.d_ev)+', '
        printstr2 = str(self.vary)+', '+str(self.total_prize)+', '+str(self.total_cost)+', '+str(self.proj_tix)+')'
        return printstr1+printstr2
    def get_dict(self):
        VAR_ARR = ["name","price","oo","p_ev","d_ev","vary","total_prize","total_cost","proj_tix"]
        dict_made = {
            VAR_ARR[0] : self.name,
            VAR_ARR[1] : self.price,
            VAR_ARR[2] : self.overall_odds,
            VAR_ARR[3] : self.p_ev,
            VAR_ARR[4] : self.d_ev,
            VAR_ARR[5] : self.vary,
            VAR_ARR[6] : self.total_prize,
            VAR_ARR[7] : self.total_cost,
            VAR_ARR[8] : self.proj_tix
        }
        return dict_made
class ProcessGame(object):
    #Method to convert all data (as string) to list with 4 vars:
    #   price and OO stored in 1 list as tuples
    #   2nd nested list with pay amount
    #   3rd nested list with tix remaining
    def convert_scratcher_string(self, scratch_string: str):
        scratch_data = scratch_string.split('\n')
        overview_list = []
        self.s_name = ""
        self.this_price = -1
        self.this_oo = -1
        self.this_pay_list = []
        self.this_tix_list = []
        for i in range(0, len(scratch_data)-1, 1):
            snippet = scratch_data[i]
            #determine what kind of data this is
            match snippet[0]:
                case '#':
                    #Scratcher Title
                    self.s_name = snippet
                case '$':
                    #pay and numtix
                    #delimit string by tab
                    broken_payline = snippet.split('\t')
                    #Process million payline differently
                    adj_pay = broken_payline[0]
                    adj_pay = adj_pay.replace(',','')
                    if adj_pay.find('Million')>=0:
                        adj_pay = (adj_pay.replace(' Million',''))[1:]
                        adj_pay = int(1000000*float(adj_pay))
                    else:
                        adj_pay = int(adj_pay[1:])
                    self.this_pay_list.append(adj_pay)

                    #get numtickets
                    s_index = 0
                    while broken_payline[2][s_index] != ' ':
                        s_index += 1
                    adj_tix = int((broken_payline[2][:s_index]).replace(',',''))
                    self.this_tix_list.append(adj_tix)
                case 'O':
                    #Overall_Odds line
                    #Use index starting at the end
                    pointer = len(snippet)
                    while snippet[pointer-1] !=' ':
                        pointer -= 1
                    self.this_oo = float(snippet[pointer:])
                case '-':
                    #game delimiter
                    #Add data to overall list
                    overview_entry = list((self.s_name, self.this_price, self.this_oo, self.this_pay_list, self.this_tix_list))
                    overview_list.append(overview_entry)
                    #Add delimiter to each sublist
                    #pay_list.append(self.this_pay_list)
                    #tix_list.append(self.this_tix_list)
                    #clear variables for next game
                    self.s_name = ""
                    self.this_oo = 0
                    self.this_price = 0
                    self.this_pay_list = []
                    self.this_tix_list = []
                case _:
                    #price
                    self.this_price = int(snippet)
        return overview_list

    #returns number of tickets remaining assume oo odds are the same
    def project_remaining_tix(self, numTixarr: list[int], overall_odds: float):
        prize_tix_rem = 0
        for tix in numTixarr:
            prize_tix_rem += tix
        return overall_odds*prize_tix_rem
    #returns ev of game given pay list and remaining tickets list
    #totalTickets is total tickets projected to be left, price is price of ticket
    #returns ev%, ev$, prizepool
    def calculate_ev(self, payarr: list[float], numTixarr: list[int], price: int, totaltix: int):
        total_prize = 0
        for pline in range(0, len(payarr), 1):
            total_prize += payarr[pline]*numTixarr[pline]
        total_cost = price*totaltix
        percent_return = total_prize/total_cost
        dollar_return = (total_prize-total_cost)/totaltix
        return percent_return, dollar_return, total_prize, total_cost
    
    def calculate_var(self, dollar_ev: float, payarr: list[float], numTixarr: list[int], price: int, totaltix: int):
        adj_ev = dollar_ev + price
        num_cardboard = totaltix    #num empty tickets. Is finalized after loop
        variance = 0
        for i in range(0, len(payarr), 1):
            pay = payarr[i]
            tix = numTixarr[i]
            num_cardboard -= tix
            temp = (pay - adj_ev) ** 2
            temp *= (tix/totaltix)
            variance += temp
        return variance
        


class AZScratcherGatherer(object):
    #Constants
    BASE_URL = 'https://www.arizonalottery.com'
    GAME_END_STRING = "Game Ended"
    PRICE_STRING = 'Ticket Price: '
    #Used coordinates are ratios*maxdims
    CHROME_COORDINATES = (0.11067708333333333, 0.17476851851851852)     #change this to your shortcut or pin to chrome
    FILE_COORDINATES = (0.9869791666666666, 0.20601851851851852)   #this is where you should click to type into the terminal
    PAY_COORDINATES = (0.44140625, 0.6041666666666666)
    PAY_RANGE = 30/1564
    WAIT_PERIOD = 5
    A_WHILE = .1
    WAIT_FOR_LOAD = .8
    SHORT_WHILE = .01
    ONE_MOMENT = .000001
    #Gathers all scratcher data and puts them in file. returns names of all scratchers in respective order
    def GatherScratcherData(self):
        key = KeyKuts() #setup keyboard object

        cool_potential_links = self.__HTTP_Call()
        all_actual_links = []
        self.all_names = []
        for link in cool_potential_links:
            neatSoup = self.__scanLink(link)
            ended = neatSoup.text.find(self.GAME_END_STRING)
            if ended==-1:
                all_actual_links.append(link)
                #TEST PROTOCOL: uncomment below lines to only test first N links
#                if len(all_actual_links) >= 8:
#                    break
        #print(all_actual_links)
        #go to each of the valid links manually
        #clear file
        #make tkinter obj to get size of screen
        fcoord = self.__convertCoords(self.FILE_COORDINATES)
        ccoord = self.__convertCoords(self.CHROME_COORDINATES)
        pcoord = self.__convertCoords(self.PAY_COORDINATES)
        prange = self.__convertCoords((self.PAY_RANGE, 0))[0]
        #TEST CODE BELOW
#        time.sleep(1)
#        all_actual_links = ['/scratchers/1400-230-million-cash-explosion/']
        #Prioritize Notepad and Chrome as first two tabs
        #Clear file
        key.alt_tab()
        mouse.move(fcoord[0], fcoord[1], absolute=True, duration=self.ONE_MOMENT)
        mouse.click()
        key.command('ctrl+a')
        key.command('delete')
        time.sleep(.1)
        for scratcher in all_actual_links:
            #registers names to access later
            splitter = scratcher.split('/')
            splitter = splitter[len(splitter)-2].replace('-',' ')
            self.all_names.append(splitter)
            pyperclip.copy(splitter)    #copy titile to clipboard
            #print(splitter)
            #Paste title into document
            key.stype('#')
            key.paste()
            key.enter()
            # Go to chrome and paste link into browser. Sleep a moment.
            key.alt_tab()
            mouse.move(ccoord[0], ccoord[1], absolute=True, duration=self.ONE_MOMENT)
            mouse.click()
            time.sleep(.01)
            key.link_paste()
            key.type(self.BASE_URL)
            key.type(scratcher)
            key.enter()
            #Scroll down finite amount to start of paytable
            time.sleep(self.WAIT_FOR_LOAD)
            mouse.move(pcoord[0], pcoord[1], absolute=True, duration=self.ONE_MOMENT)
            mouse.hold(LEFT)
            mouse.move(prange, 0, absolute=False, duration=self.SHORT_WHILE)
            key.copy()
            mouse.release(LEFT)
            key.alt_tab()
            mouse.move(fcoord[0], fcoord[1], absolute=True, duration=self.ONE_MOMENT)
            mouse.click()
            key.paste()
            key.enter()
            key.alt_tab()
            mouse.move(ccoord[0], ccoord[1], absolute=True, duration=self.ONE_MOMENT)
            mouse.wheel(-7)
            time.sleep(self.A_WHILE) #.3

            le_grey = self.__findGrayscale(ccoord)
            end_coord = self.__convertCoords((self.CHROME_COORDINATES[0]+.2, le_grey))
            #Click_hold and drag to gather data
            mouse.hold(LEFT)
            mouse.move(end_coord[0], end_coord[1], absolute=True, duration=self.SHORT_WHILE)#self.SHORT_WHILE)
            #Copy data to clipboard
            key.copy()
            time.sleep(self.A_WHILE)
            mouse.release(LEFT)
            #Navigate back to terminal and echo it into the file w/ title name and delimiter
            key.alt_tab()
            #ScratcherNameCmd
            mouse.move(fcoord[0], fcoord[1], absolute=True, duration=self.ONE_MOMENT)
            mouse.click()
            key.paste()
            key.enter()
            key.type('-')
            key.enter()
        key.command('ctrl+s')   #save file
        key.command('ctrl+w')   #close file
        print("Executed. All relevant data stored, file ready for access")
    def getNames(self):
        return self.all_names
    def __convertCoords(self, ratio_tuple: tuple[float]):
        screen = Tk()
        screen_width = screen.winfo_screenwidth()
        screen_height = screen.winfo_screenheight()
        temp_list = list(ratio_tuple)
        temp_list[0] *= screen_width
        temp_list[1] *= screen_height
        return tuple(temp_list)

        #Navigates to terminal and pastes command. Requires Keyboard obj
        #NOTE: terminal must already be on-screen when method is called
        #DEPRECATED
        #def echoTerminal(key, data, isPasted):
        #    tcoord = convertCoords(TERMINAL_COORDINATES)
        #    mouse.move(tcoord[0], tcoord[1], absolute=True, duration=.000001)    #Navigate to open page
        #    mouse.click()
        #    key.type("echo '")
        #    if isPasted:
        #        key.paste()
        #    else:
        #        key.type(data)
        #    key.type("' ")
        #    key.stype(">")
        #    key.type(FILE_NAME)
        #    key.enter()

    def __HTTP_Call(self):
        first_soup = self.__scanLink('/scratchers/')
        #first_soup = scanLink()
        all_primary_links = [a["href"] for a in first_soup.find_all("a")]

        #sort through and only include links starting with /scratchers/13...
        #   OR /scratchers/14...
        link_filter = ['/scratchers/13', '/scratchers/14']
        somewhat_valid_links = []
        for i in link_filter:
            for j in all_primary_links:
                if(j.find(i)!=-1 and j not in somewhat_valid_links):
                    somewhat_valid_links.append(j)

        #return links of games to scrape (will include some ended games)
        return somewhat_valid_links

    def __scanLink(self, href_link):
        scratcher_URL = self.BASE_URL + href_link
        thisRequest = requests.get(scratcher_URL)
        soupy = BeautifulSoup(thisRequest.content, "html.parser")
        return soupy

    #returns coords of where bottom of table is located as a fraction of max height
    def __findGrayscale(self, start_tuple: tuple[float]):
        tink = Tk()
        max_height = tink.winfo_screenheight()
        grey_location = -1
        breakcolor = 235
        scnsht = ImageGrab.grab().convert('RGB').load() #Takes screenshot
        for y in range(int(start_tuple[1]), max_height, 5):
            color = scnsht[start_tuple[0],y]
            if color[0]<breakcolor or color[1]<breakcolor or color[2]<breakcolor:
                grey_location = y
                break
        return grey_location/max_height
#Method to attempt to access basic commands with better readability and more reusability
class KeyKuts(object):
    CMD_WAIT = .1
    QUICK_BREATH = .000001
    def copy(self):
        keyboard.press('ctrl+c')
        time.sleep(self.CMD_WAIT)
        keyboard.release('ctrl+c')
        time.sleep(self.CMD_WAIT)

    def paste(self):
        keyboard.press_and_release('ctrl+v')
        time.sleep(self.CMD_WAIT)

    def alt_tab(self):
        keyboard.press_and_release('alt+tab')
        time.sleep(self.CMD_WAIT)

    def enter(self):
        keyboard.press_and_release('enter')
        time.sleep(self.CMD_WAIT)

    def command(self, sentence: str):
        keyboard.press_and_release(sentence)
        time.sleep(self.CMD_WAIT)
    
    def link_paste(self):
        keyboard.press_and_release('F6')
        time.sleep(self.CMD_WAIT)

    def type(self, sentence: str):
        for char in sentence:
            keyboard.press_and_release(char)
            time.sleep(self.QUICK_BREATH)

    def stype(self, sentence: str):
        for char in sentence:
            actual_char = 'shift+' + char
            keyboard.press_and_release(actual_char)
            time.sleep(self.QUICK_BREATH)
    

if __name__=="__main__":
    main()

#content = soupy.find("div").text