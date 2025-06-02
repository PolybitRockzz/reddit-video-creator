import sys
import msvcrt
import toml
from pathlib import Path
from utils import *

def load_config():
    """Load the configuration from config.toml"""
    try:
        config_path = Path("config.toml")
        if config_path.exists():
            with open(config_path, 'r') as f:
                return toml.load(f)
        else:
            return {}
    except Exception as e:
        return {}

def save_config(config):
    """Save the configuration to config.toml"""
    try:
        config_path = Path("config.toml")
        with open(config_path, 'w') as f:
            toml.dump(config, f)
        return True
    except Exception as e:
        return False

def display_main_settings_interface(selected_option, sections):
    """Display the main settings interface"""
    clear_screen()
    hide_cursor()
    
    width, height = get_terminal_size()
    
    # Draw top border
    left_border, right_border = draw_border(width, height)

    # Title with colors
    orange = "\033[38;5;208m"
    blue = "\033[34m"
    green = "\033[32m"
    reset = "\033[0m"
    
    # Main content
    content_lines = [
        "",
        f"{orange}SETTINGS CONFIGURATION{reset}",
        "",
        "Select a configuration section to edit:",
        ""
    ]
    
    # Calculate positioning for content
    content_height = len(content_lines) + len(sections) + 5  # +5 for spacing and instructions
    available_lines = height - 2  # -2 for top and bottom borders
    start_line = max(0, (available_lines - content_height) // 2)
    
    lines_printed = 1  # Start at 1 because top border is already printed
    
    # Fill empty lines before content
    for i in range(start_line):
        if lines_printed < height - 1:
            print(left_border + " " * (width - 2) + right_border)
            lines_printed += 1
    
    # Display main content
    for line in content_lines:
        if lines_printed < height - 1:
            centered_line = center_text(line, width)
            print(left_border + centered_line + right_border)
            lines_printed += 1
    
    # Remember where menu starts
    menu_start_row = lines_printed + 1  # +1 for 1-indexed cursor positioning
    
    # Display menu options
    for i, section in enumerate(sections):
        if lines_printed < height - 1:
            if i == selected_option:
                # Highlighted option
                option_text = f"► {section.upper()}"
                cyan = "\033[96m"
                formatted_text = f"{cyan}{option_text}{reset}"
            else:
                # Normal option
                option_text = f"  {section.upper()}"
                formatted_text = option_text
            
            centered_option = center_text(formatted_text, width)
            print(left_border + centered_option + right_border)
            lines_printed += 1
    
    # Add spacing and instructions
    if lines_printed < height - 1:
        print(left_border + " " * (width - 2) + right_border)
        lines_printed += 1
    
    if lines_printed < height - 1:
        instructions = "Use ↑↓ to navigate, Enter to select, ESC to return to main menu"
        centered_instructions = center_text(instructions, width)
        print(left_border + centered_instructions + right_border)
        lines_printed += 1
    
    # Fill remaining lines up to the bottom border
    while lines_printed < height - 1:
        print(left_border + " " * (width - 2) + right_border)
        lines_printed += 1
    
    # Draw bottom border without newline to prevent scrolling
    draw_bottom_border(width)
    
    return menu_start_row

def display_section_settings_interface(section_name, selected_option, variables, values):
    """Display the section-specific settings interface"""
    clear_screen()
    hide_cursor()
    
    width, height = get_terminal_size()
    
    # Draw top border
    left_border, right_border = draw_border(width, height)

    # Title with colors
    orange = "\033[38;5;208m"
    blue = "\033[34m"
    green = "\033[32m"
    yellow = "\033[93m"
    reset = "\033[0m"
    
    # Main content
    content_lines = [
        "",
        f"{orange}{section_name.upper()} SETTINGS{reset}",
        "",
        "Select a setting to modify:",
        ""
    ]
    
    # Calculate positioning for content
    menu_items = variables + ["← Back to Main Settings"]
    content_height = len(content_lines) + len(menu_items) + 5  # +5 for spacing and instructions
    available_lines = height - 2  # -2 for top and bottom borders
    start_line = max(0, (available_lines - content_height) // 2)
    
    lines_printed = 1  # Start at 1 because top border is already printed
    
    # Fill empty lines before content
    for i in range(start_line):
        if lines_printed < height - 1:
            print(left_border + " " * (width - 2) + right_border)
            lines_printed += 1
    
    # Display main content
    for line in content_lines:
        if lines_printed < height - 1:
            centered_line = center_text(line, width)
            print(left_border + centered_line + right_border)
            lines_printed += 1
    
    # Remember where menu starts
    menu_start_row = lines_printed + 1  # +1 for 1-indexed cursor positioning
    
    # Display menu options for variables
    for i, variable in enumerate(variables):
        if lines_printed < height - 1:
            # Get current value for display
            current_value = values.get(variable, "Not set")
            if isinstance(current_value, str) and len(current_value) > 25:
                display_value = current_value[:22] + "..."
            else:
                display_value = str(current_value)
            
            if i == selected_option:
                # Highlighted option
                option_text = f"► {variable}: {display_value}"
                cyan = "\033[96m"
                formatted_text = f"{cyan}{option_text}{reset}"
            else:
                # Normal option
                option_text = f"  {variable}: {display_value}"
                formatted_text = option_text
            
            centered_option = center_text(formatted_text, width)
            print(left_border + centered_option + right_border)
            lines_printed += 1
    
    # Display back option
    if lines_printed < height - 1:
        back_index = len(variables)
        if back_index == selected_option:
            # Highlighted back option
            option_text = "► ← Back to Main Settings"
            cyan = "\033[96m"
            formatted_text = f"{cyan}{option_text}{reset}"
        else:
            # Normal back option
            option_text = "  ← Back to Main Settings"
            formatted_text = option_text
        
        centered_option = center_text(formatted_text, width)
        print(left_border + centered_option + right_border)
        lines_printed += 1
    
    # Add spacing and instructions
    if lines_printed < height - 1:
        print(left_border + " " * (width - 2) + right_border)
        lines_printed += 1
    
    if lines_printed < height - 1:
        instructions = "Use ↑↓ to navigate, Enter to select/edit, ESC to go back"
        centered_instructions = center_text(instructions, width)
        print(left_border + centered_instructions + right_border)
        lines_printed += 1
    
    # Fill remaining lines up to the bottom border
    while lines_printed < height - 1:
        print(left_border + " " * (width - 2) + right_border)
        lines_printed += 1
    
    # Draw bottom border without newline to prevent scrolling
    draw_bottom_border(width)
    
    return menu_start_row

def update_main_menu_selection(selected_option, sections, menu_start_row, width):
    """Update only the menu selection without redrawing everything"""
    hide_cursor()
    cyan = "\033[96m"
    reset = "\033[0m"
    
    for i, section in enumerate(sections):
        move_cursor(menu_start_row + i, 1)
        clear_line()
        
        if i == selected_option:
            # Highlighted option
            option_text = f"► {section.upper()}"
            formatted_text = f"{cyan}{option_text}{reset}"
        else:
            # Normal option
            option_text = f"  {section.upper()}"
            formatted_text = option_text
        
        centered_option = center_text(formatted_text, width)
        print("│" + centered_option + "│", end="", flush=True)
    
    show_cursor()

def update_section_menu_selection(selected_option, variables, values, menu_start_row, width):
    """Update only the section menu selection without redrawing everything"""
    hide_cursor()
    cyan = "\033[96m"
    reset = "\033[0m"
    
    # Update variable options
    for i, variable in enumerate(variables):
        move_cursor(menu_start_row + i, 1)
        clear_line()
        
        # Get current value for display
        current_value = values.get(variable, "Not set")
        if isinstance(current_value, str) and len(current_value) > 25:
            display_value = current_value[:22] + "..."
        else:
            display_value = str(current_value)
        
        if i == selected_option:
            # Highlighted option
            option_text = f"► {variable}: {display_value}"
            formatted_text = f"{cyan}{option_text}{reset}"
        else:
            # Normal option
            option_text = f"  {variable}: {display_value}"
            formatted_text = option_text
        
        centered_option = center_text(formatted_text, width)
        print("│" + centered_option + "│", end="", flush=True)
    
    # Update back option
    back_index = len(variables)
    move_cursor(menu_start_row + back_index, 1)
    clear_line()
    
    if back_index == selected_option:
        # Highlighted back option
        option_text = "► ← Back to Main Settings"
        formatted_text = f"{cyan}{option_text}{reset}"
    else:
        # Normal back option
        option_text = "  ← Back to Main Settings"
        formatted_text = option_text
    
    centered_option = center_text(formatted_text, width)
    print("│" + centered_option + "│", end="", flush=True)
    
    show_cursor()

def handle_text_input(prompt, current_value=""):
    """Handle text input with visual feedback"""
    width, height = get_terminal_size()
    
    # Calculate input area position
    input_row = height // 2 + 2
    max_input_width = width - 20  # Leave margins
    
    # Display prompt
    move_cursor(input_row - 1, 1)
    clear_line()
    prompt_line = center_text(prompt, width)
    print("│" + prompt_line + "│", end="", flush=True)
    
    # Display input field
    move_cursor(input_row, 1)
    clear_line()
    
    # Initialize input with current value
    user_input = current_value
    cursor_pos = len(user_input)
    
    while True:
        # Display current input
        display_text = user_input
        if len(display_text) > max_input_width:
            # Show end of text if too long
            display_text = "..." + display_text[-(max_input_width-3):]
        
        # Clear and redraw input line
        move_cursor(input_row, 1)
        clear_line()
        input_display = f"► {display_text}"
        if len(input_display) < max_input_width:
            input_display += "_"  # Show cursor
        centered_input = center_text(input_display, width)
        print("│" + centered_input + "│", end="", flush=True)
        
        # Get key input
        key = msvcrt.getch()
        
        if key == b'\r':  # Enter
            return user_input
        elif key == b'\x1b':  # ESC
            return None
        elif key == b'\x08':  # Backspace
            if user_input:
                user_input = user_input[:-1]
                cursor_pos = len(user_input)
        elif key == b'\xe0':  # Special keys (ignore arrow keys, etc.)
            msvcrt.getch()  # Consume the second byte
        else:
            # Regular character input
            try:
                char = key.decode('utf-8')
                if char.isprintable() and len(user_input) < 200:  # Reasonable limit
                    user_input += char
                    cursor_pos = len(user_input)
            except UnicodeDecodeError:
                pass  # Ignore invalid characters

def handle_choice_input(prompt, choices, current_value=""):
    """Handle choice selection with visual menu"""
    width, height = get_terminal_size()
    
    # Find current selection index
    selected_option = 0
    if current_value in choices:
        selected_option = choices.index(current_value)
    
    while True:
        # Calculate positioning
        content_height = len(choices) + 4  # +4 for prompt and spacing
        start_row = max(1, (height - content_height) // 2)
        
        # Display prompt
        move_cursor(start_row, 1)
        clear_line()
        prompt_line = center_text(prompt, width)
        print("│" + prompt_line + "│", end="", flush=True)
        
        # Display spacing
        move_cursor(start_row + 1, 1)
        clear_line()
        print("│" + " " * (width - 2) + "│", end="", flush=True)
        
        # Display choices
        for i, choice in enumerate(choices):
            move_cursor(start_row + 2 + i, 1)
            clear_line()
            
            if i == selected_option:
                cyan = "\033[96m"
                reset = "\033[0m"
                option_text = f"► {choice}"
                formatted_text = f"{cyan}{option_text}{reset}"
            else:
                option_text = f"  {choice}"
                formatted_text = option_text
            
            centered_option = center_text(formatted_text, width)
            print("│" + centered_option + "│", end="", flush=True)
        
        # Display instructions
        move_cursor(start_row + 2 + len(choices), 1)
        clear_line()
        print("│" + " " * (width - 2) + "│", end="", flush=True)
        
        move_cursor(start_row + 3 + len(choices), 1)
        clear_line()
        instructions = "Use ↑↓ to navigate, Enter to select, ESC to cancel"
        centered_instructions = center_text(instructions, width)
        print("│" + centered_instructions + "│", end="", flush=True)
        
        # Get keyboard input
        key = msvcrt.getch()
        
        if key == b'\xe0':  # Special key prefix
            key = msvcrt.getch()
            if key == b'H':  # Up arrow
                selected_option = (selected_option - 1) % len(choices)
            elif key == b'P':  # Down arrow
                selected_option = (selected_option + 1) % len(choices)
        elif key == b'\r':  # Enter
            return choices[selected_option]
        elif key == b'\x1b':  # ESC
            return None

def handle_float_input(prompt, current_value, min_val, max_val, increment):
    """Handle float input with increment/decrement controls"""
    width, height = get_terminal_size()
    
    # Parse current value
    try:
        current_float = float(current_value) if current_value else min_val
        # Ensure it's within bounds
        current_float = max(min_val, min(max_val, current_float))
    except (ValueError, TypeError):
        current_float = min_val
    
    while True:
        # Calculate positioning
        content_height = 8  # For display elements
        start_row = max(1, (height - content_height) // 2)
        
        # Display prompt
        move_cursor(start_row, 1)
        clear_line()
        prompt_line = center_text(prompt, width)
        print("│" + prompt_line + "│", end="", flush=True)
        
        # Display current value
        move_cursor(start_row + 2, 1)
        clear_line()
        value_text = f"Current Value: {current_float:.2f}"
        centered_value = center_text(value_text, width)
        print("│" + centered_value + "│", end="", flush=True)
        
        # Display range info
        move_cursor(start_row + 3, 1)
        clear_line()
        range_text = f"Range: {min_val} - {max_val} (increment: {increment})"
        centered_range = center_text(range_text, width)
        print("│" + centered_range + "│", end="", flush=True)
        
        # Display controls
        move_cursor(start_row + 5, 1)
        clear_line()
        controls = "Use ↑↓ to adjust value, Enter to confirm, ESC to cancel"
        centered_controls = center_text(controls, width)
        print("│" + centered_controls + "│", end="", flush=True)
        
        # Get keyboard input
        key = msvcrt.getch()
        
        if key == b'\xe0':  # Special key prefix
            key = msvcrt.getch()
            if key == b'H':  # Up arrow
                new_value = current_float + increment
                if new_value <= max_val:
                    current_float = round(new_value, 2)
            elif key == b'P':  # Down arrow
                new_value = current_float - increment
                if new_value >= min_val:
                    current_float = round(new_value, 2)
        elif key == b'\r':  # Enter
            return str(current_float)
        elif key == b'\x1b':  # ESC
            return None

def handle_variable_edit(section_name, variable_name, current_value):
    """Handle editing a specific variable based on section and variable type"""
    clear_screen()
    hide_cursor()
    
    width, height = get_terminal_size()
    
    # Draw interface frame
    left_border, right_border = draw_border(width, height)
    
    # Colors
    yellow = "\033[93m"
    cyan = "\033[96m"
    green = "\033[32m"
    reset = "\033[0m"
    
    # Display header
    header_lines = [
        "",
        f"{yellow}EDIT SETTING{reset}",
        "",
        f"Section: {cyan}{section_name}{reset}",
        f"Variable: {cyan}{variable_name}{reset}",
        ""
    ]
    
    lines_printed = 1  # Top border already printed
    
    # Display header
    for line in header_lines:
        if lines_printed < height - 1:
            centered_line = center_text(line, width)
            print(left_border + centered_line + right_border)
            lines_printed += 1
    
    # Fill remaining space for editing area
    while lines_printed < height - 1:
        print(left_border + " " * (width - 2) + right_border)
        lines_printed += 1
    
    # Draw bottom border
    draw_bottom_border(width)
    
    # Handle different variable types based on section and variable name
    new_value = None
    
    if section_name == "reddit":
        # All reddit variables are text
        new_value = handle_text_input(f"Enter new value for {variable_name}:", current_value)
    
    elif section_name == "video":
        if variable_name == "output_directory":
            new_value = handle_text_input("Enter output directory path:", current_value)
        elif variable_name == "resolution":
            choices = ["720p", "1080p"]
            new_value = handle_choice_input("Select resolution:", choices, current_value)
        elif variable_name == "fps":
            choices = ["15", "30", "60"]
            new_value = handle_choice_input("Select FPS:", choices, current_value)
        else:
            new_value = handle_text_input(f"Enter new value for {variable_name}:", current_value)
    
    elif section_name == "text_to_speech":
        if variable_name == "service":
            choices = ["gTTS", "pyttsx3"]
            new_value = handle_choice_input("Select TTS service:", choices, current_value)
        elif variable_name == "speed":
            new_value = handle_float_input("Adjust speed:", current_value, 0.1, 2.0, 0.1)
        elif variable_name == "volume":
            new_value = handle_float_input("Adjust volume:", current_value, 0.1, 1.0, 0.05)
        elif variable_name == "voice":
            # Show special notice for voice
            clear_screen()
            hide_cursor()
            
            # Redraw border
            left_border, right_border = draw_border(width, height)
            
            notice_lines = [
                "",
                f"{yellow}VOICE SETTING{reset}",
                "",
                f"{cyan}NOTICE: This project currently only supports English voices.{reset}",
                "",
                "Enter the voice name or identifier for your TTS service.",
                "For gTTS: Use language codes like 'en' (default)",
                "For pyttsx3: Use system voice names",
                ""
            ]
            
            lines_printed = 1
            for line in notice_lines:
                if lines_printed < height - 1:
                    centered_line = center_text(line, width)
                    print(left_border + centered_line + right_border)
                    lines_printed += 1
            
            # Fill remaining space
            while lines_printed < height - 1:
                print(left_border + " " * (width - 2) + right_border)
                lines_printed += 1
            
            draw_bottom_border(width)
            
            new_value = handle_text_input("Enter voice setting:", current_value)
        else:
            new_value = handle_text_input(f"Enter new value for {variable_name}:", current_value)
    
    else:
        # Default to text input for unknown sections
        new_value = handle_text_input(f"Enter new value for {variable_name}:", current_value)
    
    # Save the new value if provided
    if new_value is not None:
        config = load_config()
        
        # Ensure section exists
        if section_name not in config:
            config[section_name] = {}
        
        # Update the value
        config[section_name][variable_name] = new_value
        
        # Save configuration
        if save_config(config):
            # Show success message
            clear_screen()
            hide_cursor()
            
            left_border, right_border = draw_border(width, height)
            
            success_lines = [
                "",
                f"{green}SETTING SAVED{reset}",
                "",
                f"Variable: {cyan}{variable_name}{reset}",
                f"New Value: {cyan}{new_value}{reset}",
                "",
                "Press any key to continue..."
            ]
            
            content_height = len(success_lines)
            available_lines = height - 2
            start_line = max(0, (available_lines - content_height) // 2)
            
            lines_printed = 1
            
            # Fill empty lines before content
            for i in range(start_line):
                if lines_printed < height - 1:
                    print(left_border + " " * (width - 2) + right_border)
                    lines_printed += 1
            
            # Display success message
            for line in success_lines:
                if lines_printed < height - 1:
                    centered_line = center_text(line, width)
                    print(left_border + centered_line + right_border)
                    lines_printed += 1
            
            # Fill remaining lines
            while lines_printed < height - 1:
                print(left_border + " " * (width - 2) + right_border)
                lines_printed += 1
            
            draw_bottom_border(width)
            
            show_cursor()
            msvcrt.getch()
    
    show_cursor()

def show_settings_page():
    """Main settings page function"""
    config = load_config()
    
    # Define main sections from config
    main_sections = list(config.keys()) if config else ["reddit", "video", "text_to_speech"]
    
    selected_option = 0
    max_options = len(main_sections)
    
    # Display main settings interface
    width, height = get_terminal_size()
    menu_start_row = display_main_settings_interface(selected_option, main_sections)
    
    while True:
        # Get keyboard input
        key = msvcrt.getch()
        
        if key == b'\xe0':  # Special key prefix for arrow keys
            key = msvcrt.getch()
            if key == b'H':  # Up arrow
                selected_option = (selected_option - 1) % max_options
                update_main_menu_selection(selected_option, main_sections, menu_start_row, width)
            elif key == b'P':  # Down arrow
                selected_option = (selected_option + 1) % max_options
                update_main_menu_selection(selected_option, main_sections, menu_start_row, width)
        elif key == b'\r':  # Enter key
            # Enter selected section
            section_name = main_sections[selected_option]
            section_values = config.get(section_name, {})
            show_section_page(section_name, section_values, config)
            
            # Redraw main interface when returning from section
            menu_start_row = display_main_settings_interface(selected_option, main_sections)
        elif key == b'\x1b':  # ESC key
            return  # Return to main menu

def show_section_page(section_name, section_values, full_config):
    """Display and handle a specific section's settings"""
    variables = list(section_values.keys()) if section_values else []
    
    # Add default variables if section is empty
    if not variables:
        if section_name == "reddit":
            variables = ["client_id", "client_secret", "username", "password", "user_agent"]
        elif section_name == "video":
            variables = ["output_directory", "resolution", "fps"]
        elif section_name == "text_to_speech":
            variables = ["service", "voice", "speed", "volume"]
    
    selected_option = 0
    max_options = len(variables) + 1  # +1 for back option
    
    # Display section interface
    width, height = get_terminal_size()
    menu_start_row = display_section_settings_interface(section_name, selected_option, variables, section_values)
    
    while True:
        # Get keyboard input
        key = msvcrt.getch()
        
        if key == b'\xe0':  # Special key prefix for arrow keys
            key = msvcrt.getch()
            if key == b'H':  # Up arrow
                selected_option = (selected_option - 1) % max_options
                update_section_menu_selection(selected_option, variables, section_values, menu_start_row, width)
            elif key == b'P':  # Down arrow
                selected_option = (selected_option + 1) % max_options
                update_section_menu_selection(selected_option, variables, section_values, menu_start_row, width)
        elif key == b'\r':  # Enter key
            if selected_option == len(variables):  # Back option selected
                return  # Return to main settings
            else:
                # Edit selected variable
                variable_name = variables[selected_option]
                current_value = section_values.get(variable_name, "")
                handle_variable_edit(section_name, variable_name, current_value)
                
                # Redraw section interface when returning from edit
                menu_start_row = display_section_settings_interface(section_name, selected_option, variables, section_values)
        elif key == b'\x1b':  # ESC key
            return  # Return to main settings