import sys
import time
import msvcrt
import os
import subprocess
import pkg_resources
import urllib.request
import urllib.error
import toml
from pathlib import Path
from utils import *

def draw_loading_bar(progress, max_length=50):
    """Draw a loading bar with the given progress (0-100)"""
    filled_length = int(max_length * progress / 100)
    bar = "█" * filled_length + "░" * (max_length - filled_length)
    percentage = f"{progress:3.0f}%"
    return f"[{bar}] {percentage}"

def display_boot_interface_initial():
    """Display the boot interface for the first time"""
    clear_screen()
    hide_cursor()
    
    width, height = get_terminal_size()
    
    # Draw top border
    left_border, right_border = draw_border(width, height)

    orange = "\033[38;5;208m"  # Orange color for "REDDIT VIDEO CREATOR"
    reset = "\033[0m"          # Reset color

    
    # Boot content (static parts)
    boot_lines = [
        "",
        f"{orange}REDDIT VIDEO CREATOR{reset}",
        "",
        "Booting up the script...",
        "",
        "",  # Placeholder for progress bar
        "",
        "",
        "",  # Placeholder for status text
        ""
    ]
    
    # Calculate total content height
    content_height = len(boot_lines)
    
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
    
    # Display boot content
    progress_bar_row = None
    status_text_row = None
    
    for i, line in enumerate(boot_lines):
        if lines_printed < height - 1:
            centered_line = center_text(line, width)
            print(left_border + centered_line + right_border)
            
            # Remember the row positions for dynamic updates
            if i == 5:  # Progress bar position
                progress_bar_row = lines_printed + 1  # +1 for 1-indexed cursor positioning
            elif i == 8:  # Status text position
                status_text_row = lines_printed + 1
                
            lines_printed += 1
    
    # Fill remaining lines up to the bottom border
    while lines_printed < height - 1:
        print(left_border + " " * (width - 2) + right_border)
        lines_printed += 1
    
    # Draw bottom border without newline to prevent scrolling
    draw_bottom_border(width)
    
    return progress_bar_row, status_text_row, width

def update_boot_progress(progress, status_text, progress_bar_row, status_text_row, width):
    """Update only the progress bar and status text without redrawing everything"""
    hide_cursor()
    
    # Update progress bar
    move_cursor(progress_bar_row, 1)
    clear_line()
    progress_line = draw_loading_bar(progress)
    centered_line = center_text(progress_line, width)
    print("│" + centered_line + "│", end="", flush=True)
    
    # Update status text
    move_cursor(status_text_row, 1)
    clear_line()
    centered_status = center_text(status_text, width)
    print("│" + centered_status + "│", end="", flush=True)
    
    show_cursor()

def validate_dependencies():
    """Check if all required dependencies are installed with correct versions"""
    try:
        requirements_path = Path("requirements.txt")
        if not requirements_path.exists():
            return False, "requirements.txt not found"
        
        with open(requirements_path, 'r') as f:
            requirements = f.read().strip().split('\n')
        
        for requirement in requirements:
            if not requirement.strip():
                continue
            
            try:
                pkg_resources.require(requirement)
            except (pkg_resources.DistributionNotFound, pkg_resources.VersionConflict) as e:
                return False, f"Dependency issue: {str(e)}"
        
        return True, "All dependencies validated"
    except Exception as e:
        return False, f"Error checking dependencies: {str(e)}"

def validate_config_file():
    """Create or validate the config.toml file"""
    try:
        config_path = Path("config.toml")
        
        # If config doesn't exist, create it with default values
        if not config_path.exists():
            default_config = {
                "reddit": {
                    "client_id": "your_reddit_client_id",
                    "client_secret": "your_reddit_client_secret",
                    "username": "your_reddit_username",
                    "password": "your_reddit_password",
                    "user_agent": "RedditVideoCreator:v1.0 (by /u/your_username)"
                },
                "video": {
                    "output_directory": "output/",
                    "resolution": "1080p",
                    "fps": 30,
                    "duration_limit": 300,
                    "background_music": True,
                    "voice_synthesis": "gtts"
                },
                "text_to_speech": {
                    "voice": "en",
                    "speed": 1.0,
                    "volume": 0.8
                },
                "processing": {
                    "max_concurrent_downloads": 3,
                    "temp_directory": "temp/",
                    "cleanup_after_processing": True
                },
                "ui": {
                    "theme": "dark",
                    "show_progress": True,
                    "auto_save_settings": True
                }
            }
            
            with open(config_path, 'w') as f:
                toml.dump(default_config, f)
            
            return True, "Created default config.toml file"
        
        # Validate existing config file
        with open(config_path, 'r') as f:
            config = toml.load(f)
        
        # Check required sections
        required_sections = ["reddit", "video", "text_to_speech", "processing", "ui"]
        for section in required_sections:
            if section not in config:
                return False, f"Missing section '{section}' in config.toml"
        
        return True, "Configuration file validated"
    except Exception as e:
        return False, f"Error with config file: {str(e)}"

def check_ffmpeg_installation():
    """Check if FFmpeg is installed and accessible"""
    try:
        # Try to run ffmpeg -version
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=10)
        
        if result.returncode == 0:
            return True, "FFmpeg found and working"
        else:
            return False, "FFmpeg command failed"
    except subprocess.TimeoutExpired:
        return False, "FFmpeg command timed out"
    except FileNotFoundError:
        return False, "FFmpeg not found in PATH"
    except Exception as e:
        return False, f"Error checking FFmpeg: {str(e)}"

def check_internet_connectivity():
    """Check if internet connection is available"""
    try:
        # Try to connect to a reliable host
        urllib.request.urlopen('https://www.google.com', timeout=5)
        return True, "Internet connection verified"
    except urllib.error.URLError:
        return False, "No internet connection"
    except Exception as e:
        return False, f"Error checking connectivity: {str(e)}"

def create_required_directories():
    """Create required directories if they don't exist"""
    try:
        directories = ["output", "temp"]
        
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
        
        return True, "Required directories created"
    except Exception as e:
        return False, f"Error creating directories: {str(e)}"

def simulate_boot_process():
    """Simulate the boot process with actual system validation"""
    
    # Define validation stages
    validation_stages = [
        (5, "Initializing system...", None),
        (15, "Creating required directories...", create_required_directories),
        (25, "Validating configuration file...", validate_config_file),
        (40, "Checking dependencies...", validate_dependencies),
        (55, "Checking FFmpeg installation...", check_ffmpeg_installation),
        (70, "Testing internet connectivity...", check_internet_connectivity),
        (85, "Loading user interface...", None),
        (95, "Finalizing startup...", None),
        (100, "Boot complete! Starting application...", None)
    ]
    
    # Display the initial interface once
    progress_bar_row, status_text_row, width = display_boot_interface_initial()
    
    # Track validation results
    validation_errors = []
    
    for progress, status, validation_func in validation_stages:
        # Update progress and status
        update_boot_progress(progress, status, progress_bar_row, status_text_row, width)
        
        # Run validation if function is provided
        if validation_func:
            time.sleep(0.3)  # Brief pause for visual effect
            success, message = validation_func()
            
            if success:
                # Show success message briefly
                success_status = f"✓ {message}"
                update_boot_progress(progress, success_status, progress_bar_row, status_text_row, width)
                time.sleep(0.5)
            else:
                # Show error message
                error_status = f"✗ {message}"
                update_boot_progress(progress, error_status, progress_bar_row, status_text_row, width)
                validation_errors.append(f"{status}: {message}")
                time.sleep(1.0)  # Longer pause for errors
        else:
            time.sleep(0.5)  # Normal loading time for non-validation stages
        
        # Check if user wants to skip (optional)
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key == b' ':  # Space to skip
                break
    
    # Handle validation errors
    if validation_errors:
        error_summary = f"Found {len(validation_errors)} issue(s). Press any key to continue anyway..."
        update_boot_progress(100, error_summary, progress_bar_row, status_text_row, width)
        msvcrt.getch()
        
        # Show detailed error information
        show_validation_errors(validation_errors)
    else:
        # All validations passed
        update_boot_progress(100, "All systems ready! Press any key to continue...", progress_bar_row, status_text_row, width)
        msvcrt.getch()

def show_validation_errors(errors):
    """Display detailed validation errors to the user"""
    clear_screen()
    hide_cursor()
    
    width, height = get_terminal_size()
    
    # Draw top border
    left_border, right_border = draw_border(width, height)
    
    red = "\033[91m"
    yellow = "\033[93m"
    reset = "\033[0m"
    
    error_lines = [
        "",
        f"{red}VALIDATION WARNINGS{reset}",
        "",
        f"{yellow}The following issues were detected during startup:{reset}",
        ""
    ]
    
    # Add each error
    for i, error in enumerate(errors, 1):
        error_lines.append(f"{i}. {error}")
    
    error_lines.extend([
        "",
        f"{yellow}Note: The application may still work with limited functionality.{reset}",
        "You can fix these issues later in the Settings menu.",
        "",
        "Press any key to continue..."
    ])
    
    # Calculate positioning
    content_height = len(error_lines)
    available_lines = height - 2
    start_line = max(0, (available_lines - content_height) // 2)
    
    lines_printed = 1  # Top border already printed
    
    # Fill empty lines before content
    for i in range(start_line):
        if lines_printed < height - 1:
            print(left_border + " " * (width - 2) + right_border)
            lines_printed += 1
    
    # Display error content
    for line in error_lines:
        if lines_printed < height - 1:
            centered_line = center_text(line, width)
            print(left_border + centered_line + right_border)
            lines_printed += 1
    
    # Fill remaining lines
    while lines_printed < height - 1:
        print(left_border + " " * (width - 2) + right_border)
        lines_printed += 1
    
    # Draw bottom border
    draw_bottom_border(width)
    
    show_cursor()
    msvcrt.getch()

def show_boot_screen():
    """Main function to show the boot screen"""
    simulate_boot_process()

if __name__ == "__main__":
    try:
        show_boot_screen()
    except KeyboardInterrupt:
        show_cursor()
        clear_screen()
        print("\nBoot process interrupted by user.")
        sys.exit(0)
    except Exception as e:
        show_cursor()
        clear_screen()
        print(f"An error occurred during boot: {e}")
        input("Press Enter to exit...")
        sys.exit(1)
