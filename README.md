# GitHub-Repo-Analyzer

## 📖 Introduction

Struggling to understand a new codebase? Want to streamline your documentation process?
Introducing GitHub Repo Analyzer, your one-stop shop for analyzing and documenting your Git repositories!

This powerful tool empowers you to delve into the inner workings of your code, making it easier than ever to either finding the dependencies used, tracking commit history or generating documentation for your code to make easily readable.

## 📝 Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Benefits](#benefits)
4. [Targeted Users](#targetedusers)
5. [Getting Started](#gettingstarted)
6. [Usage](#usage)
7. [Future Goals](#futuregoals)
8. [Contributing](#contributing)
9. [Author](#author)
10. [License](#license)

## 📝 Overview

GitHub-Repo-Analyzer is a comprehensive tool designed to simplify the process of understanding and documenting your Git repositories. It offers a suite of features that cater to both individual developers and collaborative teams.

## ✨ Features

<ul>
  <li><strong>Dependency Analysis:</strong> Identifies all external libraries and frameworks used in your project. This helps understand project requirements and potential compatibility issues.</li>
  <li><strong>Commit History Analysis:</strong> Gain a comprehensive view of your repository's historical changes, including author, date, files changed and commit message. This allows you to track code evolution and identify contributions.</li>
  <li><strong>DocString Generation:</strong> Automatically generate DocStrings within your codebase. DocStrings are comments that explain the functionality of functions, classes, and modules. This improves code readability and maintainability. It automatically creates a pull request to the user's respective project updated with DocStrings.</li>
  <li><strong>Documentation Generation (using Sphinx):</strong> Leveraging Sphinx, a popular documentation generation tool, to create comprehensive API documentation from extracted DocStrings. This provides a user-friendly way to understand project functionalities.</li>
</ul>

## 📈 Benefits

<ul>
  <li><strong>Improved Code Understanding:</strong> Sometimes the dependencies used in the project to run are not available and creates a lot of problem. With this, developers can quickly grasp dependencies and focus on main task.</li>
  <li><strong>Enhanced Maintainability:</strong> DocString generation and automatic documentation creation streamline the maintenance process.</li>
  <li><strong>Clearer Contribution Guidelines:</strong> DocStrings provide a clear understanding of existing functions, allowing developers to add their own with proper documentation.</li>
  <li><strong>Increased Readability:</strong> Tool generates a proper html documentation leaveraging Sphinix to increase the readability for general purpose.</li>
</ul>

## 🎯 Targeted Users

<ul>
  <li>Individual developers working on personal or small projects.</li>
  <li>Developer teams need to confront a project with least comments or doc strings explaining the project.</li>
  <li>Open-source project maintainers aiming to improve contributor experience.</li>
</ul>

## 📲 Getting Started

Follow these steps to set up the GitHub-Repo-Analyzer on your system:

1. Clone the repository:
    ```bash
    git clone https://github.com/prakharmosesOK/Repository-Analyzing-Tool
    ```

2. Open two terminals, one for frontend and another for backend.

3. In first terminal, navigate to the frontend folder and install all dependencies. Then start the project.
    ```bash
    cd frontend
    ```
    ```bash
    npm install
    ```
    ```bash
    npm start
    ```

4. In second terminal, navigate to the backend folder, create a virtual environment.
    ```bash
    cd backend
    ```
    ```bash
    python -m venv gitrepoanalyzer
    ```

5. Activate the virtual environmentm install all required dependencies and run the server.
    ```bash
    gitrepoanalyzer\Scripts\activate.ps1
    ```
    ```bash
    pip install -r requirements.txt
    ```
    ```bash
    python manage.py runserver
    ```

   <strong>Note:</strong>
   <ul>
     <li>The command given above are for windows.</li>
     <li>Don't forget to close the virtual environment before closing the tool as a good   practice. The command for the same is:
  ```bash
  deactivate
  ```
  </li>
   </ul>

##  🧑🏽‍💻 Usage

The tool basically contains four section:

1. <strong>Dependency Tracker</strong>

   ![image](https://github.com/prakharmosesOK/Repository-Analyzing-Tool/assets/142619454/5c6fb662-1262-40b3-9025-3217086be0f7)

   The use have to enter the Repository link and the branch for which the dependencies are to be fetched.
   By default, tool finds the dependencies of the main branch.

2. <strong>Version Control</strong>

   ![image](https://github.com/prakharmosesOK/Repository-Analyzing-Tool/assets/142619454/69117807-3c17-4026-9fba-c65e81479d04)

   The users are required to enter the repo link in the space provided. It fetches all the commit history and version control for the given repository link.

3. <strong>Comments/DocStrings Generator</strong>

   ![image](https://github.com/prakharmosesOK/Repository-Analyzing-Tool/assets/142619454/3c84e5e3-c4b9-41d7-a3e4-8a92e935c77a)

<ul>
   <li>The user is required to enter the Repository link for which the DocStrings need to be generated.</li>
   <li>Then the tool lists down all the files in the repository, the user has to select for in which file the docstrings should be generated.</li>
   <li>The DocStrings are generated and a pull request is created to the repository which link was provided with a new branch named "GenDocStr".</li>
</ul>

4. <strong>Documentation Generator</strong>

   ![image](https://github.com/prakharmosesOK/Repository-Analyzing-Tool/assets/142619454/467b6968-58a1-434f-9b6f-e9037b258680)

<ul>
   <li>The user has to enter the repository link for which the documentation is to be generated.</li>
   <li>The tool will generate the documentation for those directories only which contain __pycache__ folder. Others will be excluded.</li>
   <li>By default behavior of Sphinix, any function name or class name starting with underscore will not be considered for documentation as it is considered private.</li>
   <li>The documentation.zip can be downloaded from the tool. To open the documentation, open "docs/build/html/index".</li>
</ul>

## ⚽ Future Goals

<ol>
  <li>Version Control can be displayed using GUI for better understanding.</li>
  <li>DocString generation can be extended beyond python files.</li>
  <li>Model generated DocStrings can be improved.</li>
</ol>

## 👷 Contributing
I welcome contributions from the community. Feel free to submit pull requests or bug reports to improve the GitHub-Repo-Analyzer.

## 🎓 Author

<p>  <a href="https://github.com/prakharmosesOK"><b>Prakhar Moses</b><a/><p/>
<p> <a href="https://github.com/prakharmoses"><b>Prakhar Moses</b><a/></p>
