# How to Install Rails Gateway on Windows

Since you are running Windows without Docker, you need to install Ruby and Rails manually.

## Step 1: Install Ruby (via Winget)
Run this command in PowerShell:

```powershell
winget install RubyInstallerTeam.RubyWithDevKit.3.2
```

**IMPORTANT:** 
1. During installation, a terminal window may pop up asking to install **MSYS2**. Press `ENTER` to accept the defaults.
2. If it asks to run `ridk install`, choose option `3` (MSYS2 and MINGW development toolchain).

## Step 2: Restart Your Terminal
**Close this terminal window** completely and open a new PowerShell one. verification:

```powershell
ruby -v
# Should show ruby 3.2.x
```

## Step 3: Install Rails
In your new terminal:

```powershell
gem install rails
```

## Step 4: Setup the Gateway
Now navigate to the rails directory and install dependencies:

```powershell
cd f:\Shopify\shopify_ai_project\rails_gateway
bundle install
```

## Step 5: Setup Database
Create the local SQLite database:

```powershell
rails db:migrate
```

## Step 6: Run the Server
Start the Rails API:

```powershell
rails server
```

The API will be available at `http://localhost:3000`.
