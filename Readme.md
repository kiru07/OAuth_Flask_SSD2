# Flask - GitHub - OAuth Application


An application to demonstrate OAuth2 flow using GitHub as the OAuth resource and authorization provider.

---

## Project Setup

* Requirements:
  - *Python* version *3.7* or higher
  - Assuming *Windows 10* OS used for setup. (Please refer to official python documentation for *Linux/MacOS* commands)

* Create virtual environment to install dependencies

        python -m venv Flask_OAuth_App

    - Creates a directory called *Flask_OAuth_App* which will host the virtual environment, and our project files

* Activate virtual environment:

        > cd \Flask_OAuth_App
        > Scripts\activate.bat


> *Note*: Deactivate venv after use by executing *deactivate.bat* in above path

* Download project repository from GitHub (link: https://github.com/kiru07/OAuth_Flask_SSD2/)
  - Extract project folder and place files inside *Flask_OAuth_App* directory

* Install dependency packages in venv using *requirements.txt*
> *Note*: Make sure venv is activated


        pip install -r requirements.txt


#### GitHub OAuth App Credentials

* Register for an OAuth application on GitHub
  - Login to GitHub
  - Go to *Settings -> Developer Settings -> OAuth Apps -> New OAuth App*
  - Fill in the following details

        Application Name: *<any valid name>* (eg: flask_oauth_app)
        Homepage URL: http://localhost:5000
        Application Description: *<any valid description>*
        Authorization callback URL: http://localhost:5000/login/oauth2/code/github

  - Click *Register Application*
  - Make note of the __Client ID__ and __Client Secret__ provided by GitHub

  * Set credentials in flask app
    - In *flaskapp.py* replace following variable values (line 17, 18) with the *Client ID* and *Client Secret* credentials provided by GitHub

            ...
            ...
            # Github OAuth App credentials (Store as .env in production)
            GITHUB_CLIENT_ID = 'Paste Client ID Here'
            GITHUB_CLIENT_SECRET = 'Paste Client Secret Here''
            ...
            ...

> Project setup complete

## Start Application

* Makesure the virtual environment is activated
* Run following command to start development server:

        python flaskapp.py

* This will start the application on __*http://localhost:5000*__ (ie: *http://127.0.0.1:5000*)
  - Login using a GitHub Account
  - Use nav links to create or view gists
