import os

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_terminal_size():
    """Get terminal dimensions"""
    try:
        columns, lines = os.get_terminal_size()
        return columns, lines
    except:
        return 80, 24  # Default fallback

def draw_border(width, height):
    """Draw border around the terminal"""
    # Top border
    print("┌" + "─" * (width - 2) + "┐")
    
    # Side borders (will be filled with content)
    return "│", "│"

def draw_bottom_border(width):
    """Draw bottom border"""
    print("└" + "─" * (width - 2) + "┘", end="", flush=True)

def center_text(text, width):
    """Center text within given width"""
    text_len = len(text)
    if text_len >= width - 2:
        return text[:width-2]
    
    padding = (width - 2 - text_len) // 2
    return " " * padding + text + " " * (width - 2 - text_len - padding)

def draw_menu_options(selected_option, options):
    """Draw menu options with selection highlight"""
    menu_lines = []
    menu_lines.append("Please select an option:")
    menu_lines.append("")
    
    for i, option in enumerate(options):
        if i == selected_option:
            menu_lines.append(f"► {option} ◄")
        else:
            menu_lines.append(f"{option}")
    
    menu_lines.append("")
    menu_lines.append("Use ↑/↓ arrow keys to navigate, Enter to select, ESC to exit")
    
    return menu_lines