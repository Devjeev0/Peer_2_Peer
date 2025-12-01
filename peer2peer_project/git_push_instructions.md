# How to Push Your Code to GitHub

Since `git` is not currently recognized in your terminal, follow these steps to install Git and push your project.

## Step 1: Install Git
1.  **Download Git**: Go to [git-scm.com/downloads](https://git-scm.com/downloads) and download the Windows installer.
2.  **Install**: Run the installer. You can stick to the default settings for most options.
    *   **Important**: On the screen "Adjusting your PATH environment", make sure "Git from the command line and also from 3rd-party software" is selected.
3.  **Verify**: After installation, close your current terminal/VS Code and open a new one. Type `git --version` to confirm it's installed.

## Step 2: Initialize Git in Your Project
Once Git is installed and recognized:
1.  Open your terminal in the project folder: `e:\belief\peer2peer_project`
2.  Run the following commands:
    ```bash
    git init
    git add .
    git commit -m "Initial commit of Peer2Peer Lending Platform"
    ```

## Step 3: Create a Repository on GitHub
1.  Go to [github.com/new](https://github.com/new).
2.  **Repository name**: Enter a name (e.g., `peer2peer-lending`).
3.  **Visibility**: Choose Public or Private.
4.  **Initialize this repository with**: Leave these unchecked (no README, no .gitignore) since we are importing an existing repository.
5.  Click **Create repository**.

## Step 4: Link and Push
1.  Copy the URL of your new repository (e.g., `https://github.com/YOUR_USERNAME/peer2peer-lending.git`).
2.  Back in your terminal, run:
    ```bash
    git branch -M main
    git remote add origin https://github.com/YOUR_USERNAME/peer2peer-lending.git
    git push -u origin main
    ```
    *(Replace the URL with your actual repository URL)*

## Step 5: Authenticate
*   If prompted, sign in with your GitHub credentials. You may need to use a Personal Access Token or authorize via the browser.

---
**Note**: If you already have Git installed but it's not showing up, try restarting your terminal or computer.
