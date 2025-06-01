import os
import sys

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def hide_cursor():
    """Hide the terminal cursor"""
    print("\033[?25l", end="", flush=True)

def show_cursor():
    """Show the terminal cursor"""
    print("\033[?25h", end="", flush=True)

def move_cursor(row, col):
    """Move cursor to specific position (1-indexed)"""
    print(f"\033[{row};{col}H", end="", flush=True)

def clear_line():
    """Clear the current line"""
    print("\033[2K", end="", flush=True)

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

def update_menu_selection(selected_option, options, menu_start_row, width):
    """Update only the menu selection without redrawing the entire screen"""
    hide_cursor()
    
    menu_lines = draw_menu_options(selected_option, options)
    
    # Update each menu line
    for i, line in enumerate(menu_lines):
        row = menu_start_row + i
        move_cursor(row, 1)  # Move to beginning of line
        clear_line()  # Clear the line
        
        # Redraw the line with borders
        centered_line = center_text(line, width)
        print("│" + centered_line + "│", end="", flush=True)
    
    show_cursor()

def display_interface_initial(selected_option, options):
    """Display the complete interface for the first time"""
    clear_screen()
    hide_cursor()
    
    width, height = get_terminal_size()
    
    # Draw top border
    left_border, right_border = draw_border(width, height)
    
    # Get content
    title_lines = draw_ascii_title()
    menu_lines = draw_menu_options(selected_option, options)
    
    # Calculate total content height
    content_height = len(title_lines) + len(menu_lines) + 4  # +4 for spacing
    
    # Calculate available space for content (excluding borders)
    available_lines = height - 2  # -2 for top and bottom borders
    
    # Calculate starting position to center vertically
    start_line = max(0, (available_lines - content_height) // 2)
    
    # Track how many lines we've printed
    lines_printed = 1  # Start at 1 because top border is already printed
    
    # Fill empty lines before content
    for i in range(start_line):
        if lines_printed < height - 1:  # Leave space for bottom border
            print(left_border + " " * (width - 2) + right_border)
            lines_printed += 1
    
    # Display title
    for line in title_lines:
        if lines_printed < height - 1:
            centered_line = center_text(line, width)
            print(left_border + centered_line + right_border)
            lines_printed += 1
    
    # Add spacing between title and menu
    for i in range(2):
        if lines_printed < height - 1:
            print(left_border + " " * (width - 2) + right_border)
            lines_printed += 1
    
    # Store the menu start position for later updates
    menu_start_row = lines_printed + 1  # +1 because we're 1-indexed for cursor positioning
    
    # Display menu
    for line in menu_lines:
        if lines_printed < height - 1:
            centered_line = center_text(line, width)
            print(left_border + centered_line + right_border)
            lines_printed += 1
    
    # Fill remaining lines up to the bottom border
    while lines_printed < height - 1:
        print(left_border + " " * (width - 2) + right_border)
        lines_printed += 1
    
    # Draw bottom border without newline to prevent scrolling
    draw_bottom_border(width)
    
    show_cursor()
    return menu_start_row

def draw_ascii_title():
    """Draw ASCII art title"""
    
    title_lines = [
        f"██████╗ ███████╗██████╗ ██████╗ ██╗████████╗",
        f"██╔══██╗██╔════╝██╔══██╗██╔══██╗██║╚══██╔══╝",
        f"██████╔╝█████╗  ██║  ██║██║  ██║██║   ██║   ",
        f"██╔══██╗██╔══╝  ██║  ██║██║  ██║██║   ██║   ",
        f"██║  ██║███████╗██████╔╝██████╔╝██║   ██║   ",
        f"╚═╝  ╚═╝╚══════╝╚═════╝ ╚═════╝ ╚═╝   ╚═╝   ",
        "",
        f"██╗   ██╗██╗██████╗ ███████╗ ██████╗ ",
        f"██║   ██║██║██╔══██╗██╔════╝██╔═══██╗",
        f"██║   ██║██║██║  ██║█████╗  ██║   ██║",
        f"╚██╗ ██╔╝██║██║  ██║██╔══╝  ██║   ██║",
        f" ╚████╔╝ ██║██████╔╝███████╗╚██████╔╝",
        f"  ╚═══╝  ╚═╝╚═════╝ ╚══════╝ ╚═════╝ ",
        "",
        "CREATOR v0.1 BETA"
    ]
    return title_lines