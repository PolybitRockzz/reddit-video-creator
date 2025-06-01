import sys
import msvcrt

from utils import *
from pages.create_video import show_create_video_page
from pages.settings import show_settings_page
from pages.credits import show_credits_page

# Functions moved to utils.py for better organization

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
    show_cursor()  # Restore cursor before exiting
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
    
    # Display interface for the first time
    width, height = get_terminal_size()
    menu_start_row = display_interface_initial(selected_option, options)
    
    while True:
        # Get keyboard input
        key = msvcrt.getch()
        
        if key == b'\xe0':  # Special key prefix for arrow keys
            key = msvcrt.getch()
            if key == b'H':  # Up arrow
                selected_option = (selected_option - 1) % max_options
                # Update only the menu portion
                update_menu_selection(selected_option, options, menu_start_row, width)
            elif key == b'P':  # Down arrow
                selected_option = (selected_option + 1) % max_options
                # Update only the menu portion
                update_menu_selection(selected_option, options, menu_start_row, width)
        elif key == b'\r':  # Enter key
            if selected_option == 0:
                handle_option_1()
                # Redraw interface when returning from a page
                menu_start_row = display_interface_initial(selected_option, options)
            elif selected_option == 1:
                handle_option_2()
                # Redraw interface when returning from a page
                menu_start_row = display_interface_initial(selected_option, options)
            elif selected_option == 2:
                handle_option_3()
                # Redraw interface when returning from a page
                menu_start_row = display_interface_initial(selected_option, options)
            elif selected_option == 3:
                handle_option_4()
        elif key == b'\x1b':  # ESC key
            handle_option_4()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        show_cursor()  # Restore cursor before exiting
        clear_screen()
        print("\nProgram interrupted by user.")
        sys.exit(0)
    except Exception as e:
        show_cursor()  # Restore cursor before exiting
        clear_screen()
        print(f"An error occurred: {e}")
        input("Press Enter to exit...")
        sys.exit(1)
