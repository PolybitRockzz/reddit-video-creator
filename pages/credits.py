import sys
import msvcrt
from utils import *

def show_credits_page():
    """Display the Credits page with main page style layout"""
    clear_screen()
    hide_cursor()
    
    width, height = get_terminal_size()
    
    # Draw top border
    left_border, right_border = draw_border(width, height)
    
    # Credits content
    credits_lines = [
        "CREDITS",
        "",
        "",
        "GitHub Repository:",
        "https://github.com/PolybitRockzz/reddit-video-creator",
        "",
        "",
        "Founder:",
        "@PolybitRockzz",
        "",
        "",
        "Project:",
        "Reddit Video Creator v0.1 BETA",
        "",
        "",
        "Press any key to return to main menu..."
    ]
    
    # Calculate total content height
    content_height = len(credits_lines)
    
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
    
    # Display credits content
    for line in credits_lines:
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
    
    # Wait for user input
    msvcrt.getch()
