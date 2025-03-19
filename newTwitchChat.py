#ElectrifyThunder
#This program connects to your Twitch channel
#You're able to create commands, execute them, etc.

#Date Created: 3/17/2025

#Services
from twitchAPI.chat import Chat,EventData,ChatMessage,ChatSub,ChatCommand
from twitchAPI.type import AuthScope,ChatEvent
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.twitch import Twitch
import asyncio
import random
import keyboard
import threading
import time
import os
import requests
import aiohttp

import dontlook #Hidden secrets to not show

#Secrets and Descriptions (Replace these with your channel descriptions and secrets)
TARGET_CHANNEL = dontlook.TARGET_CHANNEL
APP_SECRET = dontlook.APP_SECRET
USER_SCOPE = dontlook.USER_SCOPE
Client_ID = dontlook.Client_ID
Access_Token = dontlook.Access_Token
APP_SECRET = dontlook.APP_SECRET
APP_ID = dontlook.APP_ID
twitchUsersDoc = "twitchUsers.txt"

#Begin Body
class setupTwitch(): #Main Bot Functions
    def __init__(self):
        self.broadCasterID = None
        self.userID = None
        self.controlActive = False
    
    def setBroadCasterID(self,ID):
        self.broadCasterID = ID
    def setuserID(self,ID):
        self.userID = ID
    def setchatControl(self,bool):
        self.controlActive = bool

    def getChatControl(self):
        return self.controlActive
    def getBroadCasterID(self):
        return self.broadCasterID

class keyboardInteraction(): #Chats Control Keyboard
    async def __init__(self):
        pass

    async def jump(msg:ChatCommand):
        await keyPress("Space",msg)
    async def moveForward(msg:ChatCommand):
        await keyPress("w",msg)
    async def moveLeft(msg:ChatCommand):
        await keyPress("a",msg)
    async def moveBackwards(msg:ChatCommand):
        await keyPress("s",msg)
    async def moveRight(msg:ChatCommand):
        await keyPress("d",msg)

class shopPurchase(): #My Channels Shop Interface
    async def __init__(self):
        pass

    shopItems = {
        "Apple": 20,
        "Banana": 30,
    }

class userBank(): #The chatters data globally
    async def __init__(self):
        self.Money = None 
        self.Health = None
        self.Name = None
        self.userItems = None

    def getuserMoney(self):
        return self.Money
    def getuserHealth(self):
        return self.Health
    def getuserName(self):
        return self.Name
    def getuserItems(self):
        return self.userItems
    
    def setuserMoney(self,money):
        self.Money = money
    def setuserHealth(self,health):
        self.Health = health
    def setuserName(self,Name):
        self.Name = Name
    def setuserItems(self,item):
        self.userItems = item

setupTwitch.setchatControl(setupTwitch,False)
userBank.setuserMoney(userBank,100)
userBank.setuserHealth(userBank,100)

#Logic Main
userItems = []

#Fun and interesting commands
async def keyPress(key,msg:ChatCommand): #KeyPresser
    if setupTwitch.getChatControl(setupTwitch):
        amountKeys = 3 #Amount of times it'll press.
        for count in range(0, amountKeys):
            keyboard.press(key)
            await asyncio.sleep(0.2)
        keyboard.release(key)

async def chatControls(msg:ChatMessage): #activate chat control commands
    isBroadCaster = 'broadcaster' in msg.user.badges and msg.user.badges['broadcaster'] == '1'

    if msg.user.mod or isBroadCaster: 
        setupTwitch.setchatControl(setupTwitch,not setupTwitch.getChatControl(setupTwitch))
        if setupTwitch.getChatControl(setupTwitch):
            await msg.reply("CHAT CONTROL IS NOW ACTIVE")
        else:
            await msg.reply("CHAT CONTROL IS NOT ACTIVE")

async def userBuyItem(msg:ChatMessage): #Shop Service
    cleaned_text = msg.text.replace("!buy","").strip()

    if cleaned_text in shopPurchase.shopItems:
        #Sell the item to the buyer
        item_price = shopPurchase.shopItems[cleaned_text]

        if userBank.getuserMoney(userBank) >= item_price: 
            userBank.setuserMoney(userBank,userBank.getuserMoney(userBank) - item_price)

            #Add items to the user profile
            userItems.append(cleaned_text)
            userBank.setuserItems(userBank,userItems)

            #Announce the user
            await msg.reply(f"You've purchased: {item_price} your bank is now {userBank.getuserMoney(userBank)} ")
        else:
            await msg.reply(f"You don't have enough for the item {cleaned_text}..")

    else:
        await msg.reply(f"Sorry, but {cleaned_text} is not in the shop!")

async def pickRandomNumber(cmd:ChatCommand): #Number Picking!
    user = cmd.user
    cleaned_text = int(cmd.text.replace("!picknumber","").strip())

    pickedRandom = random.randint(0,cleaned_text)

    if pickedRandom == cleaned_text:
        await cmd.reply(f"YOU TIED THE NUMBER {user.display_name}")
    else:
        await cmd.reply(f"Your random number is {pickedRandom}")

async def cmdRollChance(cmd:ChatCommand): #Gambling Roll Chance
    user = cmd.user
    chanceRoll = random.randint(0,100)
    await cmd.reply(f"Here's your roll num {chanceRoll}")



#Main functions to run the bot
async def on_ready(ready_event:EventData): #Bot successfully joins the channel!
    await ready_event.chat.join_room(TARGET_CHANNEL)
    print("Bot has joined the channel.")

async def on_message(msg:ChatMessage): #Main send logic
    #Set main ID's
    if msg.user.display_name == TARGET_CHANNEL:
        setupTwitch.setBroadCasterID(setupTwitch,msg.user.id)
    else:
        setupTwitch.setuserID(setupTwitch,msg.user.id)
    
    #Set user global data
    userBank.setuserName(userBank,msg.user.display_name)

    #Logic here
    print(f"{msg.user.display_name} - {msg.text} {msg.user.id}")

async def checkBalance(msg: ChatMessage):
    # Get user's balance
    user = msg.user
    defaultBalance = 10  # Default balance value

    try:
        # Ensure the file exists; create if it doesn't
        if not os.path.exists(twitchUsersDoc):
            open(twitchUsersDoc, "w").close()  # Create an empty file

        user_found = False
        user_balance = None

        # Read the file to check if the user exists
        with open(twitchUsersDoc, "r") as file:
            lines = file.readlines()

        for line in lines:
            if not line.strip():  # Skip empty lines
                continue

            # Parse line into its components
            parts = line.split()
            username = parts[0]
            currency = parts[2]
            myID = parts[4]

            if myID == user.id:  # Check for an existing user match
                user_found = True
                user_balance = currency
                break

        # If the user doesn't exist, append them to the file
        if not user_found:
            with open(twitchUsersDoc, "a") as file:  # Open in append mode
                file.write(f"{user.name} Currency: {defaultBalance} ID: {user.id}\n")
            user_balance = defaultBalance  # Assign the default balance

        return user_balance

    except Exception as e:
        print(f"Error found: {e}")
        return None


async def gambling(msg: ChatMessage):  # Gamble Machine Here
    await checkBalance(msg)

    user = msg.user
    amountToGamble = msg.text.replace("!gamble", "").strip()

    if amountToGamble:
        try:
            lines = []
            user_found = False
            amountToGamble = int(amountToGamble)

            if not os.path.exists(twitchUsersDoc):
                open(twitchUsersDoc, "w").close()  # Create an empty file

            # Read all lines from the file
            with open(twitchUsersDoc, "r") as file:
                lines = file.readlines()

            # Process each line to update user's balance if found
            updated_lines = []
            for line in lines:
                if not line.strip():  # Skip empty lines
                    continue

                # Parse line into its components
                parts = line.split()
                username = parts[0]
                currency = int(parts[2])
                myID = parts[4]

                if myID == user.id:
                    user_found = True

                    if currency <= 0:
                        currency = random.randint(1, 100)
                    
                    #Gamble Machines Result
                    row = spinNow()
                    payout = getPayout(row, amountToGamble)

                    #Payout the user
                    if payout == 0:
                        currency -= amountToGamble
                        await msg.reply(f"YOU LOST THE GAMBLE - {amountToGamble} (new Balance {currency} ) (RESULT: {row})")
                    elif payout > 0:
                        currency += payout
                        await msg.reply(f"YOU WON THE GAMBLE + {payout} (new Balance: {currency}) (RESULT: {row})")

                    updated_line = f"{user.name} Currency: {currency} ID: {user.id}\n"
                else:
                    updated_line = line  # Keep the original line if not the user
                
                updated_lines.append(updated_line)

            # If the user was not found, add them to the file
            if not user_found:
                new_user_line = f"{user.name} Currency: {10} ID: {user.id}\n"
                updated_lines.append(new_user_line)

            # Write back all the updated lines to the file
            with open(twitchUsersDoc, "w") as file:
                file.writelines(updated_lines)

        except Exception as e:
            print(f"Error found: {e}")


async def sendBalance(msg:ChatMessage):
    myMoney = await checkBalance(msg)
    if int(myMoney) > 0:
        await msg.reply(f"YOUR BALANCE IS: {myMoney}")
    elif int(myMoney) <= 0:
        await msg.reply(f"YOU ARE BROKE.")


async def lurkCommand(cmd:ChatCommand): #Lurking User
    lurkChances = ["Thanks For Lurking!", "See you later... :(", "BYE!"]
    pickLurk = random.choice(lurkChances)
    await cmd.reply(pickLurk)

def spinNow():
    symbols = ["🔥","🎮","🔔","⭐","🩸"]
    return [random.choice(symbols) for symbol in range(3)]

def getPayout(row,bet):
    print(row)

    if row[0] == row[1] == row[2]:
        if row[0] == "🔥":
            return bet * 3
        elif row[0] == "🎮":
            return bet * 4
        elif row[0] == "🔔":
            return bet * 5
        elif row[0] == "⭐":
            return bet * 10
        elif row[0] == "🩸":
            return bet - 6
        
    elif row[1] == row[2]:
        if row[1] == "🔥":
            return bet * 2
        elif row[1] == "🎮":
            return bet * 3
        elif row[1] == "🔔":
            return bet * 4
        elif row[1] == "⭐":
            return bet * 5
        elif row[1] == "🩸":
            return bet - 3
        
    elif row[0] == row[1]:
        if row[1] == "🔥":
            return bet * 1
        elif row[1] == "🎮":
            return bet * 2
        elif row[1] == "🔔":
            return bet * 2
        elif row[1] == "⭐":
            return bet * 3
        elif row[1] == "🩸":
            return bet - 2
        
    return 0

async def checkPing(msg:ChatMessage):
    start_time = time.monotonic()
    end_time = time.monotonic()
    response_time = (end_time - start_time) * 1000
    await msg.reply(f"PONG! ({response_time} ms)")


async def run_bot():
    #Setup Main Bot:
    bot = await Twitch(APP_ID,APP_SECRET)

    auth = UserAuthenticator(bot,USER_SCOPE)
    token,refresh_token = await auth.authenticate()
    await bot.set_user_authentication(token,USER_SCOPE,refresh_token)

    chat = await Chat(bot)

    #Register Events:
    chat.register_event(ChatEvent.READY,on_ready)
    chat.register_event(ChatEvent.MESSAGE,on_message)

    #Regular Commands:
    chat.register_command("keycontrol",chatControls)
    chat.register_command("lurk",lurkCommand)

    #viewer key commands - Controls My Computer:
    chat.register_command("jump",keyboardInteraction.jump)
    chat.register_command("right",keyboardInteraction.moveRight)
    chat.register_command("left",keyboardInteraction.moveLeft)
    chat.register_command("backwards",keyboardInteraction.moveBackwards)
    chat.register_command("forward",keyboardInteraction.moveForward)

    #ShopList
    for index in range(len(shopPurchase.shopItems)):
        itemName = list(shopPurchase.shopItems.keys())[index]
        chat.register_command(f"buy{itemName}",userBuyItem)

    #Fun Commands
    chat.register_command("picknumber",pickRandomNumber)
    chat.register_command("roll",cmdRollChance)
    chat.register_command("gamble",gambling)
    chat.register_command("balance",sendBalance)
    chat.register_command("myping",checkPing)
    
    #Main Start
    chat.start()

    try:
        input("") #Final run string
    finally:
        chat.stop()
        await bot.close()

asyncio.run(run_bot())