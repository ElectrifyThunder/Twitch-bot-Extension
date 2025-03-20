IN ORDER TO USE THIS BE SURE TO ADD YOUR OWN IDs:

CLIENT_ID = "YOUR CLIENT ID"
CLIENT_SECRET = "YOUR CLIENT SECRET"
TARGET_CHANNEL = "YOUR CHANNEL"

USER_SCOPE = [AuthScope.CHAT_READ,AuthScope.CHAT_EDIT,AuthScope.CHANNEL_MANAGE_BROADCAST]

TUTORIAL:

1) Go To Twitch Developers
https://dev.twitch.tv
2) Create a new Application
![image](https://github.com/user-attachments/assets/432f74e0-a418-49d7-8b5c-15238c06da07)

3) Rename OAuth Redirect URLs to http://localhost:17563 and click ADD
![image](https://github.com/user-attachments/assets/b7a48fe9-4d1c-4f47-bcc7-0f4cec20c5de)

4) Get your CLIENT_ID
![image](https://github.com/user-attachments/assets/509421a6-8856-47ca-a30f-661306f2a59d)
CLIENT_ID = "[YOUR CLIENT ID]" - Rename to whatever your client ID is

6) Click New Secret & copy that
APP_SECRET = "[YOUR APP SECRET]" - Rename whatever your App Secret is

7) Done? Congrats, now paste your channel name in the TARGET_CHANNEL It'll look like this
TARGET_CHANNEL = "[YOUR CHANNEL]"

