class PlayerData:
    """
    Represents a player in the game with their stats and properties
    """
    
    def __init__(self, player_id, data=None):
        """
        Initialize player data
        
        Args:
            player_id (str): The player's unique identifier
            data (dict, optional): Game save data dictionary
        """
        self.player_id = player_id
        self.name = "Unknown"
        self.health = 100
        self.max_health = 100
        
        # Upgrades with default values
        self.upgrades = {
            "health": 0,
            "stamina": 0,
            "extraJump": 0,
            "launch": 0,
            "mapPlayerCount": 0,
            "speed": 0,
            "strength": 0,
            "range": 0,
            "throw": 0
        }
        
        # Load data if provided
        if data:
            self.load_from_data(data)
    
    def load_from_data(self, data):
        """
        Load player data from game save dictionary
        
        Args:
            data (dict): Game save data dictionary
        """
        # Load player name
        if "playerNames" in data and "value" in data["playerNames"]:
            # Debug print to check
            print(f"Loading player name for ID {self.player_id} from data: {data['playerNames']['value']}")
            
            if self.player_id in data["playerNames"]["value"]:
                self.name = data["playerNames"]["value"].get(self.player_id, "Unknown")
                # Debug print
                print(f"Loaded player name: {self.name}")
        
        # Load player health
        if "dictionaryOfDictionaries" in data and "value" in data["dictionaryOfDictionaries"]:
            dict_values = data["dictionaryOfDictionaries"]["value"]
            
            # Health
            if "playerHealth" in dict_values:
                self.health = dict_values["playerHealth"].get(self.player_id, 100)
            
            # Load upgrades
            upgrade_mappings = {
                "playerUpgradeHealth": "health",
                "playerUpgradeStamina": "stamina",
                "playerUpgradeExtraJump": "extraJump",
                "playerUpgradeLaunch": "launch",
                "playerUpgradeMapPlayerCount": "mapPlayerCount", 
                "playerUpgradeSpeed": "speed",
                "playerUpgradeStrength": "strength",
                "playerUpgradeRange": "range",
                "playerUpgradeThrow": "throw"
            }
            
            for game_key, model_key in upgrade_mappings.items():
                if game_key in dict_values and self.player_id in dict_values[game_key]:
                    self.upgrades[model_key] = dict_values[game_key][self.player_id]
            
            # Calculate max health based on health upgrade
            self.max_health = 100 + (self.upgrades["health"] * 20)
    
    def update_data(self, data):
        """
        Update game save data with this player's information
        
        Args:
            data (dict): Game save data dictionary to update
        """
        # Update health
        if "dictionaryOfDictionaries" in data and "value" in data["dictionaryOfDictionaries"]:
            dict_values = data["dictionaryOfDictionaries"]["value"]
            
            if "playerHealth" in dict_values:
                dict_values["playerHealth"][self.player_id] = self.health
            
            # Update upgrades
            upgrade_mappings = {
                "playerUpgradeHealth": "health",
                "playerUpgradeStamina": "stamina", 
                "playerUpgradeExtraJump": "extraJump",
                "playerUpgradeLaunch": "launch",
                "playerUpgradeMapPlayerCount": "mapPlayerCount",
                "playerUpgradeSpeed": "speed",
                "playerUpgradeStrength": "strength",
                "playerUpgradeRange": "range",
                "playerUpgradeThrow": "throw"
            }
            
            for game_key, model_key in upgrade_mappings.items():
                if game_key in dict_values:
                    dict_values[game_key][self.player_id] = self.upgrades[model_key]
                    
        # Update name if needed
        if "playerNames" in data and "value" in data["playerNames"]:
            data["playerNames"]["value"][self.player_id] = self.name
            
        return data


class GameSave:
    """
    Represents the full game save file with all players and items
    """
    
    def __init__(self, data=None):
        """
        Initialize the game save
        
        Args:
            data (dict, optional): Raw game save data
        """
        self.team_name = "Default Team"
        
        # Initialize run stats with default values
        self.run_stats = {
            "level": 1,
            "currency": 0,
            "lives": 3,
            "chargingStationCharge": 0,
            "totalHaul": 0,
            "save level": 0
        }
        
        self.players = {}  # Dictionary of PlayerData objects
        self.items = {
            "purchased": {},
            "purchasedTotal": {},
            "upgradesPurchased": {}
        }
        
        # Raw data reference for when adding players
        self.raw_data = None
        
        # Load data if provided
        if data:
            self.raw_data = data
            self.load_data(data)
            
    def add_player(self, player_id, player_name):
        """
        Add a new player to the game save
        
        Args:
            player_id (str): Steam player ID
            player_name (str): Player display name
            
        Returns:
            PlayerData: The newly created player data object
        """
        print(f"GameSave: Adding player {player_id} with name '{player_name}'")
        
        # Verify we have a valid name
        if not player_name or player_name.strip() == "":
            player_name = f"Player_{player_id[-4:]}"
            print(f"Empty player name detected, using fallback: {player_name}")
        
        # Ensure we have the raw data structure
        if not self.raw_data:
            raise ValueError("Cannot add player: No raw data structure available")
        
        # Add player to player names dictionary
        if "playerNames" in self.raw_data and "value" in self.raw_data["playerNames"]:
            # Check if we already have 6 players (maximum allowed)
            current_players = len(self.raw_data["playerNames"]["value"])
            if current_players >= 6:
                raise ValueError("Cannot add player: Maximum of 6 players already reached")
                
            # Add to player names dictionary
            self.raw_data["playerNames"]["value"][player_id] = player_name
            print(f"Added player name to raw data: {player_id} -> '{player_name}'")
            
            # Verify it was added correctly
            print(f"Verification - name in raw data: '{self.raw_data['playerNames']['value'].get(player_id, 'NOT FOUND')}'")
            
            # Ensure player exists in all required dictionaries in dictionaryOfDictionaries
            if "dictionaryOfDictionaries" in self.raw_data and "value" in self.raw_data["dictionaryOfDictionaries"]:
                dict_values = self.raw_data["dictionaryOfDictionaries"]["value"]
                
                # Add player to health dictionary with default health of 100
                if "playerHealth" in dict_values:
                    dict_values["playerHealth"][player_id] = 100
                else:
                    dict_values["playerHealth"] = {player_id: 100}
                
                # Add player to all upgrade dictionaries with default value of 0
                upgrade_dicts = [
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
                
                for dict_name in upgrade_dicts:
                    if dict_name in dict_values:
                        dict_values[dict_name][player_id] = 0
                    else:
                        dict_values[dict_name] = {player_id: 0}
                
                # Add to crown dictionary if it exists
                if "playerHasCrown" in dict_values:
                    dict_values["playerHasCrown"][player_id] = 0
            
            # Create a PlayerData object for the new player
            new_player = PlayerData(player_id, self.raw_data)
            
            # Force set the name if necessary
            if new_player.name != player_name:
                print(f"Warning: PlayerData name mismatch, forcing name: '{player_name}'")
                new_player.name = player_name
            
            # Verify player name was loaded correctly
            print(f"Verification - PlayerData name: '{new_player.name}'")
            
            # Add to the players dictionary
            self.players[player_id] = new_player
            
            return new_player
        else:
            raise ValueError("Cannot add player: Invalid save structure")
    
    @classmethod
    def create_new_game(cls, team_name="R.E.P.O."):
        """
        Create a new game save from scratch
        
        Args:
            team_name (str, optional): Team name. Defaults to "R.E.P.O. Team".
            
        Returns:
            tuple: (game_save, raw_data)
        """
        import datetime
        
        # Create basic save structure
        raw_data = {
            "dictionaryOfDictionaries": {
                "__type": "System.Collections.Generic.Dictionary`2[[System.String, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089],[System.Collections.Generic.Dictionary`2[[System.String, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089],[System.Int32, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]], mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]],mscorlib",
                "value": {
                    "runStats": {
                        "level": 1,
                        "currency": 0,
                        "lives": 0,
                        "chargingStationCharge": 0,
                        "totalHaul": 0,
                        "save level": 0
                    },
                    "playerHealth": {},
                    "playerUpgradeHealth": {},
                    "playerUpgradeStamina": {},
                    "playerUpgradeExtraJump": {},
                    "playerUpgradeLaunch": {},
                    "playerUpgradeMapPlayerCount": {},
                    "playerUpgradeSpeed": {},
                    "playerUpgradeStrength": {},
                    "playerUpgradeRange": {},
                    "playerUpgradeThrow": {},
                    "playerHasCrown": {},
                    "itemsPurchased": {},
                    "itemsPurchasedTotal": {},
                    "itemsUpgradesPurchased": {},
                    "itemBatteryUpgrades": {},
                    "item": {},
                    "itemStatBattery": {}
                }
            },
            "playerNames": {
                "__type": "System.Collections.Generic.Dictionary`2[[System.String, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089],[System.String, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]],mscorlib",
                "value": {}
            },
            "timePlayed": {
                "__type": "float",
                "value": 0.0
            },
            "dateAndTime": {
                "__type": "string",
                "value": datetime.datetime.now().strftime("%Y-%m-%d")
            },
            "teamName": {
                "__type": "string",
                "value": team_name
            }
        }
        
        # Initialize standard item lists
        common_items = [
            "Item Cart Medium", "Item Cart Small", "Item Drone Battery", "Item Drone Feather",
            "Item Drone Indestructible", "Item Drone Torque", "Item Drone Zero Gravity",
            "Item Extraction Tracker", "Item Grenade Duct Taped", "Item Grenade Explosive",
            "Item Grenade Human", "Item Grenade Shockwave", "Item Grenade Stun", "Item Gun Handgun",
            "Item Gun Shotgun", "Item Gun Tranq", "Item Health Pack Large", "Item Health Pack Medium",
            "Item Health Pack Small", "Item Melee Baseball Bat", "Item Melee Frying Pan",
            "Item Melee Inflatable Hammer", "Item Melee Sledge Hammer", "Item Melee Sword",
            "Item Mine Explosive", "Item Mine Shockwave", "Item Mine Stun", "Item Orb Zero Gravity",
            "Item Power Crystal", "Item Rubber Duck", "Item Upgrade Map Player Count",
            "Item Upgrade Player Energy", "Item Upgrade Player Extra Jump", "Item Upgrade Player Grab Range",
            "Item Upgrade Player Grab Strength", "Item Upgrade Player Health", 
            "Item Upgrade Player Sprint Speed", "Item Upgrade Player Tumble Launch", "Item Valuable Tracker"
        ]
        
        # Initialize all item dictionaries with zeros
        for item_name in common_items:
            raw_data["dictionaryOfDictionaries"]["value"]["itemsPurchased"][item_name] = 0
            raw_data["dictionaryOfDictionaries"]["value"]["itemsPurchasedTotal"][item_name] = 0
            raw_data["dictionaryOfDictionaries"]["value"]["itemsUpgradesPurchased"][item_name] = 0
            raw_data["dictionaryOfDictionaries"]["value"]["itemBatteryUpgrades"][item_name] = 0
            raw_data["dictionaryOfDictionaries"]["value"]["item"][item_name] = 0
            raw_data["dictionaryOfDictionaries"]["value"]["itemStatBattery"][item_name] = 0
        
        # Create GameSave instance
        game_save = cls(raw_data)
        
        return game_save, raw_data
        
    def get_save_folder_name(self):
        """
        Generate a folder name for saving this game save
        
        Returns:
            str: Folder name formatted like REPO_SAVE_YYYY_MM_DD_HH_MM_SS
        """
        import datetime
        
        # Get current date and time
        now = datetime.datetime.now()
        
        # Format as REPO_SAVE_YYYY_MM_DD_HH_MM_SS
        folder_name = now.strftime("REPO_SAVE_%Y_%m_%d_%H_%M_%S")
        
        return folder_name
    
    def load_data(self, data):
        """
        Load game save data from dictionary
        
        Args:
            data (dict): Raw game save data
        """
        # Load team name
        if "teamName" in data and "value" in data["teamName"]:
            self.team_name = data["teamName"]["value"]
        
        # Load run stats
        if ("dictionaryOfDictionaries" in data and 
            "value" in data["dictionaryOfDictionaries"] and
            "runStats" in data["dictionaryOfDictionaries"]["value"]):
            self.run_stats = data["dictionaryOfDictionaries"]["value"]["runStats"]
        
        # Load players
        self._load_players(data)
        
        # Load items
        self._load_items(data)
    
    def _load_players(self, data):
        """
        Load all players from data
        
        Args:
            data (dict): Raw game save data
        """
        self.players = {}
        
        # Find all player IDs from health or names
        player_ids = set()
        
        # Check player health dictionary
        if ("dictionaryOfDictionaries" in data and 
            "value" in data["dictionaryOfDictionaries"] and
            "playerHealth" in data["dictionaryOfDictionaries"]["value"]):
            player_ids.update(data["dictionaryOfDictionaries"]["value"]["playerHealth"].keys())
        
        # Check player names dictionary
        if "playerNames" in data and "value" in data["playerNames"]:
            player_ids.update(data["playerNames"]["value"].keys())
        
        # Create PlayerData objects for each ID
        for player_id in player_ids:
            self.players[player_id] = PlayerData(player_id, data)
    
    def _load_items(self, data):
        """
        Load all items from data
        
        Args:
            data (dict): Raw game save data
        """
        if "dictionaryOfDictionaries" in data and "value" in data["dictionaryOfDictionaries"]:
            dict_values = data["dictionaryOfDictionaries"]["value"]
            
            # Items purchased
            if "itemsPurchased" in dict_values:
                self.items["purchased"] = dict_values["itemsPurchased"]
            
            # Items purchased total
            if "itemsPurchasedTotal" in dict_values:
                self.items["purchasedTotal"] = dict_values["itemsPurchasedTotal"]
            
            # Items upgrades purchased
            if "itemsUpgradesPurchased" in dict_values:
                self.items["upgradesPurchased"] = dict_values["itemsUpgradesPurchased"]
    
    def update_data(self, data):
        """
        Update the raw game data with this save's information
        
        Args:
            data (dict): Raw game save data to update
            
        Returns:
            dict: Updated raw game save data
        """
        # Update team name
        if "teamName" in data:
            data["teamName"]["value"] = self.team_name
        
        # Update run stats
        if ("dictionaryOfDictionaries" in data and 
            "value" in data["dictionaryOfDictionaries"] and
            "runStats" in data["dictionaryOfDictionaries"]["value"]):
            data["dictionaryOfDictionaries"]["value"]["runStats"] = self.run_stats
        
        # Update players
        for player in self.players.values():
            player.update_data(data)
        
        # Update items
        if "dictionaryOfDictionaries" in data and "value" in data["dictionaryOfDictionaries"]:
            dict_values = data["dictionaryOfDictionaries"]["value"]
            
            # Items purchased
            if "itemsPurchased" in dict_values:
                dict_values["itemsPurchased"] = self.items["purchased"]
            
            # Items purchased total
            if "itemsPurchasedTotal" in dict_values:
                dict_values["itemsPurchasedTotal"] = self.items["purchasedTotal"]
            
            # Items upgrades purchased
            if "itemsUpgradesPurchased" in dict_values:
                dict_values["itemsUpgradesPurchased"] = self.items["upgradesPurchased"]
        
        return data
    
    # Run Stats Methods
    
    def get_run_stat(self, stat_name, default=0):
        """
        Get a run stat value
        
        Args:
            stat_name (str): The name of the run stat
            default (any, optional): Default value if stat doesn't exist. Defaults to 0.
            
        Returns:
            The stat value or default if not found
        """
        return self.run_stats.get(stat_name, default)
    
    def set_run_stat(self, stat_name, value):
        """
        Set a run stat value
        
        Args:
            stat_name (str): The name of the run stat
            value: The new value
            
        Returns:
            bool: True if successful, False if not
        """
        if stat_name in self.run_stats or isinstance(self.run_stats, dict):
            self.run_stats[stat_name] = value
            return True
        return False
    
    def get_all_run_stats(self):
        """
        Get all run stats
        
        Returns:
            dict: A copy of the run stats dictionary
        """
        return self.run_stats.copy()
    
    # Convenience methods for common run stats
    
    def get_level(self):
        """Get the current level"""
        return self.get_run_stat("level", 1)
    
    def set_level(self, level):
        """Set the current level"""
        return self.set_run_stat("level", level)
    
    def get_currency(self):
        """Get the current currency"""
        return self.get_run_stat("currency", 0)
    
    def set_currency(self, amount):
        """Set the current currency"""
        return self.set_run_stat("currency", amount)
    
    def add_currency(self, amount):
        """
        Add currency
        
        Args:
            amount (int): Amount to add (negative to subtract)
            
        Returns:
            int: New currency amount
        """
        current = self.get_currency()
        self.set_currency(current + amount)
        return self.get_currency()
    
    def get_lives(self):
        """Get the current lives"""
        return self.get_run_stat("lives", 3)
    
    def set_lives(self, lives):
        """Set the current lives"""
        return self.set_run_stat("lives", lives)
    
    def add_lives(self, amount=1):
        """
        Add lives
        
        Args:
            amount (int): Amount to add (negative to subtract)
            
        Returns:
            int: New lives count
        """
        current = self.get_lives()
        self.set_lives(current + amount)
        return self.get_lives()
    
    def get_charging_station_charge(self):
        """Get the charging station charge"""
        return self.get_run_stat("chargingStationCharge", 0)
    
    def set_charging_station_charge(self, charge):
        """Set the charging station charge"""
        return self.set_run_stat("chargingStationCharge", charge)
    
    def get_total_haul(self):
        """Get the total haul"""
        return self.get_run_stat("totalHaul", 0)
    
    def set_total_haul(self, total):
        """Set the total haul"""
        return self.set_run_stat("totalHaul", total)
    
    def add_to_haul(self, amount):
        """
        Add to the total haul
        
        Args:
            amount (int): Amount to add
            
        Returns:
            int: New total haul
        """
        current = self.get_total_haul()
        self.set_total_haul(current + amount)
        return self.get_total_haul()
    
    def get_save_level(self):
        """Get the save level checkpoint"""
        return self.get_run_stat("save level", 0)
    
    def set_save_level(self, level):
        """Set the save level checkpoint"""
        return self.set_run_stat("save level", level)
    
    def update_item_purchased(self, item_name, quantity):
        """
        Update an item's purchased quantity and total
        
        Args:
            item_name (str): Name of the item
            quantity (int): New quantity value
        """
        if item_name in self.items["purchased"]:
            # Calculate delta for total
            old_quantity = self.items["purchased"][item_name]
            delta = quantity - old_quantity
            
            # Update purchased
            self.items["purchased"][item_name] = quantity
            
            # Update total by adding delta
            if item_name in self.items["purchasedTotal"]:
                self.items["purchasedTotal"][item_name] += delta
            else:
                self.items["purchasedTotal"][item_name] = quantity
    
    def update_upgrade_purchased(self, upgrade_name, quantity):
        """
        Update an upgrade item's purchased quantity
        
        Args:
            upgrade_name (str): Name of the upgrade
            quantity (int): New quantity value
        """
        if upgrade_name in self.items["upgradesPurchased"]:
            self.items["upgradesPurchased"][upgrade_name] = quantity