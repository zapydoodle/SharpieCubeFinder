import requests
import re
import os
import json

def Main():
    inputName=input("What are you looking for in the card's name? ")
    inputName=inputName.replace(" ","")
    regExName=MakeRegEx(inputName)
    inputText=input("What are you looking for in the card's text? (rules and flavour text are combined) ")
    inputText=inputText.replace(" ","")
    regExText=MakeRegEx(inputText)
    cards=GetCards(regExName,regExText)
    file = open("output.txt","w")
    print("List complete")
    print("Writing to output.txt")
    for card in cards:
        #print(card['name'])
        file.write(card['name'] + " " + card['set'] + "\n")
    file.close()
    

def MakeRegEx(inputText):
    regEx='.*'.join(inputText)
    #print(regEx)
    return regEx


def FetchCards(url):
    """Fetch cards from Scryfall based on the provided URL."""
    cards = []
    while url:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            cards.extend(data['data'])
            url = data.get('next_page')  # Get the next page of results
        else:
            print(f"Error: {response.status_code}")
            break
    return cards
    
def CombineText(card):
    """Combine oracle (rules) text and flavor text into one block."""
    oracleText = card.get('oracle_text', '')
    flavorText = card.get('flavor_text', '')
    combinedText = oracleText + " " + flavorText
    return combinedText.strip()  # Remove any leading/trailing whitespace

def FilterByName(cards, nameRegex):
    """Filter cards whose names match the given regex."""
    matchedCards = []
    for card in cards:
        if re.search(nameRegex, card['name'], re.IGNORECASE):  # Case-insensitive search
            matchedCards.append(card)
    return matchedCards

def FilterByCombinedText(cards, textRegex):
    """Filter cards where the combined oracle and flavor text matches the regex."""
    matchedCards = []
    for card in cards:
        combinedText = CombineText(card)
        if re.search(textRegex, combinedText, re.IGNORECASE):  # Case-insensitive search
            matchedCards.append(card)
            print(card['name'] + " " + card['set'])
    return matchedCards

def GetCards(regExName,regExText):
    url = "https://api.scryfall.com/cards/search?q=t:creature+OR+t:sorcery+OR+t:instant+OR+t:artifact+OR+t:land+OR+t:enchantment+OR+t:battle+OR+t:planeswalker"
    #cards = FetchCards(url)
    cards = GetLocalOrRemote(url)
    print("Searching for cards")
    nameFilteredCards = FilterByName(cards, regExName)
    finalMatchedCards = FilterByCombinedText(nameFilteredCards, regExText)
    return finalMatchedCards

def GetLocalOrRemote(url):
    filepath= "cards.json"
    if os.path.exists(filepath):
        update=input("Would you like to update the local card database? (y/n) ")
        if update == "y":
            cards = FetchCards(url)
            with open(filepath, "w") as json_file:
                json.dump(cards, json_file)
                print("Local database updated")
        elif update == "n":
            with open(filepath, "r") as json_file:
                cards = json.load(json_file)
    else:
        createLocalDatabase=input("Would you like to create a local card database? (y/n) ")
        if createLocalDatabase == "y":
            cards = FetchCards(url)
            with open(filepath, "w") as json_file:
                json.dump(cards, json_file)
                print("Local database created")
        elif createLocalDatabase == "n":
            cards = FetchCards(url)
    return cards
        
if __name__ == "__main__":
    Main()