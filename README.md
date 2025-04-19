# Twitch2Spotify
This is a small project that attempts to create a seamless communication between both Twitch and Spotify APIs. The main goal is to allow users to add a song to a Spotify client through Twitch channel point redemptions

## Disclaimer
This tool began as a self-learning and hobby project, born out of curiosity. It was never intended for commercial use or mass distribution, but rather as a way to experiment, learn, and share something that may be useful to somebody else in the community

***I do not endorse or encourage the use of this integration for streaming DMCA protected content with the intention of profiting***

Any misuse of the tool is your sole responsibility as the user, and by using it you agree to comply with all applicable rules in both the Twitch and Spotify terms of service

## How does it work?
At a high level, the tool consists of a simple API made in Python to expose an endpoint that will act as a webhook for Twitch events. Said events come from a free subscription-based service offered by Twitch called [EventSub](https://dev.twitch.tv/docs/eventsub/) that will let us know when a specific action takes place

In this particular case, we will create and then listen to a custom channel point redemption called `Spotify song request` that allows a Twitch chatter to provide a Spotify song URL embedded in their message in exchange for a determined Twitch channel point amount, and we will use that same URL to append said song to the target's song queue using [Spotify's API](https://developer.spotify.com/documentation/web-api)

### TL;DR
The tool listens to Twitch so when a chatter uses a determined channel point redemption, it lets Spotify know that a song should be added to the queue

## Limitations

1. **You must have a premium Spotify account**\
The free Spotify plan is subject to multiple restrictions that will interfere with the tool, this is why a premium subscription is needed. However, please note that any premium plan will work. You can find more details about the plans in the [official Spotify plans page](https://www.spotify.com/co-en/premium/)

2. **You must be Twitch affiliate or partner**\
In the current state of the project we use channel point redemptions to allow chatters to send in their song requests, and in order to be able to have access to channel points in your channel you must be at least a Twitch affiliate. In case you're not familiar with the program, please visit the official Twitch article on [How to become an affiliate](https://help.twitch.tv/s/article/joining-the-affiliate-program) that will walk you through the requirements and steps to become one

3. **You must have a machine to host the tool**\
It can be in your own PC or on a server but the tool needs somewhere to run. To make this process more user-friendly the project was developed with [Docker](https://www.docker.com/) in mind, so it can be easy to host regardless of the platform and operating system you're working on

4. **The tool can be hosted for up to 25 different Spotify accounts**\
Given that the project revolves around self-hosting, our tool will use the [development quota mode](https://developer.spotify.com/documentation/web-api/concepts/quota-modes) that Spotify offers, which allows up to 25 unique Spotify accounts to use the tool simultaneously.\
It is possible to increase said limit but you would have to apply for the extended mode following Spotify's guidelines and since this is out of the project's scope and it's subject to changes, it will not be explained in this guide

## How to setup the tool

[**Please click here to visit the setup guide**](docs/setup_guide.md)

## How to use the tool

[**Please click here to visit the user guide**](docs/usage_guide.md)

## For developers

As the creator of the project I have no plans of implementing new features given that the main goal was already achieved but I will do my best to maintain it functional. Nonetheless, feel free to fork, modify, and build upon it as long as it is done under the same license **(GPL-3.0)** and with proper attribution

## How to contribute

### 1. Reporting a problem
If you found something broken please feel free to create an issue so it can be looked into, but make sure that your report includes the following details:

|Field|Description|
|-|-|
|**Type**|A brief description that classifies the issue. Example: `Bug`, `Security`, `Performance`, ...|
|**Description**|A detailed description of the issue itself. The more specific and descriptive, the better|
|**Steps to replicate**|A detailed description on how to replicate said issue. You can include photos if needed|
|**Logs** (Optional)|Including the console logs would be really helpful to facilitate debugging so make sure to add them if the issue is an unhandled exception|

### 2. Creating a pull request

My code isn't the best, so if you would like to improve it here are some general rules to follow if you plan to add your own:

- Do not change code unrelated to your pull request (including style fixes)
- Make sure to use `Black` for Python and `Prettier` for static files as your formatters
- Make sure to use the `pre-commit` hooks to sanitize even further the code
- Include reasoning behind the change in the pull request description, focusing on why the change is being made
- Refer to issues (such as Fixes [`Bug #1234`] or Implements [`Feature #5678`]), or discussions to further back up the changes
- Keep things simple, organized, and readable
- As I said earlier, my code isn't the best, but please do not create a massive code refactor in a single pull request. If you plan to rebuild a big portion of the code please consider forking the project or submitting the changes progressively in small implementations

<details>
<summary><b>Click here to know how to install and use the hooks</b></summary>

If you plan on editing and contributing code, it is highly recommended to use the pre-commit hooks. This is particularly useful to ensure a consistent code style, making it more readable and maintainable:

1. Install pre-commit so the linting hooks can be executed before submitting changes to the repo. \
`pre-commit install`

2. Update the hooks to their latest version to ensure compatibility:\
`pre-commit autoupdate`

3. **(Optional)** Once you've made any changes, you can simply use `git add .` to stage the changes and then you can manually run the hooks by using:\
`pre-commit run --all-files`
</details>

### 3. Maintaining the documentation

The entire documentation of the project lies in what you're currently reading, so any contributions will be welcomed

## Guide to deploy locally:
> [!IMPORTANT]
> Please note that this project was developed and tested on **Python 3.13.2**. I can't ensure compatibility with previous or newer versions since there may be conflicts with the PyPI dependencies, therefore you will need to update them manually as needed

### Requirements
To test and run everything locally, all you need to have is Docker installed and run the compose file, however, you can run everything separately by having Python, Nodejs, Redis and the Zrok CLI tool in your environment

<details>
<summary><b>Click here to see the breakdown of each requirement</b></summary>

|Requirement|Usage|
|-|-|
|Python|Both the webhook and the web server are implemented in Python using the FastAPI framework and Uvicorn respectively|
|Nodejs|To facilitate the usage of the tool, the web server provides a simple UI using Jinja2 templates. Said templates are a combination of basic HTML, CSS and JS static files and in order to improve performance the project uses Parcel to bundle the static files|
|Redis|We use Redis as a temporary resilient storage of data such as access tokens and to cache the events we receive, allowing us to identify duplicates|
|Zrok|This tool is completely optional but highly recommended given that it provides you with a free static URL that is exposed to the internet that will act as an entry point to allow communication through the HTTPS protocol with the webhook through a web tunnel
</details>

### Deployment
Assuming you've already created the .env file simply follow these steps

#### API setup and usage

1. Create a virtual environment: *(In this particular case I'll name it **venv**)*\
`python -m venv venv`

2. Activate the virtual environment:\
`~/venv/scripts/activate`

3. Install the basic requirements: *(Please note that installing the **requirements-dev.txt** will also install **requirements.txt** but they're split in 2 different files to minimize the potential docker image size and unwanted packages for production releases)*\
`pip install -r requirements-dev.txt`

4. **(Optional)** You can update pip by using:\
`python.exe -m pip install --upgrade pip optional`

5. Run the web server: *(Make sure that you bundled the static files, the Redis service is running on the default port before running the API or things won't work as intended)*;\
`python ~/src/main.py`

#### Parcel setup and usage
1. Install the Node dependencies:\
`npm install .`

2. Bundle the project: *(This will create a folder named `dist` with the minified version of all the static files that will be served)*\
`npm run build`

3. You can also serve the static files separately by running the following command:\
`npm start`\
And to access the templates simply visit `localhost:5000/{the_name_of_the_template}`

#### Zrok setup and usage
1. Create a Zrok account and install the Zrok CLI tool:\
For that you must follow the [official Zrok installation guide](https://docs.zrok.io/docs/guides/install/)

2. Take your user token from the Zrok web dashboard and enable your environment:\
`zrok enable {your_token}`

3. Reserve your static subdomain:\
`zrok reserve public {the_host_of_your_api} --unique-name {the_subdomain_you_want}`

4. Enable the tunnel with the reserved domain:\
`zrok share reserved {the_reserved_subdomain}`\
\
If you experience any issues with these steps, make sure to check the [official Zrok documentation](https://docs.zrok.io/docs/getting-started)

#### Redis setup
The installation of Redis varies depending on your operating system so please make sure to check their [official documentation](https://redis.io/docs/latest/operate/oss_and_stack/install/) for your specific machine
