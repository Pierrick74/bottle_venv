import os
import pathlib
from urllib.parse import urljoin

import sys

import requests


MY_DIR = os.path.dirname(os.path.abspath(__file__))
WSGI_FILE_TEMPLATE = """
import sys

project_home = '/home/pierrickviret74/bottle_venv'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

from todo import app as application  
"""

GIT_FILE_TEMPLATE = """
import git

repo = git.Repo('/home/pierrickviret74/bottle_venv')
origin = repo.remotes.origin
origin.pull()
print("Repository updated")
"""

GIT_CREATE_TEMPLATE = """
import git
import os

repo_url = "https://github.com/Pierrick74/bottle_venv.git"
destination = os.path.expanduser('~/bottle_venv')

if not os.path.exists(destination):
    git.Repo.clone_from(repo_url, destination)
    print(f"Repository cloned to {destination}")
else:
    print("Repository already exists")
"""


def execute_remote_script(username, api_token, script_name):
    host = "www.pythonanywhere.com"
    headers = {'Authorization': f'Token {api_token}'}

    # 1. Créer une nouvelle console
    console_url = f"https://{host}/api/v0/user/{username}/consoles/"
    console_data = {
        "executable": "python3.10",
        "arguments": "",
        "working_directory": "/home/pierrickviret74/"
    }

    response = requests.post(console_url, headers=headers, json=console_data)
    console_info = response.json()
    console_id = console_info['id']
    print(f"Console créée avec ID: {console_id}")

    # Attendre que la console soit prête
    import time
    print("Attente de l'initialisation de la console...")
    time.sleep(10)

    # 2. Envoyer la commande pour exécuter le script
    input_url = f"https://{host}/api/v0/user/{username}/consoles/{console_id}/send_input/"
    command_data = {"input": f"python3.10 {script_name}\n"}

    response = requests.post(input_url, headers=headers, json=command_data)
    print("Commande envoyée")

    # 3. Récupérer le résultat
    import time
    time.sleep(10)  # Attendre l'exécution

    output_url = f"https://{host}/api/v0/user/{username}/consoles/{console_id}/get_latest_output/"
    response = requests.get(output_url, headers=headers)
    print("Sortie du script:")
    
    try:
        output_data = response.json()
        if 'output' in output_data:
            print(output_data['output'])
        else:
            print(f"Response keys: {list(output_data.keys())}")
            print(f"Full response: {output_data}")
    except requests.exceptions.JSONDecodeError:
        print(f"Non-JSON response: {response.text}")
        print(f"Status code: {response.status_code}")

    # 4. Fermer la console (optionnel)
    requests.delete(f"https://{host}/api/v0/user/{username}/consoles/{console_id}/", headers=headers)

def main():
    username = 'pierrickviret74'
    api_token = '9ba33966abd29f61229141c1718dd86f525c7582'

    region = "www"

    base_api_url = f"https://{region}.pythonanywhere.com/api/v0/user/{username}/"

    site_hostname = f"{username}.pythonanywhere.com"

    project_home = f"/home/{username}"

    webapps_url = urljoin(base_api_url, "webapps/")
    print(f"Checking if website already exists with GET from {webapps_url}")
    resp = requests.get(
        webapps_url,
        headers={"Authorization": f"Token {api_token}"}
    )
    if resp.status_code != 200:
        print(f"Error getting website list: status was {resp.status_code}\n{resp.content}")
        sys.exit(-1)

    sites = [site["domain_name"] for site in resp.json()]
    print(f"Found these sites: {sites}")
    if site_hostname not in sites:
        print(f"Creating website at {site_hostname} with POST to {webapps_url}")
        resp = requests.post(
            webapps_url,
            data={
                "domain_name": site_hostname,
                "python_version": "python37",
            },
            headers={"Authorization": f"Token {api_token}"}
        )
        if resp.status_code not in (200, 201):
            print(f"Error creating site: status was {resp.status_code}\n{resp.content}")
            sys.exit(-1)

    # Test d'écriture d'un fichier simple
    test_filename = "test_file.txt"
    test_content = "Hello from Python script - Test d'écriture"
    file_upload_url = f"{base_api_url}files/path/home/{username}/{test_filename}"

    response = requests.post(
        file_upload_url,
        files={"content": test_content},
        headers={"Authorization": f"Token {api_token}"}
    )

    response = requests.get(
        f'https://www.pythonanywhere.com/api/v0/user/{username}/files/path/home/{username}/bottle_venv/.gitignore',
        headers={'Authorization': f'Token {api_token}'}
    )
    file_upload_url = urljoin(base_api_url, f"files/path")
    print(f"gitignore resultat {response.status_code}")

    if response.status_code == 200:
        git_script_filename = site_hostname.replace(".", "_").lower() + "_gitscript.py"
        git_script_upload_url = file_upload_url + f"/{git_script_filename}"
        git_file_content = GIT_FILE_TEMPLATE
        resp = requests.post(
            git_script_upload_url,
            files={"content": git_file_content},
            headers={"Authorization": f"Token {api_token}"}
        )
        if resp.status_code in (200, 201):
            print(f"Script uploadé avec succès, exécution...")
            execute_remote_script(username, api_token, f"/home/{username}/git_update_script.py")
        else:
            print(f"Erreur upload script: {resp.status_code}")
    else:
        git_script_filename = "gitnewscript.py"
        git_file_content = GIT_CREATE_TEMPLATE
        git_script_upload_url = f"{base_api_url}files/path/home/{username}/{git_script_filename}"
        resp = requests.post(
            git_script_upload_url,
            files={"content": git_file_content},
            headers={"Authorization": f"Token {api_token}"}
        )
        if resp.status_code in (200, 201):
            print(f"Script uploadé avec succès, exécution...")
            execute_remote_script(username, api_token, "gitnewscript.py")
        else:
            print(f"Erreur upload script: {resp.status_code}")

    wsgi_file_filename = site_hostname.replace(".", "_").lower() + "_wsgi.py"
    wsgi_file_remote_path = f"/var/www/{wsgi_file_filename}"
    wsgi_file_upload_url = file_upload_url + wsgi_file_remote_path
    wsgi_file_content = WSGI_FILE_TEMPLATE.format(project_home=project_home)
    print(f"Uploading WSGI file via {wsgi_file_upload_url}")
    resp = requests.post(
        wsgi_file_upload_url,
        files={"content": wsgi_file_content},
        headers={"Authorization": f"Token {api_token}"}
    )
    if resp.status_code not in (200, 201):
        print(f"Error uploading WSGI file: status was {resp.status_code}\n{resp.content}")
        sys.exit(-1)


    our_webapp_url = urljoin(webapps_url, f"{site_hostname}/")
    static_file_route_url = urljoin(our_webapp_url, "static_files/")
    print(f"Getting existing static file routes with get to {static_file_route_url}")
    resp = requests.get(
        static_file_route_url,
        headers={"Authorization": f"Token {api_token}"}
    )
    if resp.status_code != 200:
        print(f"Error getting static file route list: status was {resp.status_code}\n{resp.content}")
        sys.exit(-1)

    static_route_urls = [route["url"] for route in resp.json()]
    print(f"Found these route URLs: {static_route_urls}")
    if "/static" not in static_route_urls:
        print(f"Configuring static file route with post to {static_file_route_url}")
        resp = requests.post(
            static_file_route_url,
            data={
                "url": "/static",
                "path": f"{project_home}/static",
            },
            headers={"Authorization": f"Token {api_token}"}
        )
        if resp.status_code not in (200, 201):
            print(f"Error creating static file route: status was {resp.status_code}\n{resp.content}")
            sys.exit(-1)

    reload_website_url = urljoin(our_webapp_url, "reload/")
    print(f"Reloading website with post to {reload_website_url}")
    resp = requests.post(
        reload_website_url,
        headers={"Authorization": f"Token {api_token}"}
    )
    if resp.status_code not in (200, 201):
        print(f"Error reloading website: status was {resp.status_code}\n{resp.content}")
        sys.exit(-1)

    site_url = f"https://{site_hostname}/"
    print(f"All done!  The site is now live at {site_url}")

if __name__ == "__main__":
    main()