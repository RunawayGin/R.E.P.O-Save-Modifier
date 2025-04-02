# Add this to a new file: app/core/user_cache.py

import os
import json
import time
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional

@dataclass
class CachedUser:
    """Represents a cached user for quick re-adding to saves"""
    steam_id: str
    username: str
    avatar_path: Optional[str] = None
    last_used: float = 0  # Unix timestamp
    
    def to_dict(self):
        """Convert to dictionary for serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary"""
        return cls(**data)

class UserCache:
    """Manages caching of users for quick re-adding"""
    
    def __init__(self, cache_dir=None):
        """
        Initialize the user cache
        
        Args:
            cache_dir (str, optional): Directory to store the cache file. 
                Defaults to app/resources/cache.
        """
        # Set cache directory
        if cache_dir is None:
            # Get the application's root directory
            app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            cache_dir = os.path.join(app_dir, 'resources', 'cache')
        
        # Ensure cache directory exists
        os.makedirs(cache_dir, exist_ok=True)
        
        self.cache_dir = cache_dir
        self.cache_file = os.path.join(cache_dir, 'user_cache.json')
        self.users: Dict[str, CachedUser] = {}
        
        # Load cache if exists
        self.load_cache()
    
    def load_cache(self):
        """Load the cache from file"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self.users = {
                            steam_id: CachedUser.from_dict(user_data)
                            for steam_id, user_data in data.items()
                        }
                    else:
                        print("Invalid cache format, starting with empty cache")
                        self.users = {}
            except Exception as e:
                print(f"Error loading user cache: {str(e)}")
                self.users = {}
        else:
            self.users = {}
    
    def save_cache(self):
        """Save the cache to file"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(
                    {sid: user.to_dict() for sid, user in self.users.items()},
                    f,
                    indent=2
                )
            return True
        except Exception as e:
            print(f"Error saving user cache: {str(e)}")
            return False
    
    def add_user(self, steam_id, username, avatar_path=None):
        """
        Add a user to the cache
        
        Args:
            steam_id (str): Steam ID
            username (str): Username
            avatar_path (str, optional): Path to avatar image. Defaults to None.
            
        Returns:
            bool: True if successful
        """
        # Update or create user
        current_time = time.time()
        
        # If exists, update last_used and other fields if needed
        if steam_id in self.users:
            self.users[steam_id].username = username
            self.users[steam_id].last_used = current_time
            if avatar_path:
                self.users[steam_id].avatar_path = avatar_path
        else:
            # Create new
            self.users[steam_id] = CachedUser(
                steam_id=steam_id,
                username=username,
                avatar_path=avatar_path,
                last_used=current_time
            )
        
        # Save to file
        return self.save_cache()
    
    def get_user(self, steam_id):
        """
        Get a user from the cache
        
        Args:
            steam_id (str): Steam ID
            
        Returns:
            CachedUser: User data or None if not found
        """
        return self.users.get(steam_id)
    
    def get_all_users(self, sort_by_recent=True):
        """
        Get all cached users
        
        Args:
            sort_by_recent (bool, optional): Sort by most recently used. Defaults to True.
            
        Returns:
            List[CachedUser]: List of users
        """
        users = list(self.users.values())
        
        if sort_by_recent:
            users.sort(key=lambda u: u.last_used, reverse=True)
            
        return users
    
    def remove_user(self, steam_id):
        """
        Remove a user from the cache
        
        Args:
            steam_id (str): Steam ID
            
        Returns:
            bool: True if successful
        """
        if steam_id in self.users:
            del self.users[steam_id]
            return self.save_cache()
        return False
    
    def update_last_used(self, steam_id):
        """
        Update the last used timestamp for a user
        
        Args:
            steam_id (str): Steam ID
            
        Returns:
            bool: True if successful
        """
        if steam_id in self.users:
            self.users[steam_id].last_used = time.time()
            return self.save_cache()
        return False
