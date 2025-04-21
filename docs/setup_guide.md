# Detailed setup guide

## Disclaimer
You're not expected to have any programming knowledge or background to complete this guide since the process is simple and linear, but the guide itself will be long. Also, this was written on April of 2025 so things may have changed and look different on your end, but they should work in the same way

## Pre-requirements:
### Install Docker:
If you're on Windows or Mac you're defaulted to use Docker Desktop, but Linux users can choose to only install the Docker engine instead if you don't want the UI application

This process itself varies depending on your operating system, so please make sure to visit the [official Docker installation guide](https://docs.Docker.com/get-started/get-Docker/) and come back here once you're done

If you're on `Mac` or `Windows`, you will need to reboot your system after you install Docker

### Clone the repository:
If you know what `git` is and you have it installed simply run `git clone https://github.com/Schlvf/Twitch2Spotify.git`

If you don't have `git` please follow these steps:
1. Go to the main screen in the repository and click on the green button with the text `<> Code`
2. Click on `Download as zip`
3. Create a folder in your computer or server and decompress the zip file inside the folder

## Setup
### STEP 1 - The configuration file
Regardless of the deployment method you will choose later on, you must prepare a **`.env`** file that will help you set the basic configuration needed to run the project so start by creating a new file and name it `.env`

Once created copy and paste the example from below. We will be editing these values as we progress in the guide

#### Example of .env file

```conf
PORT = 8000
ENV = dev

redis_host = grimm-redis

sudo_auth = the_passcode_you_made
twitch_hmac_secret = the_passcode_you_made

twitch_app_id = your_twitch_app_id
twitch_app_secret = your_twitch_app_secret


spotify_app_id = your_spotify_app_id
spotify_app_secret = your_spotify_app_secret

ZROK_ENABLE_TOKEN = your_zrok_token
ZROK_UNIQUE_NAME = your_desired_subdomain

app_subdomain = https://{your_desired_subdomain}.share.zrok.io

# ssl_key_file = path_to_your_key.pem
# ssl_cert_file = path_to_your_cert.pem
```

This is a detailed breakdown of each configuration variable that our `.env` file must contain and its purpose:

|KEY|VALUE|
|-|-|
|**PORT**|This will be the port in which our web server will be running. You can default it to `8000` or any other available port of your choice. *(If you're planning to use  your own SSL certificates it must be **`443`** since that's the default HTTPS port)*|
|**ENV**|This defines the environment we're aiming to deploy to. It can be either **`dev`** or **`prod`**. Default it to `dev`. *(If you're planning to use your own SSL certificates it must be `prod`)*|
|**redis_host**|This corresponds to the connection string for our Redis. Default it to `grimm-redis`. *(If you're not using Docker you must change this accordingly to your Redis service host)*|
|**sudo_auth**|This will be a random passcode/string that we will create and need to send in our request header to access our protected API endpoints. For testing purposes, it is recommended to use something easy to remember|
|**twitch_app_id**|This will be the id corresponding to the Twitch App that we will create later on in the guide. For now leave it empty|
|**twitch_app_secret**|This is the secret of the app we mentioned above. For now leave it empty|
|**twitch_hmac_secret**|This will be a random passcode/string that we will create and use to authenticate the events that our webhook receives. Just make sure it is at least 12 characters long and don't use special symbols|
|**spotify_app_id**|This will be the id corresponding to the Spotify App that we will create later on in the guide. For now leave it empty|
|**spotify_app_secret**|This is the secret of the app we mentioned above. For now leave it empty|
|**ZROK_ENABLE_TOKEN**|This is the access token to our Zrok environment. For now leave it empty. *(If you're using your own SSL certificates you can skip everything involving Zrok and simply pass them to the web server directly)*|
|**ZROK_UNIQUE_NAME**|This will be the subdomain for the Zrok URL that you want to reserve. You can name it whatever you want but please note that if the name has been already claimed by another user you will need to change it. For example, if you reserve `toaster` as the name, the full URL will look like this: `https://toaster.share.zrok.io`|
|**app_subdomain**|This will be the full URL that we will be exposing to the internet. Default it to the Zrok URL from above and replace your reserved subdomain|
|**ssl_key_file**|*(Optional)* This must be the path to your SSL key file|
|**ssl_cert_file**|*(Optional)* Same as above, but with the cert file|

You can leave empty the `ssl_key_file` and `ssl_cert_file` if you're using Zrok

#### Now lets make the first changes to the config file

For `sudo_auth` and `twitch_hmac_secret` we need to make a passcode composed of only alphabet letters and numbers with at least 12 characters in total\
If you want some help creating secure passcodes you can use a generator like [LastPass](https://www.lastpass.com/features/password-generator) but make sure that you **disable symbols** so it doesn't include any special characters

If you did everything correctly, the new values in your `.env` file should look like this:

```config
...

sudo_auth = HqN128DFCaT4
twitch_hmac_secret = 7ZsSx5hm12v7

...
```

### STEP 2 - Setting up Zrok:
#### *(If you have your own domain and SSL certificates you can skip this step)*

Both the Twitch and Spotify APIs require you to be able to expose the webhook on a static HTTPS domain\
This can be achieved by owning your own web domain and SSL certificates, or in this case, by using a web tunneling tool like Zrok

The reason why Zrok was chosen over all the other available options is because it was the most suitable for our specific use case as it allows you to have a reserved domain with certificates for free and it is highly compatible with Docker environments\
The only downside of Zrok is that you can only transfer 5Gb of data daily, but this is something that shouldn't be an issue since we will be making and receiving simple HTTP requests and you would need hundreds of thousands of them to reach that limit

1. The first thing you must do is visit the [official Zrok website](https://zrok.io/) and creating your account\
You can do this by clicking on `Get started` and then clicking on `Account`

2. Once you've created your account, you'll receive a verification email. Just go to your inbox and follow the steps in said message

3. Now you should have access to both the [Zrok dashboard](https://myzrok.io/dashboard) and the [Zrok API web console](https://api.zrok.io/) so let's start by visiting the web console

4. In the web console you will have a tab that will display your `Environments` that should be empty, and right next to it there should be a tab called `Detail`. Once you've found it, click on it and then reveal and copy the `Token` right under your email and replace it in the `.env` file\
Example: `ZROK_ENABLE_TOKEN = L18IWW083N6`


5. Now you need to define the unique subdomain name that you want. This will be reflected in the URL that you will use to access the tool dashboard.\
For instance, if the name you choose is `toaster`, the URL that Zrok gives you will be `https://toaster.share.zrok.io`\

**Before you move to the next step please make sure that the subdomain name meets the following criteria:**

- It should be at least 10 characters
- It uses only alphabet letters and numbers, special characters can be problematic
- Since it must be unique you can add your user name at the end to reduce the chances that somebody already took it

*The guide will use `toaster` for the following examples but you should make sure to follow the criteria from above in your subdomain name*

6. Once you defined the subdomain name, assign it to the key `ZROK_UNIQUE_NAME` in the `.env` file\
Example: `ZROK_UNIQUE_NAME = toaster`

7. Finally, copy and replace the previous name in the following URL's subdomain:\
`https://{your_name_goes_here}.share.zrok.io`\
Now assign the new URL to the key `app_subdomain` in the `.env` file\
Example: `app_subdomain = https://toaster.share.zrok.io`

If you did everything correctly, the new values in your `.env` file should look like this:

```config
...

ZROK_ENABLE_TOKEN = L18IWW083N6
ZROK_UNIQUE_NAME = toaster

app_subdomain = https://toaster.share.zrok.io

...
```

### STEP 3 - Setting up Twitch:
We need to create a Twitch App in the Twitch developer portal and update our `.env` file accordingly

1. Visit the [Twitch developer portal](https://dev.twitch.tv/) and log into your account
2. Once logged in, click on the `Your console` button at the top right
3. Click on the `Register your application` button at the top right
4. Fill the fields with the following information and then click on `Create`:

|Field|Value|
|-|-|
|Name|Just give it a name of your preference like `MusicApp`|
|OAuth Redirect URLs|Copy and paste the Zrok URL making sure that you replace the subdomain with the one you intended to reserve and you add at the end `/eventsub/auth`. *(This can be updated later)*. Example: `https://toaster.share.zrok.io/eventsub/auth`|
|Category|Select `Application Integration`|
|Client Type|Select `Confidential`|

5. Once created you will be able to see it in your console page, so now click on `Manage`
6. Copy the `Client id` and replace it in the `.env` file\
Example: `twitch_app_id = n5b7yckjnriy10vrl9bu6l804cyj`
7. Click on `New secret` to generate a new secret, then copy it and replace it in the `.env` file\
Example: `twitch_app_secret = tx6wm3rkfebg6u4cyvisx2935nl`

If you did everything correctly, the new values in your `.env` file should look like this:

```config
...

twitch_app_id = n5b7yckjnriy10vrl9bu6l804cyj
twitch_app_secret = tx6wm3rkfebg6u4cyvisx2935nl

...
```

### STEP 4 - Setting up Spotify:
We need to create a Spotify App in the Spotify developer portal and update our `.env` file accordingly

1. Visit the [Spotify developer portal](https://developer.spotify.com/) and log into your account
2. Once logged in, click on your profile photo in the top right and then click on `Dashboard`
3. Click on the `Create app` on the right
4. Fill the fields with the following information:

|Field|Value|
|-|-|
|App name|Just give it a name of your preference like `MusicApp`|
|App description|Give it a brief description, it can be whatever|
|Website|It's optional so we can leave it empty|
|Redirect URIs|Copy and paste the Zrok URL making sure that you replace the subdomain with the one you intended to reserve and you add at the end `/spotify/auth`. *(This can be updated later)*. Example: `https://toaster.share.zrok.io/spotify/auth`|
|Which API/SDKs are you planning to use?|Do not check any of the checkboxes|

5. Check the **Terms of service** checkbox and click on `Save`
6. Once created you will be able to see it in your dashboard page, so now click on it
7. Copy the `Client id` and replace it in the `.env` file\
Example: `spotify_app_id = n5b7yckjnriy10vrl9bu6l804cyj`
8. Click on `View client secret` copy it and replace it in the `.env` file\
Example: `spotify_app_secret = tx6wm3rkfebg6u4cyvisx2935nl`
9. Now locate the tab called `User management` and click on it
10. In the `User management` tab fill the `Full name` field with your user name and the `Email` field with the email associated to your own Spotify account and finally click on `Add user`
11. *(Optional)* If you plan to host the tool for multiple Spotify accounts, you must repeat the previous step with their corresponding details. Keep in mind that the limit is 25

If you did everything correctly, the new values in your `.env` file should look like this:

```config
...

spotify_app_id = n5b7yckjnriy10vrl9bu6l804cyj
spotify_app_secret = tx6wm3rkfebg6u4cyvisx2935nl

...
```

### STEP 5 - Building and running the tool
Assuming all the steps from above were completed, all you have to do is run the following Docker command in your terminal:\
`docker compose --profile zrok up -d`

This command will be all you need to start the project once again in case you shut down Docker

<details>
<summary><b>Click here if you're on a Windows computer and have no idea what a terminal is</b></summary>

The equivalent to a terminal on Windows would be a `cmd` or `powershell` window. I personally prefer powershell but cmd will work the same

To open a terminal in our project open in the file explorer the folder where you cloned or unzipped the repository, then hold `shift` and `right click` on a empty space and you should be able to find an option called `Open powershell window here`, so go ahead and click it

Once the powershell or cmd window is open, simply copy and paste the command from above, and assuming that you installed Docker correctly, everything should work
</details>

#### For Windows users only

When you installed Docker Desktop, it will use by default something called `WSL` (Windows Subsystem for Linux) that basically performs some "computer magic" so Docker can work

The `WSL` engine will reserve some of the resources from your computer to run Docker, and in some instances it can reserve more than you actually need, but this shouldn't be a problem since you should be able to find an app called `WSL settings` already installed that gives you the opportunity to limit the amount of cores and memory that you want WSL to use

The project itself was designed so it can run in a potato so don't be afraid to limit the `processor count` and `memory size` to the lowest value that your settings allow

If you're still unhappy with the results and feel like `WSL` consumes way too many resources you can go to your `Docker Desktop` app settings and uncheck the `Use the WSL 2 based engine` option which will default to the barebones `Hyper-V` engine that uses resources on demand

You may have to manually enable the `Hyper-v` engine before you can use Docker again, so make sure to [visit the following guide by Microsoft](https://learn.microsoft.com/en-us/Windows-server/virtualization/hyper-v/get-started/install-hyper-v?pivots=Windows#enable-the-hyper-v-role-through-settings) where they explain how to enable and install it on your machine

When the tool was tested on a Windows machine running in the background it averaged 105MB of memory and 0.1% of core usage which is negligible, however, if you plan to host it for multiple people, it is highly advisable to consider renting a cheap virtual machine so it can be available for everybody 24/7

I deployed this exact same project in the cheapest Digital Ocean droplet available, which only cost me $4 usd/month and I never had to worry about resources on my pc or having to leave it turned on so my friends could use the tool while I'm not home

### Having issues?

In case you've never used Docker before, the following commands will help you navigate through docker, see logs, rebuild the project or delete everything

|Command|What it does|
|-|-|
|**docker ps -a**|This will allow you to see all the containers and their ids even if they're not running|
|**docker stop `container_id`**|This will allow you to stop any running container|
|**docker logs -f -t `container_id`**|This will let you see the console logs(*stdout*) of your container in real time|
|**docker stats**|This will let you see the resources used by your containers in real time|
|**docker system prune**|This will let you delete **all** the unused or stopped containers/images to free space, therefore, **use with caution**|
|**docker volume prune -a**|This will let you delete **all** the unused volumes in your docker engine, therefore, **use with caution**|
|**docker compose --profile zrok up -d --build**|This will let you rebuild and rerun the entire project in case you made changes to the source code or the config file|

In case you're experiencing problems with Zrok you may need to re-create the volume with the new `.env` file configuration, so make sure you stop all the containers first, then you delete all the containers, and finally you delete the volume\
**If attempt to delete the docker volumes but you don't follow the order specified above, Docker won't let you delete the volume that contains your old Zrok configuration so the new Zrok values in the `.env` file won't take effect**
