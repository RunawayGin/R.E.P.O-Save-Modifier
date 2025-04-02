import os
import requests
import xml.etree.ElementTree as ET
import urllib3
import time
from PySide6.QtCore import QObject, Signal, QThread

# Disable insecure request warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class SteamAPI(QObject):
    """
    Handles Steam profile integration, including fetching avatars and caching them locally
    """
    
    # Signal emitted when avatar is fetched
    avatar_fetched = Signal(str, str)  # player_id, image_path
    
    def __init__(self, cache_dir=None):
        """
        Initialize the Steam API
        
        Args:
            cache_dir (str, optional): Directory to cache avatars. 
                If None, defaults to resources/cache
        """
        super().__init__()
        
        # Set up cache directory
        if cache_dir is None:
            # Get the application's root directory
            app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            cache_dir = os.path.join(app_dir, 'resources', 'cache')
        
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        
        # Store active threads
        self.threads = []
    
    def get_cached_avatar_path(self, player_id):
        """
        Get the path to a cached avatar if it exists
        
        Args:
            player_id (str): Steam player ID
            
        Returns:
            str: Path to the cached avatar or None if not cached
        """
        # Check for existing cached files with this player_id prefix
        for ext in ['.jpg', '.png', '.jpeg']:
            cache_file = os.path.join(self.cache_dir, f"{player_id}{ext}")
            if os.path.exists(cache_file):
                return cache_file
        
        return None
    
    def fetch_avatar(self, player_id, force_refresh=False):
        """
        Fetch the Steam profile avatar for a given player_id
        
        Args:
            player_id (str): Steam player ID
            force_refresh (bool, optional): Force refreshing even if cached. Defaults to False.
            
        Returns:
            str: Path to the cached avatar or None if fetching failed
        """
        # Check cache first unless force_refresh is True
        if not force_refresh:
            cached_path = self.get_cached_avatar_path(player_id)
            if cached_path:
                return cached_path
        
        # Fetch the avatar
        try:
            xml_url = f"https://steamcommunity.com/profiles/{player_id}/?xml=1"
            
            # Fetch the XML data with SSL verification disabled for speed
            response = requests.get(xml_url, verify=False)
            if response.status_code != 200:
                print(f"Error: Unable to fetch profile XML data for {player_id}.")
                return None
    
            root = ET.fromstring(response.content)
            avatar_element = root.find('avatarFull')
            
            if avatar_element is None or not avatar_element.text:
                print(f"Error: Profile photo not found for {player_id}.")
                return None
    
            avatar_url = avatar_element.text
    
            # Determine file extension (default to .png if not found)
            file_extension = os.path.splitext(avatar_url)[1] or ".png"
            cache_file = os.path.join(self.cache_dir, f"{player_id}{file_extension}")
            
            # Download the image with SSL verification disabled
            image_response = requests.get(avatar_url, verify=False)
            if image_response.status_code != 200:
                print(f"Error: Unable to download profile photo for {player_id}.")
                return None
    
            with open(cache_file, 'wb') as f:
                f.write(image_response.content)
            
            return cache_file
            
        except Exception as e:
            print(f"Error fetching avatar for {player_id}: {str(e)}")
            return None
    
    def fetch_avatar_async(self, player_id):
        """
        Fetch a Steam avatar asynchronously
        
        Args:
            player_id (str): Steam ID
        """
        print(f"SteamAPI: Starting async fetch for {player_id}")
        
        # Check if we already have too many threads running
        active_threads = [t for t in self.threads if t.isRunning()]
        if len(active_threads) > 5:  # Limit concurrent threads
            print(f"Warning: Too many avatar fetch threads running ({len(active_threads)}). Cleaning up old threads.")
            for thread in active_threads:
                if thread.isRunning() and thread.player_id != player_id:
                    print(f"Stopping thread for {thread.player_id}")
                    thread.quit()
                    thread.wait(100)  # Brief wait
        
        # Create a worker thread to fetch the avatar
        thread = AvatarFetchThread(self, player_id)
        thread.avatar_fetched.connect(self._on_avatar_fetched)
        thread.finished.connect(lambda: self._on_thread_finished(thread))
        self.threads.append(thread)
        
        # Set thread priority to high to ensure it completes
        thread.setPriority(QThread.HighPriority)
        
        print(f"SteamAPI: Starting fetch thread for {player_id}")
        thread.start()
    
    def _on_avatar_fetched(self, player_id, image_path):
        """
        Handle when an avatar is fetched asynchronously
        
        Args:
            player_id (str): Steam ID
            image_path (str): Path to the fetched image
        """
        print(f"SteamAPI: Avatar fetched for {player_id}: {image_path}")
        # Re-emit the signal
        self.avatar_fetched.emit(player_id, image_path)
    
    def fetch_profile_info(self, player_id):
        """
        Fetch basic profile information for a Steam player
        
        Args:
            player_id (str): Steam player ID
            
        Returns:
            dict: Player information or None if fetching failed
        """
        try:
            xml_url = f"https://steamcommunity.com/profiles/{player_id}/?xml=1"
            
            # Fetch the XML data with a timeout to prevent hanging
            response = requests.get(xml_url, verify=False, timeout=5)
            if response.status_code != 200:
                print(f"Error: Unable to fetch profile data for {player_id}. Status code: {response.status_code}")
                return None

            root = ET.fromstring(response.content)
            
            # Extract basic information
            info = {}
            
            # Check if the profile exists
            error = root.find('error')
            if error is not None:
                print(f"Error: {error.text}")
                return None
                
            # Extract steamID (display name)
            steam_id = root.find('steamID')
            if steam_id is not None and steam_id.text:
                info['steamID'] = steam_id.text
            else:
                # If we can't get the name, use a default with the ID
                info['steamID'] = f"Player_{player_id[-4:]}"  # Use last 4 digits of Steam ID
            
            # Extract other optional information
            for key in ['realname', 'location', 'memberSince']:
                element = root.find(key)
                if element is not None and element.text:
                    info[key] = element.text
            
            return info
            
        except requests.exceptions.Timeout:
            print(f"Timeout error fetching profile info for {player_id}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Request error fetching profile info for {player_id}: {str(e)}")
            return None
        except Exception as e:
            print(f"Error fetching profile info for {player_id}: {str(e)}")
            return None
    
    def _on_thread_finished(self, thread):
        """
        Handle when a thread finishes
        
        Args:
            thread: The finished thread
        """
        # Remove thread from list
        if thread in self.threads:
            self.threads.remove(thread)
    
    def cleanup(self):
        """Clean up all running threads"""
        # Wait for all threads to finish
        for thread in self.threads:
            if thread.isRunning():
                thread.quit()
                thread.wait(1000)  # Wait up to 1 second

class AvatarFetchThread(QThread):
    """
    Thread for fetching avatars asynchronously
    """
    
    # Signal emitted when avatar is fetched
    avatar_fetched = Signal(str, str)  # player_id, image_path
    
    def __init__(self, steam_api, player_id):
        """
        Initialize the avatar fetch thread
        
        Args:
            steam_api (SteamAPI): SteamAPI instance
            player_id (str): Steam player ID
        """
        super().__init__()
        self.steam_api = steam_api
        self.player_id = player_id
        print(f"AvatarFetchThread: Initialized for {player_id}")
    
    def run(self):
        """Run the thread"""
        # Check cache first
        cached_path = self.steam_api.get_cached_avatar_path(self.player_id)
        if cached_path:
            print(f"AvatarFetchThread: Using cached avatar for {self.player_id}")
            self.avatar_fetched.emit(self.player_id, cached_path)
            return
        
        # Fetch the avatar
        try:
            print(f"AvatarFetchThread: Fetching avatar for {self.player_id}")
            image_path = self.steam_api.fetch_avatar(self.player_id)
            
            if image_path:
                print(f"AvatarFetchThread: Successfully fetched avatar for {self.player_id}")
                self.avatar_fetched.emit(self.player_id, image_path)
            else:
                print(f"AvatarFetchThread: Failed to fetch avatar for {self.player_id}")
        except Exception as e:
            print(f"AvatarFetchThread: Error fetching avatar for {self.player_id}: {str(e)}")