import sys
import msvcrt

from utils import *
from pages.create_video import show_create_video_page
from pages.settings import show_settings_page
from pages.credits import show_credits_page

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

def display_interface(selected_option, options):
    """Display the complete interface"""
    clear_screen()
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

def handle_option_1():
    """Handle option 1 - Create Video"""
    show_create_video_page()

def handle_option_2():
    """Handle option 2 - Settings"""
    show_settings_page()

def handle_option_3():
    """Handle option 3 - Credits"""
    show_credits_page()

def handle_option_4():
    """Handle option 4 - Exit"""
    clear_screen()
    print("╔══════════════════════════════════════╗")
    print("║            GOODBYE!                  ║")
    print("╚══════════════════════════════════════╝")
    print("\nThank you for using Reddit Video Creator!")
    print("Exiting...")
    sys.exit(0)

def main():
    """Main program loop"""
    selected_option = 0
    options = [
        "Create Video",
        "Settings",
        "Credits"
    ]
    max_options = len(options)
    
    while True:
        display_interface(selected_option, options)
        
        # Get keyboard input
        key = msvcrt.getch()
        
        if key == b'\xe0':  # Special key prefix for arrow keys
            key = msvcrt.getch()
            if key == b'H':  # Up arrow
                selected_option = (selected_option - 1) % max_options
            elif key == b'P':  # Down arrow
                selected_option = (selected_option + 1) % max_options
        elif key == b'\r':  # Enter key
            if selected_option == 0:
                handle_option_1()
            elif selected_option == 1:
                handle_option_2()
            elif selected_option == 2:
                handle_option_3()
            elif selected_option == 3:
                handle_option_4()
        elif key == b'\x1b':  # ESC key
            handle_option_4()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        clear_screen()
        print("\nProgram interrupted by user.")
        sys.exit(0)
    except Exception as e:
        clear_screen()
        print(f"An error occurred: {e}")
        input("Press Enter to exit...")
        sys.exit(1)
