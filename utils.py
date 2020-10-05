"""Helpful functions for flaskapp"""
import secrets


def get_state_string():
    """ Generates random string passed to github oauth for state management (also helps check against CSRF)"""
    return secrets.token_hex(16)


def build_gist_payload(filename, gist_content, is_public_gist, description=None):
    """Returns the payload body to send to GitHub Gist API"""
    is_public_gist = True if is_public_gist == 'y' else False
    description = description if description else ""
    payload = {
        "description": description,
        "public": is_public_gist,
        "files": {
            filename: {
                "content": gist_content
            }
        }
    }
    return payload
