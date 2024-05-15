from django.shortcuts import render
import json
import base64
from django.http import JsonResponse, HttpResponse

import os
import requests
import google.generativeai as genai
import os
from dotenv import load_dotenv

import subprocess
from github import Github
import shutil
from git import exc


  
# Load the environment variables from the .env file
load_dotenv()

gemni_api_key = os.getenv("GEMNI_API_KEY")
genai.configure(api_key=gemni_api_key)

# Set up the model
generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

# Don't chnage these
safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
]

model = genai.GenerativeModel(model_name="gemini-1.0-pro",
                            generation_config=generation_config,
                            safety_settings=safety_settings)

# To save the history of the conversation
convo = model.start_chat(history=[
])



# Creation of all the views
# -----------------------------------------------------------------------------------------------------------------
# Cloning the Repository into the local system
def repo_cloning(git_repo_link: str, branch: str = "main") -> str:
    repo_file_path = os.path.basename(git_repo_link)

    if os.path.exists(repo_file_path):
        return os.path.abspath(repo_file_path)
    subprocess.check_call(['git', 'clone', '--branch', f'{branch}', f'{git_repo_link}', repo_file_path])
    return os.path.abspath(repo_file_path)

# Reading the requirements file
def read_dependencies(repo_path: str) -> str:
    dependencies_file = os.path.join(repo_path, "requirements.txt")
    print("The dependencies_file is: ", dependencies_file)
    
    if not os.path.exists(dependencies_file):
        # Create requirements.txt using pipreqs (assuming it's installed)
        depend_command = f"pipreqs --force --savepath requirements.txt"
        # gen_reqin = "pipreqs --savepath=requirements.in"
        # gen_reqtxt = "pip-compile"
        # depend_gen_command = f"pipreqs {repo_path} --force --savepath {dependencies_file} --generate"
        try:
            curr_dir = os.getcwd()
            os.chdir(repo_path)
            subprocess.check_call(depend_command.split())
            os.chdir(curr_dir)
        except subprocess.CalledProcessError as e:
            print(f"Error running pipreqs: {e}")
            return "Could not fetch dependencies!"

    # Read dependencies (assuming requirements.txt exists now)
    try:
        with open(dependencies_file, "r") as file:
            dependencies = file.read()
            return dependencies
    except FileNotFoundError:
        print(f"requirements.txt not found in {repo_path}")
        return "Could not fetch dependencies!"

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
    try:
        req=json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON request body'})
    input_text = req["input"]
    if input_text is None:
        return JsonResponse({'error': 'No input provided'})
    
    # Create a Github object, providing your personal access token
    g = Github()
    
    x=input_text.split('/')
    n=len(x)
    repo_owner=x[n-2]
    repo_name=x[n-1]
    
    repo = g.get_repo(f"{repo_owner}/{repo_name}")

    # Print the latest commit information for the default branch
    commit_list = repo.get_commits()
    s=""

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
    
    return JsonResponse({'output': output_string})

# -----------------------------------------------------------------------------------------------------------------
# Implementing file extraction
def get_files_from_repository(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required'})
    
    body=json.loads(request.body)
    input_text=body["input"]
    print(input_text)
    if input_text is None:
        return JsonResponse({'error': 'No input provided'})
    
    file_names = []
    api_link = input_text.replace("github.com", "api.github.com/repos") + "/contents/"
    response = requests.get(api_link)

    if response.status_code == 404:
        print("Invalid Github repo link")
        return

    files = json.loads(response.text)
    # print(files)

    for file in files:
        if (file["type"] == "file"):
            file_url = input_text + "/blob/main/" + file["path"]
            file_names.append(file_url)
        elif (file["type"] == "dir"):
            get_files_from_dir(input_text, file["path"], file_names)
            pass
    print_array(file_names) # To display the files fetched
    return JsonResponse({'output': file_names})

def get_files_from_dir(repo_link, dir_path, file_names):
    api_link = repo_link.replace("github.com", "api.github.com/repos") + "/contents/" + dir_path
    response = requests.get(api_link)

    if (response.status_code == 404):
        print("Invalid GitHub Repository link!")
        return
    files = json.loads(response.text)

    for file in files:
        if file["type"] == "file":
            file_url = repo_link + "/blob/main/" + dir_path + "/" + file["name"]
            file_names.append(file_url)
        elif file["type"] == "dir":
            get_files_from_dir(repo_link, dir_path + "/" + file["name"], file_names)

# -----------------------------------------------------------------------------------------------------------------
# Implementing Documentation Generator
# Using Gemni ai
def generate_by_model(prompt: str):
    convo.send_message(prompt)
    return (convo.last.text)

# Fetching data from files
# def fetch_data_from_files(files):
#     files_data = {}
#     for file in files:
#         repo_url = file.split("/")
#         print(repo_url)
#         owner = repo_url[3]
#         repo = repo_url[4]
#         file_path = "/".join(repo_url[7:])
#         api_link = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
#         response = requests.get(api_link, params={"ref": "main"})
#         if response.status_code == 404:
#             print("Invalid Github repo link")
#             return
#         data = response.json()
#         files_data[file] = base64.b64decode(data["content"]).decode("utf-8")
#     return files_data

def fetch_data_from_files(files):
    files_data = {}
    for file in files:
        with open(file, 'r') as f:
            files_data[file] = f.read()
    return files_data

# Parsing the file contents
def parse_pyfile_content(file_data):
    parsed_sections = []
    current_section = ""
    import_section = ""
    is_Class = False
    is_Function = False

    for line in file_data.splitlines():
        if not line:
            continue
        
        if  line == "" or line.isspace():
            current_section += "\n"
            continue

        if line.startswith("import") or line.startswith("from"):
            import_section += line + "\n"
            continue

        if is_Class:
            if line.startswith("    ") or line.startswith("\t") or line.startswith("  "):
                current_section += line + "\n"
            else:
                parsed_sections.append(current_section)
                current_section = ""
                is_Class = False
                if line and line.isspace() == False and line != "":
                    current_section += line + '\n'
                    if line.startswith("class"):
                        is_Class = True
                    elif line.startswith("def"):
                        is_Function = True
            continue
        
        if is_Function:
            if line.startswith("    ") or line.startswith("\t") or line.startswith("  "):
                current_section += line + "\n"
            else:
                parsed_sections.append(current_section)
                current_section = ""
                is_Function = False
                if line and line.isspace() == False and line != "":
                    current_section += line + '\n'
                    if line.startswith("class"):
                        is_Class = True
                    elif line.startswith("def"):
                        is_Function = True
            continue
        
        if line.startswith("class"):
            parsed_sections.append(current_section)
            current_section = line + "\n"
            is_Class = True
            continue

        if line.startswith("def"):
            parsed_sections.append(current_section)
            current_section = line + "\n"
            is_Function = True
            continue
        
        if current_section.startswith("def") or current_section.startswith("class"):
            is_Function = False
            is_Class = False
            parsed_sections.append(current_section)
            current_section = ""
        current_section += line + "\n"
    
    if current_section != "" or current_section.isspace() == False:
        parsed_sections.append(current_section)
    parsed_sections.insert(0, import_section)
    return parsed_sections

# Preparing the data for the model
def preprocess_data(files_data):
    for file_name, file_data in files_data.items():
        files_data[file_name] = parse_pyfile_content(file_data)
    return files_data

# Generating Docstrings
def generate_docstrings_each(files_data):
    for file_name, file_data in files_data.items():
        updated_file_data = []
        prompt1 = "Generate DocStrings for the following import statement after each one in triple quotes:\n"
        prompt2 = "Generate DocStrings for the following python class just after the first line:\n"
        prompt3 = "Generate DocStrings for the following python function just after the first line:\n"
        prompt4 = "Generate DocStrings for the following python code in a single unit at the last in triple quotes:\n"
        for component in file_data:
            if not component or component == "" or component.isspace():
                updated_file_data.append(component)
                continue
            elif component.startswith("import"):
                updated_component = generate_by_model(prompt1 + component)
            elif component.startswith("class"):
                updated_component = generate_by_model(prompt2 + component)
            elif component.startswith("def"):
                updated_component = generate_by_model(prompt3 + component)
            else:
                updated_component = generate_by_model(prompt4 + component)
            updated_file_data.append(updated_component)
        files_data[file_name] = updated_file_data
    return files_data

# Postprocessing the data
# Handling import statements
def handle_post_import(component):
    updated_import = []
    for line in component.splitlines():
        if not line or line.startswith("```") or line == "" or line == "\n" or line.isspace():
            continue
        elif line.startswith("```python"):
            updated_import.append("\n")
        else:
            updated_import.append(line)
    return "\n".join(updated_import)

# Handling class statements
def handle_post_class(component):
    for i in range(len(component)):
        if component[i:i+5] == "class":
            break
    for j in range(len(component)-2, 0, -1):
        if component[j:j+1] == "\n":
            break
    return component[i:j+1]

# Handling function statements
def handle_post_function(component):
    for i in range(len(component)):
        if component[i:i+3] == "def":
            break
    for j in range(len(component)-2, 0, -1):
        if component[j:j+1] == "\n":
            break
    return component[i:j+1]

# Handling code blocks
def handle_post_codeblock(component):
    updated_codeblock = []
    for line in component.splitlines():
        if not line or line.startswith("```") or line.startswith("```python") or line.startswith("##") or line.startswith("**"):
            continue
        else:
            updated_codeblock.append(line)
    component = "\n".join(updated_codeblock)
    if not component.endswith('"""'):
        component += '"""'
    return component

# Main unit of postprocessing the data
def postprocess_data(generated_doc_strings, files_data_to_generate):
    for file_name, file_data in generated_doc_strings.items():
        updated_file_data = []
        for i, component in enumerate(file_data):
            if not component or component == "" or component.isspace():
                updated_file_data.append(component)
                continue
            if files_data_to_generate[file_name][i].startswith("import"):
                component = handle_post_import(component)
            elif files_data_to_generate[file_name][i].startswith("class"):
                component = handle_post_class(component)
            elif files_data_to_generate[file_name][i].startswith("def"):
                component = handle_post_function(component)
            else:
                component = handle_post_codeblock(component)
            updated_file_data.append(component)
        generated_doc_strings[file_name] = updated_file_data
    return generated_doc_strings

# Writing the generated docstrings to the files
def assemble_files(generated_doc_strings):
    for file_name, file_data in generated_doc_strings.items():
        updated_file_data = ""
        for component in file_data:
            updated_file_data += component + "\n\n"
        generated_doc_strings[file_name] = updated_file_data
    return generated_doc_strings

# Copying all the contents from main branch to another branch
# def create_branch_and_copy_contents(owner, repo, token2):
#     # GitHub API URLs
#     repo_url = f"https://api.github.com/repos/{owner}/{repo}"
#     branches_url = f"{repo_url}/git/refs/heads"
#     refs_url = f"{repo_url}/git/refs"

#     # Headers for the API requests
#     headers = {
#         'Authorization': f'token {token2}',
#         'Accept': 'application/vnd.github.v3+json',
#     }

#     # Get the list of branches
#     response = requests.get(branches_url, headers=headers)
#     response.raise_for_status()  # Raise an exception if the request failed

#     branches = response.json()

#     # Check if the branch already exists
#     if any(branch['ref'] == 'refs/heads/DocStrGen' for branch in branches):
#         print("Branch 'DocStrGen' already exists.")
#         return

#     # Get the SHA of the latest commit on main
#     main_sha = next(branch['object']['sha'] for branch in branches if branch['ref'] == 'refs/heads/main')

#     # Create the new branch
#     response = requests.post(refs_url, headers=headers, data=json.dumps({
#         'ref': 'refs/heads/GenDocStr',
#         'sha': main_sha,
#     }))
#     response.raise_for_status()  # Raise an exception if the request failed

# Writing the files in DocStrGen branch
# def write_to_file_in_branch(owner, repo, token, path, message, content, branch="GenDocStr"):
#     # GitHub API URL
#     file_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"

#     # Headers for the api request
#     headers = {
#         'Authorization': f'token {token}',
#         'Accept': 'application/vnd.github.v3+json',
#     }

#     # Get the SHA of the file
#     response = requests.get(file_url, params={'ref': branch})
#     sha = response.json().get('sha') if response.status_code == 200 else None

#     # Updating the file
#     response = requests.put(file_url, headers=headers, data=json.dumps({
#         'message': message,
#         'content': base64.b64encode(content.encode()).decode(),
#         'sha': sha,
#         'branch': branch,
#     }))
#     response.raise_for_status()   # Raise an exception if the request failed
#     return "Updated successfully!"

# def commit_file_data_to_branch(file_data_dict, branch_name="GenDocStr", access_token=None):
#     if not access_token:
#         raise ValueError("A GitHub access token with write permissions is required.")

#     # Create a temporary local repository
#     try:
#         repo = Repo.clone_from(list(file_data_dict.keys())[0].split("//")[1], branch=branch_name)
#     except Exception as e:
#         raise RuntimeError(f"Error cloning repository: {e}")

#     for file_url, file_data in file_data_dict.items():
#         # Extract file path from URL
#         file_path = file_url.split("/")[-1]

#         # Update file content
#         try:
#             with open(file_path, "w") as f:
#                 f.write(file_data)
#         except FileNotFoundError:
#             raise ValueError(f"File '{file_path}' not found in the repository.")

#         # Stage the changes
#         try:
#             repo.index.add([file_path])
#         except Exception as e:
#             raise RuntimeError(f"Error adding file '{file_path}' to index: {e}")

#     # Commit the changes with a descriptive message
#     commit_message = f"Update files with new data"
#     try:
#         repo.index.commit(commit_message)
#     except Exception as e:
#         raise RuntimeError(f"Error committing changes: {e}")

#     # Push the changes to the remote branch
#     try:
#         origin = repo.remote(name="origin")
#         origin.push(f"refs/heads/{branch_name}", auth=(access_token, ""))
#     except Exception as e:
#         raise RuntimeError(f"Error pushing changes to remote branch: {e}")

# Writing the files in the GitHub repo with the generated docstrings on another branch
# def write_to_files(files):
#     repo_file = list(files.keys())[0]
#     repo_url = repo_file.split("/")
#     owner = repo_url[3]
#     repo = repo_url[4]
#     token = os.getenv("GITHUB_ACCESS_TOKEN")
#     token2 = os.getenv("GITHUB_ACCESS_TOKEN2")

#     # Create a new branch and copy the contents of the main branch
#     create_branch_and_copy_contents(owner, repo, token2)

#     # # Write the generated docstrings to the files
#     # for file_name, file_data in files.items():
#     #     repo_link = file_name.split("/")
#     #     path = "/".join(repo_link[7:])
#     #     message = f"Writing doc strings to {path}"
#     #     result = write_to_file_in_branch(owner, repo, token, path, message, file_data)
#     #     if result != "Updated successfully!":
#     #         break
#     # else:
#     #     return "Doc Strings generated successfully!"
#     commit_file_data_to_branch(files)
#     return "Some error occured, please try again!"

# def writing_to_GitHub(files):
#     repo_file = list(files.keys())[0]
#     repo_url = repo_file.split("/")
#     owner = repo_url[3]
#     repo_name = repo_url[4]
#     token = os.getenv("GITHUB_ACCESS_TOKEN")

#     g = Github(token)
#     repo = g.get_repo(f"{owner}/{repo_name}")

#     # Creating a new branch named 'GenDocStr'
#     # branch = repo.create_branch('GenDocStr')
#     branch = repo.create_git_ref(f'refs/heads/GenDocStr', 'HEAD')

#     # Looping through files
#     for url, content in files.items():
#         file_path = url.split("/")[-1]
#         with open(file_path, 'w') as f:
#             f.write(content)
#         repo.index.add(file_path)
#         commit_message = f"Updating {file_path} with generated data"
#         branch.commit(commit_message)

#         os.remove(file_path)
    
#     branch.push()
#     return "Files updated successfully!"

# Writing to the files locally
def write_to_files(files):
    try:
        for file_name, file_data in files.items():
            with open(file_name, 'w') as f:
                f.write(file_data)
    except Exception as e:
        raise RuntimeError(f"Error writing to file: {e}")

# Committing and pushing the changes to the remote in GenDocStr branch
def commit_and_push(local_repo_path, repo_link):
    try:
        # g_token = os.getenv("GITHUB_TOKEN")
        g_token = os.getenv("GITHUB_NEW_TOKEN")
        curr_dir = os.getcwd()
        os.chdir(local_repo_path)
        subprocess.run(['git', 'checkout', '-b', 'GenDocStr'], check=True)
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', 'Generated by GitHub Repo Analyzer'], check=True)
        
        # # Forking the repo
        url_parts = repo_link.split("/")
        owner, repo_name = url_parts[3], url_parts[4]
        api_url = f"https://api.github.com/repos/{owner}/{repo_name}/forks"
        headers = {"Authorization": f"token {g_token}"}
        response = requests.post(api_url, headers = headers)
        if response.status_code != 202:
            raise RuntimeError(f"Error forking the repository: {response.text}")
        
        forked_repo = response.json()["clone_url"]
        subprocess.run(['git', 'remote', 'add', 'docstrgen', forked_repo], check=True)
        subprocess.run(['git', 'push', 'docstrgen', 'GenDocStr'], check=True)
        
        # Creating the PULL request
        pull_token = os.getenv("GITHUB_PULL_TOKEN")
        pull_url = f"https://api.github.com/repos/{owner}/{repo_name}/pulls"
        payload = {
            "title": "Pull request of generated docstrings",
            "body": "This is a pull request of the generated docstrings",
            "head": "prakharmosesOK:GenDocStr",
            "base": "main"
        }
        headers = {"Authorization": f"token {pull_token}"}
        response = requests.post(pull_url, headers=headers, json=payload)
        if response.status_code != 201:
            raise RuntimeError(f"Error creating the pull request: {response.text}")

        os.chdir(curr_dir)
    except (exc.GitCommandError, Exception) as e:
        print(f"Error committing and pushing changes: {e}")
        raise RuntimeError(f"Error committing and pushing changes: {e}")

# Main function to map docstrings generation
def generate_doc_strings(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required'})
    try:
        req=json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON request body'})
    files = req["input"]
    if files is None:
        return JsonResponse({'error': 'No input provided'})
    
    repo_link = "/".join(files[0].split("/")[:5])
    local_repo_path = repo_cloning(repo_link)

    # Getting the local file paths
    local_files = []
    for file in files:
        local_files.append(local_repo_path + "/" + "/".join(file.split("/")[7:]))
    
    files_data = fetch_data_from_files(local_files) # Need to make fn
    files_data_to_generate = preprocess_data(files_data)
    files_data_for_future = files_data_to_generate.copy()
    generated_doc_strings = generate_docstrings_each(files_data_to_generate)
    generated_doc_strings = postprocess_data(generated_doc_strings, files_data_for_future)
    files_data = assemble_files(generated_doc_strings)
    try:
        write_to_files(files_data)
        commit_and_push(local_repo_path, repo_link)
        return JsonResponse({'output': 'Doc Strings generated successfully!'})
    except Exception as e:
        return JsonResponse({'error': f'Error: {e}'})

# def generate_doc_strings(request):
#     if request.method != 'POST':
#         return JsonResponse({'error': 'POST request required'})
#     try:
#         req=json.loads(request.body)
#     except json.JSONDecodeError:
#         return JsonResponse({'error': 'Invalid JSON request body'})
#     files = req["input"]
#     if files is None:
#         return JsonResponse({'error': 'No input provided'})
    
#     files_data = fetch_data_from_files(files)
#     files_data_to_generate = preprocess_data(files_data)
#     file_data_for_future = files_data_to_generate.copy()
#     generated_doc_strings = generate_docstrings_each(files_data_to_generate)
#     generated_doc_strings = postprocess_data(generated_doc_strings, file_data_for_future)
#     files = assemble_files(generated_doc_strings)
#     result = write_to_files(files)
#     # result = writing_to_GitHub(files)
#     return JsonResponse({'output': result})


# Spacy model training for documentation generation
# def run_once_for_spacy():
#     import spacy
#     from spacy import displacy
#     from spacy.tokens import DocBin
#     from tqdm import tqdm
#     from spacy.util import filter_spans

#     nlp = spacy.load("en_core_web_lg")

#     with open('./python-train_clean.tsv', 'r', encoding='utf-8') as file:
#         data = file.read()

#     refined_first = list(data.split('\n'))
#     refined_data = []

#     for entry_row in refined_first:
#         entry = list(entry_row.split('\t'))
#         if (len(entry) < 2):
#             continue
#         if entry[0][0] == '"':
#             entry[0] = entry[0][1:]
#         if entry[0][-1] == '"':
#             entry[0] = entry[0][:-1]
#         if entry[1][0] == '"':
#             entry[1] = entry[1][1:]
#         if entry[1][-1] == '"':
#             entry[1] = entry[1][:-1]
#         refined_data.append(entry[0] + "\t" + entry[1])


#     training_data = []
#     for entry in refined_data:
#         temp_dict = {}
#         each_entry = list(entry.split('\t'))
#         if (len(each_entry) < 2):
#             continue
#         temp_dict['text'] = each_entry[0]
#         temp_dict['entities'] = [(0, len(each_entry[0]), each_entry[1])]
#         training_data.append(temp_dict)

#     nlp = spacy.blank("en")
#     doc_bin = DocBin()

#     for training_ex in tqdm(training_data):
#         text = training_ex['text']
#         labels = training_ex['entities']
#         doc = nlp.make_doc(text)
#         ents = []
#         for start, end, label in labels:
#             span = doc.char_span(start, end, label = label, alignment_mode = 'contract')
#             if span is not None:
#                 ents.append(span)
#         filtered_ents = filter_spans(ents)
#         doc.ents = filtered_ents
#         doc_bin.add(doc)

#     doc_bin.to_disk('train.spacy')

# def generate_by_spacy(prompt: str):
#     nlp_ner = spacy.load("./output/model-best")
#     doc = nlp_ner(prompt)
#     result = displacy.render(doc, style="ent")
#     return result


# -----------------------------------------------------------------------------------------------------------------
# Implementing Documentation generation using DocStrings
def genDocument_from_docstr(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required'})
    try:
        req=json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON request body'})
    repo_link = req["input"]
    if repo_link is None:
        return JsonResponse({'error': 'No input provided'})
    
    # Cloning the repository
    repo_path = repo_cloning(repo_link, "GenDocStr")

    # Move to the clone repo
    os.chdir(repo_path)

    if not os.path.exists("docs"):
        os.mkdir("docs")
    os.chdir("docs")

    # Initializing Sphinx project
    if not os.path.exists("docs"):
        subprocess.run(["sphinx-quickstart", "--quiet", f"--project=DocGenTool", "--author=DocGenerator"])
    
    os.chdir("..")

    # if not os.path.exists("__init__.py"):
    #     with open("__init__.py", "w") as f:
    #         f.write("")

    # Generate API documentation
    subprocess.run(['sphinx-apidoc', '-o', 'docs', '.'])
    
    # Adding modules to the index.rst file
    with open("docs/index.rst", "r") as conf_file:
        lines = conf_file.readlines()
    
    for i, line in enumerate(lines):
        if "   :caption: Contents:" in line:
            lines[i] = "   :caption: Contents: \n\n   modules\n"
    
    with open("docs/index.rst", "w") as index_file:
        index_file.writelines(lines)

    # Setting the theme to shpinx_rtd_theme and adding some essential features
    with open("docs/conf.py", "r") as conf_file:
        lines = conf_file.readlines()

    # Modify the contents
    for i, line in enumerate(lines):
        if "# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information" in line:
            lines[i] = '# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information \n\nimport os\nimport sys\nsys.path.insert(0, os.path.abspath(".."))\n'
        if "html_theme = 'alabaster'" in line:
            lines[i] = "\nhtml_theme = 'sphinx_rtd_theme'\n"
        if "extensions = []" in line:
            lines[i] = "extensions = ['sphinx.ext.todo', 'sphinx.ext.viewcode', 'sphinx.ext.autodoc']\n"

    # Write the modified contents back to the file
    with open("docs/conf.py", "w") as conf_file:
        conf_file.writelines(lines)
    
    os.chdir("docs")

    # Build the documentation
    # subprocess.run(['sphinx-build', '-b', 'html', 'docs', 'docs/_build'])
    subprocess.run(['make.bat', 'html'])
    os.chdir("..")

    # Create a zip file of the documentation generated
    shutil.make_archive('documentation', 'zip', 'docs')

    path_to_return = os.path.abspath('documentation.zip')
    path_to_return = path_to_return.replace("\\", '/')
    os.chdir("..")

    return JsonResponse({'output' : path_to_return})
    # Move the generated HTML files to the output directory
    # subprocess.run(["mv", "build/html", '../output_dir'])

# Downloading the generated documentation
def download_documentation(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required'})
    try:
        req = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON request body'})
    zip_file_link = req["input"]
    if zip_file_link is None:
        return JsonResponse({'error': 'No input provided'})
    
    with open(zip_file_link, 'rb') as zip_file:
        response = HttpResponse(zip_file.read(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=documentation.zip'
        return response

# -----------------------------------------------------------------------------------------------------------------
# Removing the zip file
def remove_zip(request):
    print("This is 1")
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required'})
    print("This is 2")
    try:
        req = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON request body'})
    print("This is 3")
    zip_file_link = req["input"]
    if zip_file_link is None:
        return JsonResponse({'error': 'No input provided'})
    
    path_to_remove_file = list(zip_file_link.split('/'))[:-1]
    path_to_remove_file = "/".join(path_to_remove_file)
    print("The file link received is: ", path_to_remove_file)

    # Removing the desired folder
    os.remove(zip_file_link)
    try:
        shutil.rmtree(path_to_remove_file, ignore_errors=True)
    except OSError as e:
        print(e)
    return JsonResponse({'output': 'Zip file removed successfully!'})

# -----------------------------------------------------------------------------------------------------------------
# Utils
def print_array(array):
    print("The files fetched are:")
    for i in array:
        print(i,",")