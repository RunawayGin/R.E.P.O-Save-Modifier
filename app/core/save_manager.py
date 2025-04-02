import json
import os
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import pad, unpad
from Crypto.Hash import HMAC, SHA1
import gzip
import sys



# Default game save password
DEFAULT_PASSWORD = "Why would you want to cheat?... :o It's no fun. :') :'D"

class SaveManager:
    """
    Handles ES3 file operations for the Repo game saves, including:
    - Decryption and encryption of ES3 files
    - Finding save files in the default location
    - Managing save file operations
    """
    
    def __init__(self):
        # Initialize default paths and settings
        self.default_save_path = self._get_save_folder()
        self.password = DEFAULT_PASSWORD
        self.should_gzip = False  # Default compression setting
        print(f"Default save path: {self.default_save_path}")
        
        # Verify the path exists
        if self.default_save_path and os.path.exists(self.default_save_path):
            print(f"Default save path exists: {os.path.exists(self.default_save_path)}")
            print(f"Contents: {os.listdir(self.default_save_path)}")
    
    def decrypt_es3(self, path, pwd=None):
        """
        Decrypts an ES3 file and returns the resulting bytes.

        Parameters:
            path (str): The file path of the ES3 file.
            pwd (str, optional): The decryption password. If not provided, uses self.password.

        Returns:
            bytes: The decrypted (and possibly decompressed) data.
        """
        # Use the class password if none is provided
        decryption_pwd = pwd or self.password

        # Read the entire file content as binary data
        with open(path, 'rb') as file_obj:
            file_bytes = file_obj.read()

        # The first 16 bytes are used as the initialization vector (IV)
        init_vector = file_bytes[:16]
        cipher_text = file_bytes[16:]

        # Derive a 16-byte AES key using PBKDF2 with the IV as the salt
        derived_key = PBKDF2(decryption_pwd, init_vector, dkLen=16, count=100,
                            prf=lambda p, s: HMAC.new(p, s, SHA1).digest())

        # Set up the AES cipher in CBC mode and decrypt the ciphertext
        aes_decipher = AES.new(derived_key, AES.MODE_CBC, init_vector)
        plaintext = unpad(aes_decipher.decrypt(cipher_text), AES.block_size)

        # If the decrypted data is GZip compressed, decompress it
        if plaintext.startswith(b'\x1f\x8b'):  # GZip magic number
            plaintext = gzip.decompress(plaintext)

        return plaintext

    def encrypt_es3_file(self, data, output_path=None, pwd=None, compress=None):
        """
        Encrypts raw data into the ES3 format.

        Parameters:
            data (bytes): The input data to be encrypted.
            output_path (str, optional): Destination file path. If provided, the encrypted data is written to the file.
            pwd (str, optional): Encryption password. Defaults to self.password if not specified.
            compress (bool, optional): Whether to GZip compress the data before encryption. Defaults to self.should_gzip.

        Returns:
            bytes or bool: Returns the encrypted data as bytes if output_path is None, 
                        otherwise returns True upon successfully writing to file.
        """
        # Set default password and compression setting if not provided
        encryption_pwd = pwd if pwd is not None else self.password
        use_compression = compress if compress is not None else self.should_gzip

        # Optionally compress the data using gzip
        if use_compression:
            data = gzip.compress(data)

        # Generate a 16-byte Initialization Vector (IV)
        iv_bytes = os.urandom(16)

        # Derive a 16-byte key using PBKDF2 with the IV as salt and HMAC-SHA1 as the pseudorandom function
        encryption_key = PBKDF2(
            encryption_pwd,
            iv_bytes,
            dkLen=16,
            count=100,
            prf=lambda p, s: HMAC.new(p, s, SHA1).digest()
        )

        # Create an AES cipher in CBC mode and encrypt the padded data
        cipher_obj = AES.new(encryption_key, AES.MODE_CBC, iv_bytes)
        padded_data = pad(data, AES.block_size)
        encrypted_bytes = cipher_obj.encrypt(padded_data)

        # Prepend the IV to the encrypted data
        final_output = iv_bytes + encrypted_bytes

        # Write the output to a file if a path is provided, else return the encrypted bytes
        if output_path:
            with open(output_path, 'wb') as file_out:
                file_out.write(final_output)
            return True

        return final_output

    def load_json_from_es3(self, file_path, password=None):
        """
        Load and parse JSON data from an ES3 encrypted file
        
        Args:
            file_path (str): Path to the ES3 file
            password (str, optional): Password for decryption. Defaults to class password.
            
        Returns:
            dict: Parsed JSON data or None if unsuccessful
        """
        try:
            # Decrypt the file
            print(f"Attempting to decrypt {file_path}")
            decrypted_data = self.decrypt_es3(file_path, password)
            
            # Convert bytes to string
            json_string = decrypted_data.decode('utf-8')
            
            # Convert decrypted data to JSON
            json_data = json.loads(json_string)
            print("Successfully loaded JSON data")
            return json_data
                
        except Exception as e:
            print(f"Error during decryption or JSON conversion: {str(e)}")
            return None

    def save_es3_from_json(self, data, file_path, password=None, should_gzip=None, create_backup=True, debug_compare=True, debug_player_stats=True):
        """
        Save JSON data back to an ES3 encrypted file
        
        Args:
            data (dict): JSON data to save
            file_path (str): Path to save the ES3 file
            password (str, optional): Password for encryption. Defaults to class password.
            should_gzip (bool, optional): Whether to compress the data. Defaults to class setting.
            create_backup (bool, optional): Whether to create a backup of the original file. Defaults to True.
            debug_compare (bool, optional): Whether to show differences between original and new data. Defaults to True.
            debug_player_stats (bool, optional): Whether to show player stats changes specifically. Defaults to True.
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Compare player stats specifically if enabled
            if debug_player_stats and os.path.exists(file_path):
                self.compare_player_stats(file_path, data)
            
            # Compare all data differences if debug is enabled
            elif debug_compare and os.path.exists(file_path):
                self.compare_save_data(file_path, data)
                
            # Convert JSON to string, then to bytes
            json_bytes = json.dumps(data).encode('utf-8')
            
            # Create backup of original file if requested
            if create_backup and os.path.exists(file_path):
                backup_path = file_path + ".backup"
                
                # Remove existing backup file if it exists
                if os.path.exists(backup_path):
                    try:
                        os.remove(backup_path)
                        print(f"Removed existing backup: {backup_path}")
                    except Exception as e:
                        print(f"Warning: Could not remove existing backup: {str(e)}")
                
                # Now create the backup
                try:
                    import shutil
                    shutil.copy2(file_path, backup_path)
                    print(f"Backup created: {backup_path}")
                except Exception as e:
                    print(f"Warning: Could not create backup: {str(e)}")
            
            # Encrypt and save the data - this will overwrite the original file
            print(f"Overwriting original file: {file_path}")
            success = self.encrypt_es3(json_bytes, file_path, password, should_gzip)
            
            if success:
                print(f"Successfully saved to: {file_path}")
                
                # Verify the saved file by decrypting it and comparing to the original data
                if debug_compare:
                    print("Verifying saved file...")
                    try:
                        saved_data = self.load_json_from_es3(file_path)
                        if saved_data == data:
                            print("✅ Verification successful: Saved data matches expected data")
                        else:
                            print("❌ Verification failed: Saved data does not match expected data")
                    except Exception as e:
                        print(f"❌ Verification error: {str(e)}")
                
                return True
            else:
                print(f"Failed to save to: {file_path}")
                return False
                
        except Exception as e:
            print(f"Error during encryption or saving: {str(e)}")
            return False
    
    def _get_save_folder(self):
        """
        Returns the default save location for Repo game files
        
        Returns:
            str: Path to the save folder
        """
        # Default location is in AppData\LocalLow\semiwork\Repo\saves
        if sys.platform == "win32":
            app_data = os.path.expandvars("%USERPROFILE%\\AppData\\LocalLow")
            save_folder = os.path.join(app_data, "semiwork", "Repo", "saves")
            return save_folder
        # For other platforms, return None as the game is Windows-only
        return None

    def list_save_files(self, folder_path=None):
        """
        Lists available save files in the specified folder
        
        Args:
            folder_path (str, optional): Path to look for save files. Defaults to default save path.
            
        Returns:
            list: List of tuples (display_name, save_folder_path, full_save_file_path)
        """
        if folder_path is None:
            folder_path = self.default_save_path
            
        if not folder_path or not os.path.exists(folder_path):
            print(f"Save folder does not exist: {folder_path}")
            return []
        
        # Find all save folders
        save_folders = []
        
        try:
            print(f"Looking for save files in: {folder_path}")
            
            # Get subdirectories in the saves folder
            subdirs = [d for d in os.listdir(folder_path) 
                      if os.path.isdir(os.path.join(folder_path, d))]
            
            print(f"Found subdirectories: {subdirs}")
            
            # Check each subdirectory for .Es3 files with matching names
            for subdir in subdirs:
                subdir_path = os.path.join(folder_path, subdir)
                expected_file = f"{subdir}.Es3"
                full_path = os.path.join(subdir_path, expected_file)
                
                print(f"Checking for {full_path}")
                
                # If the matching .Es3 file exists, add it to the list
                if os.path.exists(full_path):
                    print(f"Found save file: {full_path}")
                    # Add (display_name, save_folder_path, full_save_file_path)
                    save_folders.append((subdir, subdir_path, full_path))
        
        except Exception as e:
            print(f"Error listing save files: {str(e)}")
        
        # Sort by name (which should put newest first if they follow date naming convention)
        save_folders.sort(reverse=True)
        
        print(f"Found {len(save_folders)} save files")
        
        return save_folders

    def create_temp_json(self, file_path, output_dir=None):
        """
        Create a temporary JSON file from an ES3 save for backup/inspection
        
        Args:
            file_path (str): Path to the ES3 file
            output_dir (str, optional): Directory to save the JSON file. Defaults to the same directory.
            
        Returns:
            str: Path to the created JSON file, or None if unsuccessful
        """
        json_data = self.load_json_from_es3(file_path)
        
        if json_data is None:
            return None
            
        # Create output path
        if output_dir is None:
            output_dir = os.path.dirname(file_path)
            
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        output_file = os.path.join(output_dir, base_name + "_temp.json")
        
        # Save as JSON file
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=4)
            return output_file
        except Exception as e:
            print(f"Error saving temporary JSON: {str(e)}")
            return None
        
    def compare_save_data(self, file_path, new_data):
        """
        Compares the original save file data with the new data to be saved
        and prints out the differences.
        
        Args:
            file_path (str): Path to the original ES3 file
            new_data (dict): New JSON data to be saved
            
        Returns:
            bool: True if differences were found, False if files are identical
        """
        try:
            # Load the original data
            print(f"Loading original file for comparison: {file_path}")
            original_data = self.load_json_from_es3(file_path)
            
            if original_data is None:
                print("Failed to load original data for comparison")
                return False
                
            # Find differences
            print("Comparing original data with new data...")
            differences = self._find_dict_differences(original_data, new_data)
            
            if not differences:
                print("No differences found between original and new data")
                return False
                
            # Print differences
            print("\n=== DIFFERENCES DETECTED ===")
            for diff in differences:
                path, old_value, new_value = diff
                print(f"Path: {path}")
                print(f"  Original: {old_value}")
                print(f"  New:      {new_value}")
            print("=== END OF DIFFERENCES ===\n")
            
            return True
                
        except Exception as e:
            print(f"Error during comparison: {str(e)}")
            return False
            
    def _find_dict_differences(self, dict1, dict2, path=""):
        """
        Recursively finds differences between two dictionaries
        
        Args:
            dict1 (dict): First dictionary
            dict2 (dict): Second dictionary
            path (str): Current path in the dictionary (for reporting)
            
        Returns:
            list: List of differences as (path, value1, value2) tuples
        """
        differences = []
        
        # Helper to process all keys from both dictionaries
        all_keys = set(dict1.keys()) | set(dict2.keys())
        
        for key in all_keys:
            current_path = f"{path}.{key}" if path else key
            
            # Key in dict1 but not in dict2
            if key not in dict2:
                differences.append((current_path, dict1[key], "NOT PRESENT"))
                continue
                
            # Key in dict2 but not in dict1
            if key not in dict1:
                differences.append((current_path, "NOT PRESENT", dict2[key]))
                continue
                
            # Both have the key, compare values
            value1 = dict1[key]
            value2 = dict2[key]
            
            # If both are dictionaries, recurse
            if isinstance(value1, dict) and isinstance(value2, dict):
                differences.extend(self._find_dict_differences(value1, value2, current_path))
            # If lists, compare them (simplified, doesn't check nested dicts in lists)
            elif isinstance(value1, list) and isinstance(value2, list):
                if value1 != value2:
                    differences.append((current_path, value1, value2))
            # Simple value comparison
            elif value1 != value2:
                differences.append((current_path, value1, value2))
        
        return differences

    def compare_player_stats(self, file_path, new_data):
        """
        Specifically compares player statistics between the original save file and new data
        
        Args:
            file_path (str): Path to the original ES3 file
            new_data (dict): New JSON data to be saved
            
        Returns:
            bool: True if player-related differences were found, False otherwise
        """
        try:
            # Load the original data
            print(f"Loading original file for player stats comparison: {file_path}")
            original_data = self.load_json_from_es3(file_path)
            
            if original_data is None:
                print("Failed to load original data for comparison")
                return False

            # Extract player-related information from both datasets
            player_differences = []
            
            # Check player names changes
            if ("playerNames" in original_data and "value" in original_data["playerNames"] and
                "playerNames" in new_data and "value" in new_data["playerNames"]):
                
                original_names = original_data["playerNames"]["value"]
                new_names = new_data["playerNames"]["value"]
                
                # Find player IDs from both dictionaries
                all_player_ids = set(original_names.keys()) | set(new_names.keys())
                
                for player_id in all_player_ids:
                    if player_id in original_names and player_id in new_names:
                        if original_names[player_id] != new_names[player_id]:
                            player_differences.append((
                                f"Player Name ({player_id})",
                                original_names[player_id],
                                new_names[player_id]
                            ))
                    elif player_id in original_names:
                        player_differences.append((
                            f"Player Name ({player_id})",
                            original_names[player_id],
                            "REMOVED"
                        ))
                    else:
                        player_differences.append((
                            f"Player Name ({player_id})",
                            "NOT PRESENT",
                            new_names[player_id]
                        ))
            
            # Check dictionaries that contain player data
            if ("dictionaryOfDictionaries" in original_data and "value" in original_data["dictionaryOfDictionaries"] and
                "dictionaryOfDictionaries" in new_data and "value" in new_data["dictionaryOfDictionaries"]):
                
                original_dict = original_data["dictionaryOfDictionaries"]["value"]
                new_dict = new_data["dictionaryOfDictionaries"]["value"]
                
                # Player-related dictionaries to check
                player_dicts = [
                    "playerHealth",
                    "playerUpgradeHealth",
                    "playerUpgradeStamina",
                    "playerUpgradeExtraJump", 
                    "playerUpgradeLaunch",
                    "playerUpgradeMapPlayerCount",
                    "playerUpgradeSpeed",
                    "playerUpgradeStrength",
                    "playerUpgradeRange",
                    "playerUpgradeThrow"
                ]
                
                # Compare values for each player in each dictionary
                for dict_name in player_dicts:
                    if dict_name in original_dict and dict_name in new_dict:
                        # Get all player IDs from both dictionaries
                        all_player_ids = set(original_dict[dict_name].keys()) | set(new_dict[dict_name].keys())
                        
                        for player_id in all_player_ids:
                            if player_id in original_dict[dict_name] and player_id in new_dict[dict_name]:
                                if original_dict[dict_name][player_id] != new_dict[dict_name][player_id]:
                                    player_differences.append((
                                        f"{dict_name} ({player_id})",
                                        original_dict[dict_name][player_id],
                                        new_dict[dict_name][player_id]
                                    ))
                            elif player_id in original_dict[dict_name]:
                                player_differences.append((
                                    f"{dict_name} ({player_id})",
                                    original_dict[dict_name][player_id],
                                    "REMOVED"
                                ))
                            else:
                                player_differences.append((
                                    f"{dict_name} ({player_id})",
                                    "NOT PRESENT",
                                    new_dict[dict_name][player_id]
                                ))
            
            # Check for changes in items
            item_dicts = [
                "itemsPurchased",
                "itemsPurchasedTotal", 
                "itemsUpgradesPurchased"
            ]
            
            if "dictionaryOfDictionaries" in original_data and "value" in original_data["dictionaryOfDictionaries"] and \
            "dictionaryOfDictionaries" in new_data and "value" in new_data["dictionaryOfDictionaries"]:
                
                original_dict = original_data["dictionaryOfDictionaries"]["value"]
                new_dict = new_data["dictionaryOfDictionaries"]["value"]
                
                for dict_name in item_dicts:
                    if dict_name in original_dict and dict_name in new_dict:
                        # Get all item names from both dictionaries
                        all_items = set(original_dict[dict_name].keys()) | set(new_dict[dict_name].keys())
                        
                        for item_name in all_items:
                            if item_name in original_dict[dict_name] and item_name in new_dict[dict_name]:
                                if original_dict[dict_name][item_name] != new_dict[dict_name][item_name]:
                                    player_differences.append((
                                        f"{dict_name} ({item_name})",
                                        original_dict[dict_name][item_name],
                                        new_dict[dict_name][item_name]
                                    ))
                            elif item_name in original_dict[dict_name]:
                                player_differences.append((
                                    f"{dict_name} ({item_name})",
                                    original_dict[dict_name][item_name],
                                    "REMOVED"
                                ))
                            else:
                                player_differences.append((
                                    f"{dict_name} ({item_name})",
                                    "NOT PRESENT",
                                    new_dict[dict_name][item_name]
                                ))
            
            # Print player differences
            if player_differences:
                print("\n=== PLAYER STATS CHANGES ===")
                for diff in player_differences:
                    stat_name, old_value, new_value = diff
                    print(f"Stat: {stat_name}")
                    print(f"  Original: {old_value}")
                    print(f"  New:      {new_value}")
                print("=== END OF PLAYER STATS CHANGES ===\n")
                return True
            else:
                print("No player-related changes detected")
                
                # Debug: Show a sample of player data to verify we're reading correctly
                print("\n=== PLAYER DATA SAMPLE (FOR DEBUGGING) ===")
                
                # Sample player names
                if ("playerNames" in original_data and "value" in original_data["playerNames"]):
                    print("Player Names:")
                    for player_id, name in original_data["playerNames"]["value"].items():
                        print(f"  {player_id}: {name}")
                
                # Sample player health if available
                if ("dictionaryOfDictionaries" in original_data and 
                    "value" in original_data["dictionaryOfDictionaries"] and
                    "playerHealth" in original_data["dictionaryOfDictionaries"]["value"]):
                    print("\nPlayer Health:")
                    health_dict = original_data["dictionaryOfDictionaries"]["value"]["playerHealth"]
                    for player_id, health in health_dict.items():
                        print(f"  {player_id}: {health}")
                        
                # Sample player upgrades if available
                if ("dictionaryOfDictionaries" in original_data and 
                    "value" in original_data["dictionaryOfDictionaries"] and
                    "playerUpgradeHealth" in original_data["dictionaryOfDictionaries"]["value"]):
                    print("\nPlayer Health Upgrades:")
                    upgrade_dict = original_data["dictionaryOfDictionaries"]["value"]["playerUpgradeHealth"]
                    for player_id, level in upgrade_dict.items():
                        print(f"  {player_id}: Level {level}")
                
                print("=== END OF PLAYER DATA SAMPLE ===\n")
                return False
                
        except Exception as e:
            print(f"Error during player stats comparison: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    def create_temp_json(self, file_path, output_dir=None):
        """
        Create a temporary JSON file from an ES3 save for backup/inspection
        
        Args:
            file_path (str): Path to the ES3 file
            output_dir (str, optional): Directory to save the JSON file. Defaults to the same directory.
            
        Returns:
            str: Path to the created JSON file, or None if unsuccessful
        """
        json_data = self.load_json_from_es3(file_path)
        
        if json_data is None:
            return None
            
        # Create output path
        if output_dir is None:
            output_dir = os.path.dirname(file_path)
            
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        output_file = os.path.join(output_dir, base_name + "_temp.json")
        
        # Save as JSON file
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=4)
            return output_file
        except Exception as e:
            print(f"Error saving temporary JSON: {str(e)}")
            return None
    
    def create_new_game_save(self, team_name="R.E.P.O"):
        """
        Create a new game save from scratch
        
        Args:
            team_name (str, optional): Team name. Defaults to "Default Team".
            
        Returns:
            tuple: (folder_path, file_path, game_save) or (None, None, None) if unsuccessful
        """
        from .data_models import GameSave
        import datetime
        
        try:
            # Create a new game save
            game_save, raw_data = GameSave.create_new_game(team_name)
            
            # Generate folder name
            folder_name = game_save.get_save_folder_name()
            
            # Create the save folder
            save_folder = os.path.join(self.default_save_path, folder_name)
            os.makedirs(save_folder, exist_ok=True)
            
            # Create file path
            file_path = os.path.join(save_folder, folder_name + ".Es3")
            
            # Save the raw data to the file
            json_string = json.dumps(raw_data)
            success = self.encrypt_es3(json_string.encode('utf-8'), file_path, self.password, self.should_gzip)
            
            if success:
                print(f"New game save created at: {file_path}")
                return save_folder, file_path, game_save
            else:
                print("Failed to save new game")
                return None, None, None
                
        except Exception as e:
            print(f"Error creating new game save: {str(e)}")
            import traceback
            traceback.print_exc()
            return None, None, None