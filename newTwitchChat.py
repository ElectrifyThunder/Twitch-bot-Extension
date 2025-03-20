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
#Go here to see the entire Documentation on how to set it up ()

TARGET_CHANNEL = dontlook.TARGET_CHANNEL
CLIENT_SECRET = dontlook.CLIENT_SECRET
CLIENT_ID = dontlook.CLIENT_ID
USER_SCOPE = dontlook.USER_SCOPE

twitchUsersDoc = "twitchUsers.txt" #Replace with your save data here 

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
        "Apple": 5,
        "Banana": 30,
    }

setupTwitch.setchatControl(setupTwitch,False)

#Logic Main

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
        #Checks if they can buy the product?
        item_price = int(shopPurchase.shopItems[cleaned_text])
        myBalance = int(await checkBalance(msg))

        if myBalance >= item_price: 
            #User buys the product!
            newBalance = myBalance - item_price
            await changeBalance(msg,newBalance)
            updatedBalance = int(await checkBalance(msg))
            await msg.reply(f"You've purchased: {item_price} your bank is now {updatedBalance} ")
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

    #Logic here
    print(f"{msg.user.display_name} - {msg.text} {msg.user.id}")

async def changeBalance(msg, changeTo): #Change a users balance
    # Ensure the file exists
    try:
        if not os.path.exists(twitchUsersDoc):
            open(twitchUsersDoc, "w").close()  # Create an empty file

        # Read all lines in the file and update the relevant entry
        updated_lines = []
        user_found = False  # To track if the user ID is found
        
        with open(twitchUsersDoc, "r") as file:
            for line in file:
                parts = line.split()
                if len(parts) >= 5:  # Ensure line has the expected format
                    username = parts[0]
                    currency = parts[2]
                    myID = parts[4]

                    if myID == str(msg.user.id):  # Match user ID
                        user_found = True
                        updated_line = f"{username} Currency: {changeTo} ID: {myID}\n"
                        updated_lines.append(updated_line)  # Update this line
                        print(f"Updated {username}'s balance to {changeTo}")
                    else:
                        updated_lines.append(line)  # Keep the line unchanged
                else:
                    updated_lines.append(line)  # Keep malformed lines unchanged
        
        # If user not found, optionally add the user as a new entry
        if not user_found:
            new_entry = f"{msg.user.name} Currency: {changeTo} ID: {msg.user.id}\n"
            updated_lines.append(new_entry)
            print(f"Added new entry for {msg.user.name} with balance {changeTo}")

        # Write updated lines back to the file
        with open(twitchUsersDoc, "w") as file:
            file.writelines(updated_lines)

    except Exception as e:
        print(f"Error: {e}")

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
    try:
        myBalance = int(await checkBalance(msg))
        amountToGamble = int(msg.text.replace("!gamble", "").strip())
        winnings = 0

        if amountToGamble > 0:
                amountToGamble = int(amountToGamble)
                row = spinNow()
                payout = getPayout(row, amountToGamble)
            #Payout the user
                if payout == 0:
                    winnings = myBalance - amountToGamble
                    await msg.reply(f"YOU LOST THE GAMBLE - {amountToGamble}(RESULT: {row})")
                elif payout > 0:
                    winnings += payout
                    await msg.reply(f"YOU WON THE GAMBLE + {payout} (RESULT: {row})")
                
                if winnings < 0:
                    winnings = 0

                await changeBalance(msg,winnings)

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
    symbols = ["🔥","🎮","🔔","⭐"]
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
        
    elif row[1] == row[2]:
        if row[1] == "🔥":
            return bet * 2
        elif row[1] == "🎮":
            return bet * 3
        elif row[1] == "🔔":
            return bet * 4
        elif row[1] == "⭐":
            return bet * 5
        
    elif row[0] == row[1]:
        if row[1] == "🔥":
            return bet * 1
        elif row[1] == "🎮":
            return bet * 2
        elif row[1] == "🔔":
            return bet * 2
        elif row[1] == "⭐":
            return bet * 3
        
    return 0

async def checkPing(msg:ChatMessage):
    start_time = time.monotonic()
    end_time = time.monotonic()
    response_time = (end_time - start_time) * 1000
    await msg.reply(f"PONG! ({response_time} ms)")


async def run_bot():
    #Setup Main Bot:
    bot = await Twitch(CLIENT_ID,CLIENT_SECRET)
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