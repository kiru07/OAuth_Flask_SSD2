"""Service functions to perform requests to GitHub API"""
from flask import session
import requests


def get_user_name(api_url):
    """Fetches github user name using access token"""
    # GET user data and return the username
    access_token = session['access_token']
    headers = {
        'Authorization': f'token {access_token}',
        'Accept': 'application/vnd.github.v3+json',
    }

    response = requests.get(api_url, headers=headers)

    if(response.status_code == requests.codes.ok):
        user_data = response.json()
        return user_data['login']
    else:
        return None


def get_recent_gists(api_url, count=10, page=1):
    """ Fetches last [count] gists of authenticated user """
    # Make GET request last 10 gists of user
    access_token = session['access_token']
    headers = {
        'Authorization': f'token {access_token}',
        'Accept': 'application/vnd.github.v3+json',
    }
    params = {'page': page, 'per_page': count}

    response = requests.get(api_url, headers=headers, params=params)

    if response.status_code == requests.codes.ok:
        # Process the response and extract only necessary info
        list_of_gists = response.json()
        parsed_gists = parse_gists_response(list_of_gists)

        return parsed_gists
    else:
        return None


def parse_gists_response(gists_response):
    """ Parses json response from GitHub API for Gists. Extracts necessary information and returns the list of gists """
    parsed_gists = []
    for gist in gists_response:
        filename = list(gist['files'])[0]
        required_info = {
            'html_url': gist['html_url'],
            'created_at': gist['created_at'],
            'filename': filename,
            'language': gist['files'][filename]['language']
        }
        parsed_gists.append(required_info)

    return parsed_gists
