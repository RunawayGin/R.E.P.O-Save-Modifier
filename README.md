# R.E.P.O Save Modifier
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-PySide6-informational.svg)](https://doc.qt.io/qtforpython/)

  <img src="https://github.com/user-attachments/assets/7c2b63ab-fdea-4cd7-8a98-7248e2878e8f" alt="Logo" width="500"/><br>

A desktop application built with Python and PySide6 for editing save files for the game [Repo](https://store.steampowered.com/app/3241660/REPO/).



## 📸 Screenshots
<details>
  <summary>Click to view screenshots</summary>

  <img src="https://github.com/user-attachments/assets/38197bcd-ab21-4510-aa23-03ae346a0cda" alt="Home Screen" width="500"/><br>
  <img src="https://github.com/user-attachments/assets/0fc365e9-7ca3-44b1-825b-0e878406178a" alt="Game Stats" width="500"/><br>
  <img src="https://github.com/user-attachments/assets/5ee8102e-9958-4fef-8267-3110bccf9523" alt="Player Stats" width="500"/><br>
  <img src="https://github.com/user-attachments/assets/344aee10-2e7a-4ce7-8f35-6a9b2c5e532c" alt="Advanced Player Stats" width="500"/><br>
  <img src="https://github.com/user-attachments/assets/0bc8e457-8919-4aea-bfe8-a9628034690a" alt="Add Cached Users" width="500"/><br>
  <img src="https://github.com/user-attachments/assets/cc7696ba-b862-4da2-91a1-06f59577b5fe" alt="Add Users Steam ID" width="500"/><br>
  <img src="https://github.com/user-attachments/assets/64c1f3c0-b5a0-42f6-9d05-f4ced9487d45" alt="items editor" width="500"/>

</details>





## Overview

R.E.P.O Save Modifier provides a user-friendly graphical interface to load, modify, and save your Repo game progress. It decrypts the game's `.Es3` save files, allows you to edit various parameters, and then re-encrypts them for use in the game.

## Features ✨

*   **Load & Decrypt:** Automatically detects Repo save files in the default location (`%USERPROFILE%\AppData\LocalLow\semiwork\Repo\saves`) or allows browsing for `.Es3` files. Decrypts save files using the game's standard encryption method.


*   **Edit Game Data:**
    *   **Game Stats:** Modify current level, currency, lives, charging station charge, and total haul value (in thousands)
    *   **Team Name:** Change your team's name.
    
*   **Edit Player Data:**
    *   **Player Stats:** Adjust individual player health.
    *   **Player Upgrades:** Modify levels for all player upgrades (Health, Stamina, Speed, Strength, Jump, Range, etc.).
  
*   **Edit Items:**
    *   Modify quantities of purchased items (Weapons, Grenades, Utility, etc.).
    *   Modify levels of purchased upgrade items.
  
*   **Player Management:**
    *   **Add Players:** Add new players to the save using their 17-digit Steam ID.
    *   **Steam Integration:** Automatically fetches player usernames and avatars from Steam Community profiles.
    *   **User Cache:** Remembers previously added players for quick re-adding across different saves.
    
*   **Save & Encrypt:** Encrypts the modified data back into the `.Es3` format compatible with the game.
*   **Automatic Backups:** Creates a `.backup` copy of the original save file before overwriting.
*   **Modern UI:** Clean and intuitive interface built with PySide6, featuring custom widgets and theming.

## Requirements ⚙️

*   **Python:** 3.8 or newer
*   **Operating System:** Primarily tested on Windows (due to default save path detection). May work on other systems if save files are browsed manually.
*   **Dependencies:**
    *   `PySide6`: For the graphical user interface.
    *   `pycryptodomex`: For AES encryption/decryption.
    *   `requests`: For fetching Steam profile data.

## Installation 💾

You can either download a pre-built release (if available) or run from source.

**1. From Release (Recommended)**

*   Go to the [Releases](https://github.com/your-username/repo-save-modifier/releases) page of this repository. <!-- Update link -->
*   Download the latest release suitable for your operating system (e.g., `.exe` for Windows).
*   Run the downloaded executable.

**2. From Source**

*   **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/repo-save-modifier.git <!-- Update link -->
    cd repo-save-modifier
    ```
*   **Create a virtual environment (Recommended):**
    ```bash
    python -m venv venv
    # Activate the environment
    # Windows:
    venv\Scripts\activate
    # macOS/Linux:
    source venv/bin/activate
    ```
*   **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(If `requirements.txt` is missing, you can generate it from the source files or install manually: `pip install PySide6 pycryptodomex requests`)*
*   **Run the application:**
    ```bash
    python main.py
    ```

## Usage 🚀

1.  **Launch:** Run the application (`main.py` or the executable).
2.  **Load Save:**
    *   The application attempts to automatically list save files found in the default Repo save directory. Select a save from the list on the **Home** page and click "Load Selected Save".
    *   Alternatively, click "Browse Files" to manually locate and open an `.Es3` save file.
3.  **Edit:**
    *   Navigate through the sidebar tabs (**Game Stats**, **Player Stats**, **Items**) to view and modify data.
    *   Use the provided input fields, sliders, and buttons to make changes.
4.  **Add Players (Optional):**
    *   Go to the **Player Stats** tab.
    *   Click "Add Player".
    *   Use the dialog to select cached users or add a new user by fetching their data via Steam ID.
5.  **Save Changes:**
    *   Click the "Save Changes" button in the sidebar.
    *   Your modifications will be saved to the loaded `.Es3` file, and a backup of the original file will be created with a `.backup` extension in the same directory.
6.  **Exit:** Close the application.

## Technical Details 🤓

*   **Encryption:** The application uses AES-128-CBC for encryption/decryption, deriving the key from the game's default password and the file's Initialization Vector (IV) using PBKDF2 (HMAC-SHA1).
*   **Compression:** Handles GZip compression/decompression if present in the save data.
*   **Steam API:** Fetches public profile data (`?xml=1`) from `steamcommunity.com` to get usernames and avatar URLs. Avatar images are cached locally in `resources/cache`.

## Disclaimer ⚠️

Modifying save files can potentially corrupt your game progress or lead to unexpected behavior in the game. Always use this tool responsibly. The automatic backup feature is provided, but it's always a good idea to manually back up your saves before making significant changes. This tool is not affiliated with the developers of Repo.

## Contributing 🤝

Contributions are welcome! If you find a bug or have a feature request, please open an issue. If you'd like to contribute code, please fork the repository and submit a pull request.

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. <!-- Make sure you add a LICENSE file (e.g., containing the MIT License text) -->

## Acknowledgements 🙏

*   The developers of the game Repo (`semiwork`).
*   The developers of the libraries used (PySide6, PyCryptodome, Requests).