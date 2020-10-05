from flask import Flask, render_template, redirect, request, url_for, flash, session
from forms import LoginForm, GistForm
from werkzeug.utils import secure_filename
from datetime import datetime
from requests.models import PreparedRequest
import api_service
import requests
import utils

# Initialize Flask app
app = Flask(__name__)

# Secret Key for protection against CSRF. Used by Flask-WTF, session etc. (generated using secrets.token_hex(16))
app.config['SECRET_KEY'] = 'bda06c0f9615d53f003c145514b94e2a'

# Github OAuth App credentials (Store as .env in production)
GITHUB_CLIENT_ID = 'REPLACE WITH YOUR GITHUB OAUTH APPLICATION CLIENT ID'
GITHUB_CLIENT_SECRET = 'REPLACE WITH YOUR GITHUB OAUTH APPLICATION CLIENT SECRET'


# GitHub OAuth and API urls
GITHUB_OAUTH_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
GITHUB_OAUTH_ACCESS_URL = "https://github.com/login/oauth/access_token"
GITHUB_GIST_API_URL = "https://api.github.com/gists"
GITHUB_USER_API_URL = "https://api.github.com/user"


# ================== Route handlers ================================================

@app.route("/")
@app.route("/home")
def home():
    """ Handles GET requests to home page"""
    # Instantiate a login form
    form = LoginForm()
    return render_template('home.html', title='Home', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    """ Redirects to GitHub OAuth to authorize app """

    # ============  OAuth Step 1: Verify user's identity (ie: Authenticate user) and obtain Authorization --  Request for Authorization Code ==============

    # (Required) ClientId provided by Github when an OAuth app is registered
    client_id = GITHUB_CLIENT_ID
    # (Optional - default is public_repo) Resource scope we want access to from user (See docs for list)
    scope = 'public_repo gist read:user'
    # (Optional) - Random string sent to github and returned by github (helps check for CSRF)
    state = utils.get_state_string()
    # Store the state in session for verification later
    session['state'] = state

    # Use requests library to construct the url with client id as query param
    github_ouath_url = GITHUB_OAUTH_AUTHORIZE_URL
    params = {'client_id': client_id, 'scope': scope, 'state': state}
    request_url = PreparedRequest()
    request_url.prepare_url(github_ouath_url, params)

    # Redirect to GitHub's OAuth page - user will be authenticated and Authorization Code (Auth Grant) is returned.
    # (Note: GitHub will then redirect to the URL we specified  when registering the OAuth app - only if authentication is valid)
    return redirect(request_url.url)


@app.route("/login/oauth2/code/github")
def auth_callback():
    """
     Handler for URL redirected by GitHub. Uses Authorization Code to obtain Access Token from GitHub

     GitHub redirects to this route if authentication succeeds. This route is registered with GitHub when registering this OAuth App
     """

    # ==============  OAuth Step 2: Use Authorization Code and request for Access Token =============

    # Get the 'state' value returned from query parameter. Must be same as the one we passed to github
    state = request.args.get('state')
    our_state = session['state']
    if state == our_state:
        # Get the Authorization Code provided by github from query parameter
        auth_code = request.args.get('code')
        # Construct the URL for POST request to obtain Access Token from GitHub
        client_id = GITHUB_CLIENT_ID
        client_secret = GITHUB_CLIENT_SECRET
        params = {'client_id': client_id,
                  'client_secret': client_secret, 'code': auth_code}

        # To get access token in response body as json (default is via query param)
        headers = {'Accept': 'application/json'}

        # Construct the POST request. Accept JSON response
        response = requests.post(
            GITHUB_OAUTH_ACCESS_URL, params, headers=headers)

        if response.status_code == requests.codes.ok:
            # Retrieve the access token and other values returned from GitHub
            access_response = response.json()
            access_token = access_response['access_token']
            # scope = access_response['scope']
            # token_type = access_response['token_type']

            # Store the access token in the session
            session['access_token'] = access_token
            # Redirect to logged in page
            return redirect(url_for('gists'))
        else:
            return render_template('error.html', title='Error', error='400 - Bad Request')
    else:
        return render_template('error.html', title='Error', error='403 - Forbidden (OAuth State Mismatch)')


@app.route("/login/oauth2/code/github/gists")
def gists():
    """ Home page of authenticated user. Lists recent gists of authenticated user """
    if request.method == 'GET':
        if session.get('access_token'):
            # Get username from github
            username = api_service.get_user_name(GITHUB_USER_API_URL)
            # Store in session
            session['username'] = username
            # Fetch gists and process
            gist_list = api_service.get_recent_gists(GITHUB_GIST_API_URL)
            if gist_list:
                # Render template
                return render_template('gists.html', title='Recent Gists', logged_in=True, gists=gist_list, username=username)
            else:
                # If no gists created yet
                return render_template('error.html', title='Recent Gists', logged_in=True, error="You don't have any gists yet!", username=username)
        else:
            # If route accessed without access token
            return render_template('error.html', title='Error', error='403 - Forbidden')
    else:
        # For methods other than GET or POST
        return render_template('error.html', title='Error', error='405 - Method Not Supported')


@app.route("/login/oauth2/code/github/gists/create", methods=['GET', 'POST'])
def create_gist():
    """ 
    Route handler for creating GitHub Gists.

    Uses Access Token to create protected resource(gist) of authenticated user
    """
    # Instantiate Create Gist Form
    form = GistForm()
    if request.method == 'GET':
        # Check if Access Token Present
        if session.get('access_token') and session.get('username'):
            # Get username from session
            username = session['username']
            return render_template('create_gist.html', title='Create Gist', form=form, logged_in=True, username=username)
        else:
            return render_template('error.html', title='Error', error='403 - Forbidden')
    elif request.method == 'POST':
        # Form submitted - Validate input
        if form.validate_on_submit():
            # ================= OAuth Step 3: Use Access token to send data to Github gist api ==================

            # Get submitted data from form (POST body)
            # Making sure input is secure
            filename = secure_filename(request.form['filename'])
            description = request.form.get('description')
            gist_content = request.form['gist_content']
            is_public_gist = request.form.get('is_public_gist')

            # Get access_token from session
            access_token = session['access_token']
            # Build POST body (json) for publishing to Gist API
            payload = utils.build_gist_payload(
                filename, gist_content, is_public_gist, description)
            # Header with Access Token
            headers = {
                'Authorization': f'token {access_token}',
                'Accept': 'application/vnd.github.v3+json'  # for json response
            }

            # Send POST request to Gist API with json payload
            api_response = requests.post(
                GITHUB_GIST_API_URL, headers=headers, json=payload)
            # If 201 Created - then Gist published successfully
            if api_response.status_code == requests.codes.created:
                # Show flash message with success message
                flash('Gist Published Successfully!', 'success')
            else:
                # Show flash message with error message
                flash('Gist Failed to Publish!', 'danger')
            return redirect(url_for('gists'))
        else:
            # Show flash message for any validation errors
            username = session['username']
            flash(
                'Gist Failed to Publish. Please check filename and content and try again', 'danger')
            return render_template('create_gist.html', title='Create Gist', form=form, logged_in=True, username=username)
    else:
        # For request methods other than GET or POST
        return render_template('error.html', title='Error', error='405 - Method Not Supported')


@app.route("/logout")
def logout():
    """
    Logs user out of the application

    Clears session values of user
    """
    session.pop('access_token', None)
    session.pop('state', None)
    session.pop('username', None)
    # Redirect to home page
    return redirect(url_for('home'))


# =================== Jinja Template - Custom Filter ===============================


@app.template_filter('datetimeformat')
def datetimeformat(iso_datetimestring, format_string='%A %b %d, %Y at %H:%M GMT'):
    """ Formats IS08601 datetime strings in jinja template """
    iso_format = '%Y-%m-%dT%H:%M:%SZ'
    parsed_date = datetime.strptime(iso_datetimestring, iso_format)

    return parsed_date.strftime(format_string)


# To start flask dev server by running "python flaskapp.py"
if __name__ == '__main__':
    app.run(debug=True)
