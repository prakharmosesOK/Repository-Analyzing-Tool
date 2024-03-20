from django.shortcuts import render
import json
from django.http import JsonResponse

# import ast
# import networkx as nx
import os
# import matplotlib.pyplot as plt

# import base64

import subprocess
from github import Github


  
# from PIL import Image

# Cloning the Repository into the local system
def repo_cloning(git_repo_link: str) -> str:
    repo_file_path = os.path.basename(git_repo_link)
    print("The file path is: ", repo_file_path)

    # Checking if the repo already exists at the desired place
    if os.path.exists(repo_file_path):
        return os.path.abspath(repo_file_path)
    subprocess.check_call(['git', 'clone', f'{git_repo_link}', repo_file_path])
    return os.path.abspath(repo_file_path)

# Reading the requirements file
def read_dependencies(repo_path: str) -> str:
    dependencies_file = os.path.join(repo_path, "requirements.txt")
    
    # Check if requirements.txt exists
    if not os.path.exists(dependencies_file):
        # Create requirements.txt using pipreqs (assuming it's installed)
        depend_command = f"pipreqs {repo_path} --force --savepath {dependencies_file}"
        try:
            subprocess.check_call(depend_command.split())  # Using split() for safer execution
        except subprocess.CalledProcessError as e:
            print(f"Error running pipreqs: {e}")
            return None  # Or return a more informative error message

    # Read dependencies (assuming requirements.txt exists now)
    try:
        with open(dependencies_file, "r") as file:
            dependencies = file.read()
            return dependencies
    except FileNotFoundError:
        print(f"requirements.txt not found in {repo_path}")
        return None  # Or return a more informative error message

DEV_MODE = True

# Getting the dependencies used in a GitHub repo
def get_dependencies(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required'})
    try:
        req=json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON request body'})
    git_repo_link = req["input"]

    # print(f"Received input: {git_repo_link}")  # Debugging print statement
    if git_repo_link is not None:
        print("repo link: ", git_repo_link)
        repo_path = repo_cloning(git_repo_link)
        print(repo_path)
        output_dependencies = read_dependencies(repo_path)
        print(output_dependencies)
        return JsonResponse({'output': output_dependencies})
    else:
        return JsonResponse({'error': 'No input provided'})


# -----------------------------------------------------------------------------------------------------------------
# Implementing version control
def get_commit_history(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required'})
    
    # Create a Github object, providing your personal access token
    # Repo_Analyze_App = os.getenv("Repo_Analyze_App")
    Repo = os.getenv("Repo")
    Repo2 = os.getenv("Repo2")
    Repo3 = os.getenv("Repo3")
    g = Github(Repo3)
    
    # Get the repository object
    body=json.loads(request.body)
    # print(body)
    input_text=body["input"]
    print(input_text)
    
    x=input_text.split('/')
    n=len(x)
    repo_owner=x[n-2]
    repo_name=x[n-1]
    print("The repo owner is: ", repo_owner)
    print("The repo name is: ", repo_name)
    repo = g.get_repo(f"{repo_owner}/{repo_name}")

    # Print the name of the default branch
    print(f"Default branch: {repo.default_branch}")

    # Print the latest commit information for the default branch
    commit_list = repo.get_commits()
    s=""
    print("The commits are follows: \n", commit_list)

    output_string = ""
    for commit in commit_list:
        output_string += "SHA: " + commit.sha + "\n"
        output_string += "URL: " + commit.url + "\n"
        output_string += "Message: " + commit.commit.message + "\n"
        if(commit.author is not None):
            output_string += "Author: " + commit.author.login + "\n"
        if(commit.committer is not None):
            output_string += "Committer: " + commit.committer.login + "\n"
        output_string += "Parents: " + str([parent.sha for parent in commit.parents]) + "\n"
        output_string += "Stats: " + str(commit.stats) + "\n"
        output_string += "Files: " + str(commit.files) + "\n"
        output_string += "$\n"
    print(output_string)
    
    return JsonResponse({'output': output_string})