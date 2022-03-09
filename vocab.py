#! /opt/homebrew/bin/python3

# Created alias in .zshrc
# firstly run this : chmod +x vocab.py
# then use vocab as alias for it freely

import bs4,requests
import pyperclip
import os
import csv
import sys
import argparse
import random
import time
import pandas as pd
from termcolor import colored, cprint
from pyfiglet import Figlet

def duplicate_handler():

    ''' 
    Function to handle duplicate values in the csv file.
    Handles full duplicate rows and gives you choice to choose one of the rows 
    from same name possesing rows
    '''

    df = pd.read_csv('/home/skipper/vocab.csv')

    # Returns True if whole row is duplicate
    any_duplicate_rows = df.duplicated().any()

    # If whole rows are duplicate then simply remove duplicates
    if any_duplicate_rows : 
        df.drop_duplicates(inplace = True)
        df.to_csv('/home/skipper/vocab.csv',index = False)
        print("Duplicate Rows were removed....\n")

    df = pd.read_csv('/home/skipper/vocab.csv')

    # Returns True if there any same names in Word Column
    any_duplicate_names = df.duplicated(subset = ['Word']).any()

    if any_duplicate_names : 
        # Gives all duplicated values based on food recipe name 
        print(df[df.duplicated(['Word'],keep = False)])
        duplicate_index = (df[df.duplicated(['Word'],keep = False)].index.values.tolist())
        print("\nIndex Numbers : ",duplicate_index)

        choice = int(input('Enter which row [index no] to keep in your vocab.csv file : '))
        while choice not in duplicate_index:
            choice = int(input('Please enter row [index no] from given index number list : '))
        
        duplicate_index.remove(choice)
        df.drop(df.index[duplicate_index],inplace = True)
        df.to_csv('/home/skipper/vocab.csv',index = False)

        print("\nAll other duplicate word entries were deleted ... \n")



def get_vocabulary(query):
    res = requests.get('https://www.vocabulary.com/dictionary/' + query)
    res.raise_for_status()

    soup = bs4.BeautifulSoup(res.text,'html.parser')

    print('\n')
    word = soup.find('span',class_ = 'word')
    print(colored("Word : " + str(word.text),'magenta',attrs = ['bold']))


    vocab = soup.find('p',class_='short')

    if vocab is None : 
        print(colored("\nSomething wrong in the spelling...",'red',attrs=['bold']))
        print(colored("Choosing closest similarity : " + word.text,'red',attrs=['bold']))
        res = requests.get('https://www.vocabulary.com/dictionary/'+ word.text)
        res.raise_for_status()
        soup = bs4.BeautifulSoup(res.text,'html.parser')
        vocab = soup.find('p',class_='short')

    stars = '*'
    print(colored('\n'+stars*5 + 'short summary'+stars*5,'green'))
    print(" ")
    print(vocab.text)


    vocab_long = soup.find('p',class_='long')
    print(colored('\n' + stars *5 + 'long summary' + stars*5,'cyan'))
    print(" ")
    print(vocab_long.text)

    print('\n')

    col_1 = soup.find(class_='col-1')
    word_defs = col_1.find_all('li')

    meaning_one = str()

    for i,defs in enumerate(word_defs) : 
        word_type = defs.find(class_='pos-icon')
        meaning = defs.find(class_='definition')
        print(colored("Meaning :",'white',attrs = ['bold']), colored(' [' + str(word_type.text.title()) + ']','yellow') + colored(' => ','yellow',attrs=['blink']), meaning.contents[-1].strip())
        print(" ")
        if i == 0:
            meaning_one += str(meaning.contents[-1].strip())

        content = defs.find(class_='defContent')
        similar_types = content.find('dl',class_='instances')
        try:
            dd_tag = similar_types.find_all('dd')
        except:
            continue
        for tag in dd_tag : 
            sim_word = tag.find('a').text
            try:
                sim_def = tag.find('div').text
            except:
                sim_def = ''
            if sim_word.endswith('types...'): sim_word = ''
            else : 
                print('\t',colored(sim_word,'green',attrs=['underline','dark']),'->',sim_def,'\n')


    # Replacing ; with , as with ; it creates a new column for rest of the left string to be added
    meaning_one = meaning_one.replace(';', ',')
    print("Saving to file....")

    file_exists = os.path.isfile('/home/skipper/vocab.csv')


    with open('/home/skipper/vocab.csv','a',newline='') as file:

        fieldnames = ['Word','Short summary','Meaning']

        writer = csv.DictWriter(file,delimiter = ',',lineterminator='\n', fieldnames = fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow({'Word' : word.text,'Short summary' : vocab.text, 'Meaning' : meaning_one})

    print("vocab.csv updated!")
    duplicate_handler()
    print("Done!")

def revision_mode():

    file_exists = os.path.isfile('/home/skipper/vocab.csv')

    if not file_exists : 
        print("No vocab.csv file exists.. Please first search some few words using -w argument")
        sys.exit()

    words = []
    summary = []
    meaning = []
    with open('/home/skipper/vocab.csv','r') as file : 
        csv_reader = csv.reader(file,delimiter = ',')
        next(csv_reader)
        for row in csv_reader:
            # print(row)
            words.append(row[0])
            summary.append(row[1])
            meaning.append(row[2])
# points game
    points = 10
    print(colored("\nYou have 10 points...\n",'green'))

    while(points !=0):
        # random_word = random.choice(words)
        random_word = random.sample(words,1)[0]
        index_chosen = words.index(random_word)
        chosen_meaning = meaning[index_chosen]
        chosen_summary = summary[index_chosen]

        print(colored("Random word : " + random_word,'cyan',attrs=['bold']))
        response = input("Do you know the meaning ? Press Enter if Yes, Type N/n if No, Type Q/q to exit: ")

        if not response : # Enter key
            print(colored("\nWow! You know it..",'magenta',attrs=['bold']))
            print("\n(If you still want to see..) : ")
            print(colored("\nMeaning : " ,'yellow',attrs=['bold']), chosen_meaning)
            print("\nShort Summary : " + chosen_summary)
            print(colored("\nPoints Left : ",'cyan'), points)
            print("Good! Let's Move on..\n")
            time.sleep(4)

        elif response.lower() == 'n': # Space key
            print(colored("\nNot Sure ? Here you go ....",'magenta',attrs=['bold']))
            print(colored("\nMeaning : " ,'yellow',attrs=['bold']), chosen_meaning)
            print("\nShort Summary : " + chosen_summary)
            print(colored('\n1 Point deducted','red',attrs=['bold']))
            points -= 1
            print(colored("Points Left : ",'cyan'), points)
            print("")
            input("Press Enter to Continue :")
        elif response.lower() == 'q':
            break
        else :
            response = input("Do you know the meaning ? Press Enter if Yes, Type N if No : ")


        os.system('clear')
    os.system('clear')

    print(colored("Hope you learnt some new words!!",'magenta',attrs=['bold','blink']))

if __name__ == '__main__':


    parser = argparse.ArgumentParser(description = 'Vocabulary Tracker')
    parser.add_argument('-r','--rev',action = 'store_true',help = 'Revision mode')
    parser.add_argument('-w','--word',type=str,default = None,help='Enter the word ')
    args = parser.parse_args()

    if args.rev:
        os.system('clear')
        print("\n")
        f = Figlet(font = 'standard')
        print(colored(f.renderText('Revision Mode'),'green',attrs=['bold','blink']))
        print("\n")
        print(colored("\nYou have 10 points...\n",'green'))
        print(colored("\nWords Randomly will come up based on your history of dictionary searches...\n",'yellow'))
        print(colored("\nYou can quit the game in between by entering q/Q...\n",'red'))
        print(colored("\nGame will end when you have 0 points left...\n",'cyan'))
        for i in reversed(range(6)):
            time.sleep(1)
            print("Starting in ",i)

        os.system("clear")
        revision_mode()
        sys.exit()

    if args.word is None:
        query = pyperclip.paste()
        print("\nUsing the word from clipboard :",colored(query.split(' ')[0],'yellow',attrs=['bold','blink']))
        print(colored('Do you want to continue ?','green',attrs = ['bold']))
        choice = input("If yes, Press Enter, else enter any character : ")
        if not choice : 
            os.system('clear')
            print(colored("Searching...",'cyan',attrs = ['bold']))
        else:
            os.system('clear')
            print(colored("Exiting..Bye",'red',attrs=['bold','blink']))
            sys.exit()

        # print("Usage : python vocab.py -w [word]")
        # print("For Revision Mode: python vocab.py -r [rev]")

    else : 
        query = args.word

    get_vocabulary(query)

