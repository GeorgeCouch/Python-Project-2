# George Couch
# 5/21/2023
# This program uses various functions from within the Textblob api to perform actions on user entered text. It also
# simulates a text-based turn-based battle where every action is turned into text-to-speech and the results are
# written to a file.
# Time spent: 3.5 hours
# Time description: I had quite a hard time thinking of what I wanted to do with this project so that it would include
# classes. After coming up with a system to do so, making the loop and user validation was also a bit tricky. Overall,
# I finished in roughly the time that I expected to.

# imports
from textblob import TextBlob
from textblob import Word
from numpy.random import randint
import time
import pyttsx3


# Classes for character creation
# Base Class
class Character:
    def __init__(self, name: str, health: int, damage: int):
        self.name = name
        self.health = health
        self.damage = damage

    def actions(self):
        print("1: Attack for " + str(self.damage) + " damage")

    def attack(self):
        return self.damage

    def castSpell(self, selectedSpell):
        print("Cast Spell")


# first inherited class
class Warrior(Character):
    def __init__(self, name: str, health: int, damage: int, rage: int, weaponName: str):
        super().__init__(name, health, damage)
        self.rage = rage
        self.weaponName = weaponName

    # overridden methods
    def actions(self):
        print("1: Attack for " + str(self.damage) + " damage")
        print("2: Cleave for " + str(self.damage) + " damage and use 60 rage")

    def castSpell(self, selectedSpell):
        if self.rage - 60 < 0:
            return 0
        else:
            self.rage -= 60
            return self.damage * 2


# second inherited class
class Wizard(Character):
    def __init__(self, name: str, health: int, damage: int, mana: int):
        super().__init__(name, health, damage)
        self.mana = mana
        # 2-dimensional list to hold spell names, the damage they deal, and their mana cost.
        self.spellList = [["Fireball", 10, 30], ["Lightning Bolt", 20, 15], ["Wind Gust", 40, 50]]

    # overridden methods
    def actions(self):
        print("1: Attack for " + str(self.damage) + " damage")
        print("2: Select a spell to cast")

    def castSpell(self, selectedSpell):
        selectedSpell = self.spellList[selectedSpell]
        if self.mana - selectedSpell[1] < 0:
            return 0
        else:
            self.mana -= selectedSpell[1]
            return selectedSpell[2]


# vars for looping
continueLoop = True
invalidChoice = True
usrChoice = 0
usrNum = 0


# Returns the definition of a word
def define_word(text: str) -> str:
    return Word(text).define()[0]


# Returns a list of all words passed through text parameter
def get_all_words_as_list(text: str) -> str:
    text = TextBlob(text)
    return text.words


# Returns a list of synonyms of a word
def get_synsets_for_word(text: str) -> str:
    return str(Word(text).synsets)


# Returns ngrams for the given text. The number of ngrams is also given by the user
def get_ngrams_for_text(text: str, ngrams: int) -> str:
    txt = TextBlob(text)
    return txt.ngrams(ngrams)


# Menu function
def menu_display():
    global invalidChoice
    invalidChoice = True
    while invalidChoice:
        try:
            print("1: Define a word.")
            print("2: Get all words entered as a list.")
            print("3: Get synsets for a word")
            print("4: Get ngrams for a word")
            # 5th option added for turn based battle
            print("5: Turn based battle")
            print("6: Exit")
            global usrChoice
            usrChoice = int(input("Please choose an option (1/2/3/4/5/6): "))
            if usrChoice > 6 or usrChoice < 1:
                print("Please enter a number between 1 and 6")
            else:
                invalidChoice = False
        except ValueError:
            print("Please enter an integer")


# turn-based battle takes place here
def battleLoop():
    # engine for text-to-speech
    engine = pyttsx3.init()

    weaponName = input("What is the name of your weapon?: ")

    # object creation
    warrior = Warrior("Warrior", 100, 20, 100, weaponName)
    wizard = Wizard("Wizard", 100, 10, 100)

    # List to store everything that will be written to a file
    actionList = []

    # print current battle-state
    print("Let the battle begin!")
    print()
    print("Warrior: " + "Health - " + str(warrior.health) + ", Rage - " + str(warrior.rage))
    print("Wizard: " + "Health - " + str(wizard.health) + ", Mana - " + str(wizard.mana))
    print()

    # Loop while both object's health are above 0
    while warrior.health > 0 and wizard.health > 0:
        print("Player's Turn!")
        warrior.actions()
        invalidActionChoice = True
        actionChoice = ""
        while invalidActionChoice:
            # input validation
            try:
                actionChoice = int(input("Select an action: "))
                if actionChoice == 1 or actionChoice == 2:
                    invalidActionChoice = False
                else:
                    print("Please enter either 1 for Attack or 2 for Cleave")
            except ValueError:
                print("Please enter an integer")

        # Determine what to say and add to actionList depending on choice entered by user
        if actionChoice == 1:
            wizard.health -= warrior.attack()
            action = "The Warrior attacked the Wizard for {0} damage with his {1}!".format(str(warrior.damage),
                                                                                           warrior.weaponName)
            print(action)
            actionList.append(action)
            engine.say(action)
            engine.runAndWait()
        elif actionChoice == 2:
            # Ensure that the warrior has enough rage to perform the action, else waste turn
            if warrior.rage >= 60:
                wizard.health -= warrior.castSpell("Cleave")
                action = "The Warrior Cleaved the Wizard for " + str(warrior.damage * 2) + " damage!"
                print(action)
                actionList.append(action)
                engine.say(action)
                engine.runAndWait()
            else:
                print("Not enough rage. Failed to cleave.")

        # Print battle-state
        print()
        print("Warrior: " + "Health - " + str(warrior.health) + ", Rage - " + str(warrior.rage))
        print("Wizard: " + "Health - " + str(wizard.health) + ", Mana - " + str(wizard.mana))
        print()

        # Check if wizard fell below zero health
        if wizard.health > 0:
            print("Enemy's Turn!")
            print("The enemy is thinking...")
            # Pause for 2.5 seconds for formatting reasons
            time.sleep(2.5)
            # Select a random number between 0 and 1 to determine the wizard's action
            enemyAction = randint(2)
            # say result and append to actionList
            if enemyAction == 0:
                warrior.health -= wizard.attack()
                action = "The Wizard attacked the Warrior for " + str(wizard.damage) + " damage!"
                print(action)
                actionList.append(action)
                engine.say(action)
                engine.runAndWait()
            else:
                # Generate a random number between 0 and 2 to select a spell to use
                wizardSpellChoice = randint(3)
                warrior.health -= wizard.castSpell(wizardSpellChoice)
                action = "The wizard cast {0} and damaged the warrior for {1} damage".format(
                    str(wizard.spellList[wizardSpellChoice][0]), str(wizard.spellList[wizardSpellChoice][2]))
                print(action)
                actionList.append(action)
                engine.say(action)
                engine.runAndWait()

            # print battle-state
            print()
            print("Warrior: " + "Health - " + str(warrior.health) + ", Rage - " + str(warrior.rage))
            print("Wizard: " + "Health - " + str(wizard.health) + ", Mana - " + str(wizard.mana))
            print()

    # Determine who won and add the result to the actionList
    if warrior.health <= 0:
        action = "The Wizard won the battle!"
        print(action)
        actionList.append(action)
        engine.say(action)
        engine.runAndWait()
    else:
        action = "The Warrior won the battle!"
        print(action)
        actionList.append(action)
        engine.say(action)
        engine.runAndWait()

    # Clear file of previous content
    f = open("BattleData.txt", "w")
    f.close()
    # Append all actions as new lines to file
    f = open("BattleData.txt", "a")
    for action in actionList:
        f.writelines(action + "\n")
    f.close()


# Loop for bringing user back to the menu
while continueLoop:

    menu_display()

    # if else for prompting user and selecting correct function
    invalidChoice = True
    if usrChoice == 1:
        usrText = input("Enter a word that you would like defined: ")
        usrText = usrText.strip()
        while invalidChoice:
            if " " in usrText:
                usrText = input("Please only enter a single word: ")
            else:
                definedWord = define_word(usrText)
                print(definedWord)
                invalidChoice = False
    elif usrChoice == 2:
        usrText = input("Please enter some words: ")
        while invalidChoice:
            if len(usrText) == 0:
                usrText = input("No words were entered, please enter some words: ")
            else:
                wordsEntered = get_all_words_as_list(usrText)
                print(wordsEntered)
                invalidChoice = False
    elif usrChoice == 3:
        usrText = input("Enter a word that you would like the synsets for: ")
        usrText = usrText.strip()
        while invalidChoice:
            if " " in usrText:
                usrText = input("Please only enter a single word: ")
            else:
                synsets = get_synsets_for_word(usrText)
                print(synsets)
                invalidChoice = False
    elif usrChoice == 4:
        usrText = input("Enter some text that you'd like the ngrams for: ")
        while invalidChoice:
            try:
                usrNum = int(input("Enter the number of ngrams you'd like: "))
                invalidChoice = False
            except ValueError:
                print("Invalid type entered")
        ngramsTxt = get_ngrams_for_text(usrText, usrNum)
        print(ngramsTxt)
    elif usrChoice == 5:
        battleLoop()
    else:
        quit()
    print()
