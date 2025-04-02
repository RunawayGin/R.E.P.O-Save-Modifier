import os

def create_svg_icon(name, icon_content, output_dir=None):
    """
    Create an SVG icon file with the given name and content
    
    Args:
        name (str): Icon name (without extension)
        icon_content (str): SVG content
        output_dir (str, optional): Directory to save the icon. 
            Defaults to resources/icons in app directory
    
    Returns:
        str: Path to the created icon
    """
    # Determine output directory
    if output_dir is None:
        # Get the application's root directory
        app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        output_dir = os.path.join(app_dir, 'resources', 'icons')
    
    # Make sure the directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Create full path
    icon_path = os.path.join(output_dir, f"{name}.svg")
    
    # Create the SVG file
    with open(icon_path, "w", encoding='utf-8') as f:
        f.write(icon_content)
    
    return icon_path

def generate_all_icons(output_dir=None):
    """
    Generate all SVG icons needed by the application
    
    Args:
        output_dir (str, optional): Directory to save icons. If None, uses resources/icons
        
    Returns:
        list: Paths to all created icons
    """
    # Determine output directory
    if output_dir is None:
        # Get the application's root directory
        app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        output_dir = os.path.join(app_dir, 'resources', 'icons')
    
    # Make sure the directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Icons dictionary
    icons = {
        "menu": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#c3ccdf" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="3" y1="12" x2="21" y2="12"></line>
                    <line x1="3" y1="6" x2="21" y2="6"></line>
                    <line x1="3" y1="18" x2="21" y2="18"></line>
                   </svg>""",
                   
        "stats": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#c3ccdf" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M18 20V10"></path>
                    <path d="M12 20V4"></path>
                    <path d="M6 20v-6"></path>
                   </svg>""",
        
        "minimize": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#c3ccdf" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                         <line x1="5" y1="12" x2="19" y2="12"></line>
                       </svg>""",
        
        "maximize": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#c3ccdf" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                         <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                       </svg>""",
        
        "restore": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#c3ccdf" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                      </svg>""",
        
        "close": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#c3ccdf" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                     <line x1="18" y1="6" x2="6" y2="18"></line>
                     <line x1="6" y1="6" x2="18" y2="18"></line>
                   </svg>""",
        
        "home": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#c3ccdf" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                    <polyline points="9 22 9 12 15 12 15 22"></polyline>
                  </svg>""",
        
        "player": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#c3ccdf" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                      <circle cx="12" cy="7" r="4"></circle>
                    </svg>""",
        
        "upgrades": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#c3ccdf" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
                        <polyline points="17 6 23 6 23 12"></polyline>
                      </svg>""",
        
        "items": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#c3ccdf" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                     <rect x="3" y="3" width="7" height="7"></rect>
                     <rect x="14" y="3" width="7" height="7"></rect>
                     <rect x="14" y="14" width="7" height="7"></rect>
                     <rect x="3" y="14" width="7" height="7"></rect>
                   </svg>""",
        
        "open_file": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#c3ccdf" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                         <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
                       </svg>""",
        
        "save_file": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#c3ccdf" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                         <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path>
                         <polyline points="17 21 17 13 7 13 7 21"></polyline>
                         <polyline points="7 3 7 8 15 8"></polyline>
                       </svg>""",
        
        "settings": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#c3ccdf" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="3"></circle>
                        <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
                      </svg>""",
        
        "health": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#c3ccdf" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
                    </svg>""",

        "expand": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#c3ccdf" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                     <polyline points="6 9 12 15 18 9"></polyline>
                   </svg>""",
        
        "collapse": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#c3ccdf" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                       <polyline points="18 15 12 9 6 15"></polyline>
                     </svg>"""
    }
    
    # Create all icons
    paths = []
    for name, content in icons.items():
        path = create_svg_icon(name, content, output_dir)
        paths.append(path)
    
    return paths

if __name__ == "__main__":
    # Generate icons if run directly
    generated = generate_all_icons()
    for path in generated:
        print(f"Generated: {path}")