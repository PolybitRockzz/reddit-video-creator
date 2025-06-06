import sys
import msvcrt
import json
import hashlib
import praw
import toml
import random
from pathlib import Path
from utils import *
from tts import (
    create_audio_gtts, test_gtts_availability,
    create_audio_pyttsx3, test_pyttsx3_availability
)

def create_temp_directory():
    """Create temp directory if it doesn't exist"""
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    return temp_dir

def load_reddit_config():
    """Load Reddit API configuration from config.toml"""
    try:
        config_path = Path("config.toml")
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = toml.load(f)
                return config.get('reddit', {})
        return {}
    except Exception:
        return {}

def extract_post_info_from_url(url):
    """Extract post ID and subreddit from Reddit URL"""
    try:
        # Handle different Reddit URL formats
        # https://www.reddit.com/r/subreddit/comments/post_id/title/
        # https://reddit.com/r/subreddit/comments/post_id/title/
        # https://old.reddit.com/r/subreddit/comments/post_id/title/
        
        if '/comments/' in url:
            parts = url.split('/comments/')
            if len(parts) >= 2:
                post_id = parts[1].split('/')[0]
                subreddit = parts[0].split('/r/')[-1].split('/')[0]
                return post_id, subreddit
        
        return None, None
    except Exception:
        return None, None

def generate_cache_filename(post_id, author):
    """Generate a hash-based filename for caching"""
    combined = f"{author}_{post_id}"
    hash_object = hashlib.md5(combined.encode())
    return f"{hash_object.hexdigest()}.json"

def fetch_reddit_post_data(post_id, reddit_config):
    """Fetch Reddit post data using PRAW"""
    try:
        # Initialize Reddit instance
        reddit = praw.Reddit(
            client_id=reddit_config.get('client_id', ''),
            client_secret=reddit_config.get('client_secret', ''),
            username=reddit_config.get('username', ''),
            password=reddit_config.get('password', ''),
            user_agent=reddit_config.get('user_agent', 'RedditVideoCreator:v1.0')
        )
        
        # Get the submission
        submission = reddit.submission(id=post_id)
        
        # Prepare post data
        post_data = {
            'post_id': submission.id,
            'title': submission.title,
            'author': str(submission.author) if submission.author else '[deleted]',
            'subreddit': submission.subreddit.display_name,
            'selftext': submission.selftext,
            'url': submission.url,
            'score': submission.score,
            'upvote_ratio': submission.upvote_ratio,
            'num_comments': submission.num_comments,
            'created_utc': submission.created_utc,
            'is_self': submission.is_self,
            'comments': []
        }
          # Fetch top comments
        submission.comments.replace_more(limit=0)  # Remove "more comments" objects
        for comment in submission.comments.list()[:50]:  # Limit to top 50 comments
            try:
                # Check if comment has body and is not deleted/removed
                if (hasattr(comment, 'body') and 
                    comment.body and 
                    comment.body not in ['[deleted]', '[removed]']):
                    
                    comment_data = {
                        'id': getattr(comment, 'id', ''),
                        'author': str(comment.author) if comment.author else '[deleted]',
                        'body': getattr(comment, 'body', ''),
                        'score': getattr(comment, 'score', 0),
                        'created_utc': getattr(comment, 'created_utc', 0),
                        'is_submitter': getattr(comment, 'is_submitter', False),
                        'parent_id': getattr(comment, 'parent_id', '')
                    }
                    post_data['comments'].append(comment_data)
            except Exception as e:
                # Skip comments that cause errors (deleted, private, etc.)
                continue
        
        return True, post_data
        
    except Exception as e:
        return False, str(e)

def display_create_video_interface():
    """Display the create video interface"""
    clear_screen()
    hide_cursor()
    
    width, height = get_terminal_size()
    
    # Draw border
    left_border, right_border = draw_border(width, height)
    
    # Colors
    orange = "\033[38;5;208m"
    blue = "\033[34m"
    green = "\033[32m"
    yellow = "\033[93m"
    reset = "\033[0m"
    
    # Content
    content_lines = [
        "",
        f"{orange}CREATE VIDEO{reset}",
        "",
        "Enter a Reddit post URL to create a video:",
        "",
        "Supported formats:",
        "• https://reddit.com/r/subreddit/comments/post_id/title/",
        "• https://www.reddit.com/r/subreddit/comments/post_id/title/",
        "• https://old.reddit.com/r/subreddit/comments/post_id/title/",
        "",
        f"{yellow}Press ESC to return to main menu{reset}"
    ]
    
    # Calculate positioning
    content_height = len(content_lines) + 4
    available_lines = height - 2
    start_line = max(0, (available_lines - content_height) // 2)
    
    lines_printed = 1
    
    # Fill empty lines before content
    for i in range(start_line):
        if lines_printed < height - 1:
            print(left_border + " " * (width - 2) + right_border)
            lines_printed += 1
    
    # Display content
    for line in content_lines:
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

def handle_url_input():
    """Handle Reddit URL input with validation"""
    width, height = get_terminal_size()
    
    # Calculate input position
    input_row = height // 2 + 6
    max_input_width = width - 20
    
    # Display input prompt
    move_cursor(input_row - 1, 1)
    clear_line()
    prompt = "Enter Reddit URL:"
    prompt_line = center_text(prompt, width)
    print("│" + prompt_line + "│", end="", flush=True)
    
    # Input field
    move_cursor(input_row, 1)
    clear_line()
    
    user_input = ""
    
    while True:
        # Display current input
        display_text = user_input
        if len(display_text) > max_input_width:
            display_text = "..." + display_text[-(max_input_width-3):]
        
        input_field = f"[{display_text}{'_' if len(display_text) < max_input_width else ''}]"
        input_line = center_text(input_field, width)
        print("│" + input_line + "│", end="", flush=True)
        
        # Get user input
        key = msvcrt.getch()
        
        if key == b'\r':  # Enter
            if user_input.strip():
                return user_input.strip()
            
        elif key == b'\x1b':  # ESC
            return None
            
        elif key == b'\x08':  # Backspace
            if user_input:
                user_input = user_input[:-1]
                
        elif len(key) == 1 and 32 <= ord(key) <= 126:  # Printable characters
            if len(user_input) < 500:  # URL length limit
                user_input += key.decode('utf-8')
        
        # Refresh input display
        move_cursor(input_row, 1)
        clear_line()

def show_processing_screen(message):
    """Show processing screen with message"""
    clear_screen()
    hide_cursor()
    
    width, height = get_terminal_size()
    left_border, right_border = draw_border(width, height)
    
    # Colors
    yellow = "\033[93m"
    blue = "\033[34m"
    reset = "\033[0m"
    
    # Content
    content_lines = [
        "",
        f"{yellow}PROCESSING{reset}",
        "",
        message,
        "",
        f"{blue}Please wait...{reset}"
    ]
    
    # Calculate positioning
    content_height = len(content_lines)
    available_lines = height - 2
    start_line = max(0, (available_lines - content_height) // 2)
    
    lines_printed = 1
    
    # Fill empty lines before content
    for i in range(start_line):
        if lines_printed < height - 1:
            print(left_border + " " * (width - 2) + right_border)
            lines_printed += 1
    
    # Display content
    for line in content_lines:
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

def show_success_screen(post_data, cache_file):
    """Show success screen with post information"""
    clear_screen()
    hide_cursor()
    
    width, height = get_terminal_size()
    left_border, right_border = draw_border(width, height)
    
    # Colors
    green = "\033[32m"
    blue = "\033[34m"
    cyan = "\033[96m"
    reset = "\033[0m"
    
    # Content
    content_lines = [
        "",
        f"{green}✓ POST DATA FETCHED SUCCESSFULLY{reset}",
        "",
        f"Title: {post_data['title'][:60]}{'...' if len(post_data['title']) > 60 else ''}",
        f"Author: u/{post_data['author']}",
        f"Subreddit: r/{post_data['subreddit']}",
        f"Comments: {len(post_data['comments'])}",
        f"Score: {post_data['score']}",
        "",
        f"Data saved to: {cyan}{cache_file}{reset}",
        "",
        f"{blue}Press any key to return to main menu{reset}"
    ]
    
    # Calculate positioning
    content_height = len(content_lines)
    available_lines = height - 2
    start_line = max(0, (available_lines - content_height) // 2)
    
    lines_printed = 1
    
    # Fill empty lines before content
    for i in range(start_line):
        if lines_printed < height - 1:
            print(left_border + " " * (width - 2) + right_border)
            lines_printed += 1
    
    # Display content
    for line in content_lines:
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

def show_error_screen(error_message):
    """Show error screen with error details"""
    clear_screen()
    hide_cursor()
    
    width, height = get_terminal_size()
    left_border, right_border = draw_border(width, height)
    
    # Colors
    red = "\033[31m"
    blue = "\033[34m"
    reset = "\033[0m"
    
    # Content
    content_lines = [
        "",
        f"{red}✗ ERROR OCCURRED{reset}",
        "",
        "Failed to fetch Reddit post data:",
        "",
        error_message[:80] + ("..." if len(error_message) > 80 else ""),
        "",
        "Please check:",
        "• Reddit URL is valid",
        "• Reddit API credentials in settings",
        "• Internet connection",
        "",
        f"{blue}Press any key to return{reset}"
    ]
    
    # Calculate positioning
    content_height = len(content_lines)
    available_lines = height - 2
    start_line = max(0, (available_lines - content_height) // 2)
    
    lines_printed = 1
    
    # Fill empty lines before content
    for i in range(start_line):
        if lines_printed < height - 1:
            print(left_border + " " * (width - 2) + right_border)
            lines_printed += 1
    
    # Display content
    for line in content_lines:
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

def display_video_type_interface(post_data):
    """Display the video type selection interface"""
    clear_screen()
    hide_cursor()
    
    width, height = get_terminal_size()
    left_border, right_border = draw_border(width, height)
    
    # Colors
    orange = "\033[38;5;208m"
    blue = "\033[34m"
    green = "\033[32m"
    yellow = "\033[93m"
    cyan = "\033[96m"
    reset = "\033[0m"
    
    # Content
    content_lines = [
        "",
        f"{orange}SELECT VIDEO TYPE{reset}",
        "",
        f"Post: {post_data['title'][:50]}{'...' if len(post_data['title']) > 50 else ''}",
        f"Author: u/{post_data['author']} • r/{post_data['subreddit']}",
        f"Comments Available: {len(post_data['comments'])}",
        "",
        "Choose what to narrate:",
        ""
    ]
    
    # Video type options
    options = [
        "Narrate Post Description",
        "Narrate Top Comment",
        "Narrate Top 10 Comments"
    ]
    
    # Calculate positioning
    content_height = len(content_lines) + len(options) + 5
    available_lines = height - 2
    start_line = max(0, (available_lines - content_height) // 2)
    
    lines_printed = 1
    
    # Fill empty lines before content
    for i in range(start_line):
        if lines_printed < height - 1:
            print(left_border + " " * (width - 2) + right_border)
            lines_printed += 1
    
    # Display content
    for line in content_lines:
        if lines_printed < height - 1:
            centered_line = center_text(line, width)
            print(left_border + centered_line + right_border)
            lines_printed += 1
    
    # Store menu start position for updates
    menu_start_row = lines_printed + 1
    
    # Display options (will be updated by update function)
    for i, option in enumerate(options):
        if lines_printed < height - 1:
            option_text = f"  {i + 1}. {option}"
            centered_option = center_text(option_text, width)
            print(left_border + centered_option + right_border)
            lines_printed += 1
    
    # Add instructions
    if lines_printed < height - 1:
        print(left_border + " " * (width - 2) + right_border)
        lines_printed += 1
    
    if lines_printed < height - 1:
        instructions = "Use ↑↓ to navigate, Enter to select, ESC to go back"
        centered_instructions = center_text(instructions, width)
        print(left_border + centered_instructions + right_border)
        lines_printed += 1
    
    # Fill remaining lines
    while lines_printed < height - 1:
        print(left_border + " " * (width - 2) + right_border)
        lines_printed += 1
    
    draw_bottom_border(width)
    
    return menu_start_row, options

def update_video_type_selection(selected_option, options, menu_start_row, width):
    """Update only the menu selection without redrawing everything"""
    hide_cursor()
    cyan = "\033[96m"
    reset = "\033[0m"
    
    for i, option in enumerate(options):
        move_cursor(menu_start_row + i, 1)
        clear_line()
        
        if i == selected_option:
            # Highlighted option
            option_text = f"► {i + 1}. {option}"
            formatted_text = f"{cyan}{option_text}{reset}"
        else:
            # Normal option
            option_text = f"  {i + 1}. {option}"
            formatted_text = option_text
        
        centered_option = center_text(formatted_text, width)
        print("│" + centered_option + "│", end="", flush=True)
    
    show_cursor()

def process_video_content(post_data, video_type):
    """Process the selected video content type"""
    if video_type == 0:  # Narrate Post Description
        return process_post_description(post_data)
    elif video_type == 1:  # Narrate Top Comment
        return process_top_comment(post_data)
    elif video_type == 2:  # Narrate Top 10 Comments
        return process_top_10_comments(post_data)
    
    return None

def process_post_description(post_data):
    """Process post description for narration"""
    content = {
        'type': 'post_description',
        'title': post_data['title'],
        'author': post_data['author'],
        'subreddit': post_data['subreddit'],
        'text': post_data['selftext'] if post_data['selftext'] else "This post contains no description text.",
        'score': post_data['score']
    }
    return content

def process_top_comment(post_data):
    """Process top comment for narration"""
    if not post_data['comments']:
        return {
            'type': 'top_comment',
            'error': 'No comments available for this post'
        }
    
    # Sort comments by score and get the top one
    sorted_comments = sorted(post_data['comments'], key=lambda x: x['score'], reverse=True)
    top_comment = sorted_comments[0]
    
    content = {
        'type': 'top_comment',
        'post_title': post_data['title'],
        'post_author': post_data['author'],
        'subreddit': post_data['subreddit'],
        'comment': {
            'author': top_comment['author'],
            'text': top_comment['body'],
            'score': top_comment['score']
        }
    }
    return content

def process_top_10_comments(post_data):
    """Process top 10 comments for narration"""
    if not post_data['comments']:
        return {
            'type': 'top_10_comments',
            'error': 'No comments available for this post'
        }
    
    # Sort comments by score (highest first)
    sorted_comments = sorted(post_data['comments'], key=lambda x: x['score'], reverse=True)
    
    # Get top 10 (or less if not enough comments)
    top_comments = sorted_comments[:10]
    
    # Shuffle the array as requested
    random.shuffle(top_comments)
    
    content = {
        'type': 'top_10_comments',
        'post_title': post_data['title'],
        'post_author': post_data['author'],
        'subreddit': post_data['subreddit'],
        'total_comments': len(post_data['comments']),
        'selected_count': len(top_comments),
        'comments': []
    }
    
    for i, comment in enumerate(top_comments, 1):
        content['comments'].append({
            'number': i,
            'author': comment['author'],
            'text': comment['body'],
            'score': comment['score']
        })
    
    return content

def show_content_preview(content):
    """Show a preview of the processed content"""
    clear_screen()
    hide_cursor()
    
    width, height = get_terminal_size()
    left_border, right_border = draw_border(width, height)
    
    # Colors
    green = "\033[32m"
    blue = "\033[34m"
    cyan = "\033[96m"
    yellow = "\033[93m"
    reset = "\033[0m"
    
    content_lines = []
    
    if content.get('error'):
        content_lines = [
            "",
            f"{yellow}CONTENT PREVIEW{reset}",
            "",
            f"Error: {content['error']}",
            "",
            f"{blue}Press any key to go back{reset}"
        ]
    elif content['type'] == 'post_description':
        content_lines = [
            "",
            f"{green}✓ POST DESCRIPTION SELECTED{reset}",
            "",
            f"Title: {content['title'][:70]}{'...' if len(content['title']) > 70 else ''}",
            f"Author: u/{content['author']} • Score: {content['score']}",
            "",
            "Content Preview:",
            f"{content['text'][:200]}{'...' if len(content['text']) > 200 else ''}",
            "",
            f"{blue}Press any key to continue{reset}"
        ]
    elif content['type'] == 'top_comment':
        if 'comment' in content:
            content_lines = [
                "",
                f"{green}✓ TOP COMMENT SELECTED{reset}",
                "",
                f"Post: {content['post_title'][:60]}{'...' if len(content['post_title']) > 60 else ''}",
                f"Comment by: u/{content['comment']['author']} • Score: {content['comment']['score']}",
                "",
                "Comment Preview:",
                f"{content['comment']['text'][:200]}{'...' if len(content['comment']['text']) > 200 else ''}",
                "",
                f"{blue}Press any key to continue{reset}"
            ]
    elif content['type'] == 'top_10_comments':
        content_lines = [
            "",
            f"{green}✓ TOP 10 COMMENTS SELECTED{reset}",
            "",
            f"Post: {content['post_title'][:60]}{'...' if len(content['post_title']) > 60 else ''}",
            f"Selected: {content['selected_count']} comments (shuffled order)",
            "",
            "Comments Preview:"
        ]
        
        # Add preview of first few comments
        for i, comment in enumerate(content['comments'][:3], 1):
            content_lines.append(f"{i}. u/{comment['author']} (Score: {comment['score']})")
            content_lines.append(f"   {comment['text'][:80]}{'...' if len(comment['text']) > 80 else ''}")
            content_lines.append("")
        
        if len(content['comments']) > 3:
            content_lines.append(f"... and {len(content['comments']) - 3} more comments")
            content_lines.append("")
        
        content_lines.append(f"{blue}Press any key to continue{reset}")
    
    # Calculate positioning
    content_height = len(content_lines)
    available_lines = height - 2
    start_line = max(0, (available_lines - content_height) // 2)
    
    lines_printed = 1
    
    # Fill empty lines before content
    for i in range(start_line):
        if lines_printed < height - 1:
            print(left_border + " " * (width - 2) + right_border)
            lines_printed += 1
    
    # Display content
    for line in content_lines:
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

def show_video_type_selection_page(post_data):
    """Main video type selection page"""
    selected_option = 0
    
    while True:
        # Display interface
        menu_start_row, options = display_video_type_interface(post_data)
        update_video_type_selection(selected_option, options, menu_start_row, get_terminal_size()[0])
        
        # Handle input
        key = msvcrt.getch()
        
        if key == b'\xe0':  # Arrow keys
            key = msvcrt.getch()
            if key == b'H':  # Up
                selected_option = (selected_option - 1) % len(options)
                update_video_type_selection(selected_option, options, menu_start_row, get_terminal_size()[0])
            elif key == b'P':  # Down
                selected_option = (selected_option + 1) % len(options)
                update_video_type_selection(selected_option, options, menu_start_row, get_terminal_size()[0])
        elif key == b'\r':  # Enter
            # Process selected video type
            content = process_video_content(post_data, selected_option)
            if content:
                show_content_preview(content)
                return content
        elif key == b'\x1b':  # ESC
            return None  # Go back to URL input


def show_create_video_page():
    """Main entry point for create video functionality"""
    # Create temp directory for caching
    create_temp_directory()
    
    while True:
        # Step 1: Display interface and get URL input
        display_create_video_interface()
        reddit_url = handle_url_input()
        
        if reddit_url is None:  # User pressed ESC
            return
        
        # Step 2: Extract post information from URL
        post_id, subreddit = extract_post_info_from_url(reddit_url)
        
        if not post_id or not subreddit:
            show_error_screen("Invalid Reddit URL format. Please check the URL and try again.")
            continue
        
        # Step 3: Load Reddit configuration
        reddit_config = load_reddit_config()
        
        if not reddit_config.get('client_id') or not reddit_config.get('client_secret'):
            show_error_screen("Reddit API credentials not found. Please configure them in Settings.")
            continue
        
        # Step 4: Check if data is already cached
        temp_dir = Path("temp")
        cache_filename = generate_cache_filename(post_id, "unknown")  # We'll update with real author later
        
        # Try to fetch post data
        show_processing_screen("Fetching Reddit post data...")
        success, result = fetch_reddit_post_data(post_id, reddit_config)
        
        if not success:
            show_error_screen(f"Failed to fetch post data: {result}")
            continue
        
        post_data = result
        
        # Update cache filename with real author and save data
        author = post_data.get('author', 'unknown') if isinstance(post_data, dict) else 'unknown'
        cache_filename = generate_cache_filename(post_id, author)
        cache_file_path = temp_dir / cache_filename
        
        try:
            with open(cache_file_path, 'w', encoding='utf-8') as f:
                json.dump(post_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            show_error_screen(f"Failed to save post data: {str(e)}")
            continue
          # Step 5: Show video type selection
        selected_content = show_video_type_selection_page(post_data)
        
        if selected_content is None:  # User pressed ESC from video type selection
            continue  # Go back to URL input
        
        # Step 6: Generate TTS audio
        tts_config = load_tts_config()
        service = tts_config.get('service', 'pyttsx3')
        
        # Show TTS processing screen
        content_type_names = {
            'post_description': 'Post Description',
            'top_comment': 'Top Comment',
            'top_10_comments': 'Top 10 Comments'
        }
        content_type_display = content_type_names.get(selected_content['type'], 'Unknown')
        show_tts_processing_screen(content_type_display, service.upper())
        
        # Generate the audio
        success, result = generate_tts_audio(selected_content)
        
        if success:
            # Show success screen with audio file path
            show_tts_success_screen(result)
        else:
            # Show error screen
            show_tts_error_screen(result)
        
        # Return to main menu after processing
        return

def load_tts_config():
    """Load TTS configuration from config.toml"""
    try:
        config_path = Path("config.toml")
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = toml.load(f)
                return config.get('text_to_speech', {})
        return {}
    except Exception:
        return {}

def create_output_directory():
    """Create output directory if it doesn't exist"""
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    return output_dir

def clean_text_for_tts(text):
    """Clean and format text for TTS by removing markdown and special formatting"""
    import re
    
    if not text:
        return ""
    
    # Remove markdown formatting
    # Remove bold/italic markers
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'\1', text)  # ***bold italic***
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)      # **bold**
    text = re.sub(r'\*(.+?)\*', r'\1', text)          # *italic*
    text = re.sub(r'___(.+?)___', r'\1', text)        # ___underline___
    text = re.sub(r'__(.+?)__', r'\1', text)          # __underline__
    text = re.sub(r'_(.+?)_', r'\1', text)            # _italic_
    
    # Remove strikethrough
    text = re.sub(r'~~(.+?)~~', r'\1', text)
    
    # Remove code blocks and inline code
    text = re.sub(r'```[\s\S]*?```', '', text)        # Code blocks
    text = re.sub(r'`(.+?)`', r'\1', text)            # Inline code
    
    # Remove links but keep the text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # [text](url)
    text = re.sub(r'<([^>]+)>', r'\1', text)               # <url>
    
    # Remove Reddit-specific formatting
    text = re.sub(r'/u/\w+', '', text)                # Remove /u/username
    text = re.sub(r'/r/\w+', '', text)                # Remove /r/subreddit
    text = re.sub(r'u/\w+', '', text)                 # Remove u/username
    text = re.sub(r'r/\w+', '', text)                 # Remove r/subreddit
    
    # Remove quotes and blockquotes
    text = re.sub(r'^&gt;.*$', '', text, flags=re.MULTILINE)  # Remove quoted lines
    text = re.sub(r'^>.*$', '', text, flags=re.MULTILINE)     # Remove quoted lines
    
    # Remove edit markers
    text = re.sub(r'EDIT:.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'Edit:.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'edit:.*$', '', text, flags=re.MULTILINE)
    
    # Clean up HTML entities
    text = text.replace('&amp;', 'and')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')
    text = text.replace('&#x27;', "'")
    text = text.replace('&#39;', "'")
    
    # Remove extra whitespace and newlines
    text = re.sub(r'\n\s*\n', '. ', text)            # Replace double newlines with period
    text = re.sub(r'\n', ' ', text)                  # Replace single newlines with space
    text = re.sub(r'\s+', ' ', text)                 # Replace multiple spaces with single
    
    # Clean up punctuation
    text = re.sub(r'\.+', '.', text)                 # Multiple periods to single
    text = re.sub(r'\?+', '?', text)                 # Multiple questions to single
    text = re.sub(r'!+', '!', text)                  # Multiple exclamations to single
    
    return text.strip()

def prepare_audio_segments(content):
    """Prepare multiple audio segments based on content type"""
    segments = []
    
    if content['type'] == 'post_description':
        # Segment 1: Title
        title_text = clean_text_for_tts(content['title'])
        if title_text:
            segments.append({
                'type': 'title',
                'text': title_text,
                'filename_suffix': 'title',
                'description': f"Post Title: {content['title'][:50]}{'...' if len(content['title']) > 50 else ''}"
            })
        
        # Segment 2: Post content (if available)
        if content['text'] and content['text'] != "This post contains no description text.":
            content_text = clean_text_for_tts(content['text'])
            if content_text:
                segments.append({
                    'type': 'content',
                    'text': content_text,
                    'filename_suffix': 'content',
                    'description': f"Post Content ({len(content_text)} characters)"
                })
    
    elif content['type'] == 'top_comment':
        if content.get('error'):
            return [{'type': 'error', 'text': content['error'], 'filename_suffix': 'error', 'description': 'Error message'}]
        
        # Segment 1: Title
        title_text = clean_text_for_tts(content['post_title'])
        if title_text:
            segments.append({
                'type': 'title',
                'text': title_text,
                'filename_suffix': 'title',
                'description': f"Post Title: {content['post_title'][:50]}{'...' if len(content['post_title']) > 50 else ''}"
            })
        
        # Segment 2: Top comment
        comment_text = clean_text_for_tts(content['comment']['text'])
        if comment_text:
            segments.append({
                'type': 'comment',
                'text': comment_text,
                'filename_suffix': 'top_comment',
                'description': f"Top Comment by u/{content['comment']['author']} (Score: {content['comment']['score']})"
            })
    
    elif content['type'] == 'top_10_comments':
        if content.get('error'):
            return [{'type': 'error', 'text': content['error'], 'filename_suffix': 'error', 'description': 'Error message'}]
        
        # Segment 1: Title
        title_text = clean_text_for_tts(content['post_title'])
        if title_text:
            segments.append({
                'type': 'title',
                'text': title_text,
                'filename_suffix': 'title',
                'description': f"Post Title: {content['post_title'][:50]}{'...' if len(content['post_title']) > 50 else ''}"
            })
        
        # Segments 2-11: Individual comments
        for i, comment in enumerate(content['comments'], 1):
            comment_text = clean_text_for_tts(comment['text'])
            if comment_text:
                segments.append({
                    'type': 'comment',
                    'text': comment_text,
                    'filename_suffix': f'comment_{i:02d}',
                    'description': f"Comment #{i} by u/{comment['author']} (Score: {comment['score']})"
                })
    
    return segments

def generate_audio_filename(content):
    """Generate a unique filename for the audio file"""
    # Create a hash based on content type and key identifiers
    if content['type'] == 'post_description':
        identifier = f"{content['author']}_{content['title'][:50]}_post"
    elif content['type'] == 'top_comment':
        identifier = f"{content['post_author']}_{content['post_title'][:50]}_top_comment"
    elif content['type'] == 'top_10_comments':
        identifier = f"{content['post_author']}_{content['post_title'][:50]}_top10"
    else:
        identifier = "unknown_content"
    
    # Create hash and return filename
    hash_object = hashlib.md5(identifier.encode())
    return f"audio_{hash_object.hexdigest()[:12]}"

def get_male_voice_id():
    """Get a male voice ID for pyttsx3"""
    try:
        from tts import get_available_voices
        voices = get_available_voices()
        
        # Look for male voices first
        for voice in voices:
            gender = voice.get('gender', '').lower()
            name = voice.get('name', '').lower()
            
            # Check for explicitly male voices
            if 'male' in gender and 'female' not in gender:
                return voice['id']
            
            # Check for common male voice names
            male_indicators = ['david', 'mark', 'paul', 'richard', 'james', 'zira', 'male']
            if any(indicator in name for indicator in male_indicators):
                return voice['id']
        
        # If no explicitly male voice found, return the first available voice
        if voices:
            return voices[0]['id']
            
    except Exception:
        pass
    
    return None

def generate_tts_audio(content):
    """Generate multiple separate TTS audio files based on content"""
    # Load TTS configuration
    tts_config = load_tts_config()
    service = tts_config.get('service', 'pyttsx3')
    
    # Prepare audio segments
    segments = prepare_audio_segments(content)
    
    if not segments:
        return False, "No valid content segments for TTS generation"
    
    # Create output directory
    output_dir = create_output_directory()
    
    # Generate base filename
    base_filename = generate_audio_filename(content)
    
    generated_files = []
    failed_segments = []
    
    try:
        for segment in segments:
            if not segment['text'].strip():
                continue
            
            # Create filename for this segment
            segment_filename = f"{base_filename}_{segment['filename_suffix']}"
            
            success = False
            
            if service.lower() == 'gtts':
                # Use gTTS (online service)
                if not test_gtts_availability():
                    return False, "gTTS is not available. Please install it or check internet connection."
                
                audio_file = output_dir / f"{segment_filename}.mp3"
                language = tts_config.get('voice', 'en')
                speed_setting = float(tts_config.get('speed', '1.0'))
                slow_speech = speed_setting < 0.8
                
                success = create_audio_gtts(
                    text=segment['text'],
                    output_path=str(audio_file),
                    language=language,
                    slow=slow_speech
                )
            
            elif service.lower() == 'pyttsx3':
                # Use pyttsx3 (offline service)
                if not test_pyttsx3_availability():
                    return False, "pyttsx3 is not available. Please install it."
                
                audio_file = output_dir / f"{segment_filename}.wav"
                
                # Get male voice
                male_voice_id = get_male_voice_id()
                
                # Convert speed and volume from string to appropriate values
                speed_setting = float(tts_config.get('speed', '1.0'))
                volume_setting = float(tts_config.get('volume', '0.8'))
                
                # Convert speed (0.1-2.0) to rate (words per minute)
                base_rate = 175
                rate = int(base_rate * speed_setting)
                
                success = create_audio_pyttsx3(
                    text=segment['text'],
                    output_path=str(audio_file),
                    voice_id=male_voice_id,
                    rate=rate,
                    volume=volume_setting
                )
            
            if success:
                # Get file size for display
                try:
                    file_size = Path(audio_file).stat().st_size
                    size_kb = file_size / 1024
                    size_display = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb/1024:.2f} MB"
                except:
                    size_display = "Unknown size"
                
                generated_files.append({
                    'segment_type': segment['type'],
                    'filename': str(audio_file),
                    'filename_short': Path(audio_file).name,
                    'text_preview': segment['text'][:100] + ('...' if len(segment['text']) > 100 else ''),
                    'description': segment.get('description', 'Audio segment'),
                    'file_size': size_display,
                    'duration_estimate': f"~{len(segment['text']) // 10}s"  # Rough estimate: 10 chars per second
                })
            else:
                failed_segments.append(segment['filename_suffix'])
        
        if generated_files:
            success_message = f"Generated {len(generated_files)} separate audio files"
            if failed_segments:
                success_message += f" ({len(failed_segments)} failed: {', '.join(failed_segments)})"
            
            return True, {
                'message': success_message,
                'files': generated_files,
                'total_files': len(generated_files),
                'failed_count': len(failed_segments),
                'service_used': service.upper(),
                'base_filename': base_filename
            }
        else:
            return False, f"Failed to generate any audio files. Service: {service}"
            
    except Exception as e:
        return False, f"Error during TTS generation: {str(e)}"

def show_tts_processing_screen(content_type, service):
    """Show enhanced TTS processing screen"""
    clear_screen()
    hide_cursor()
    
    width, height = get_terminal_size()
    left_border, right_border = draw_border(width, height)
    
    # Colors
    yellow = "\033[93m"
    blue = "\033[34m"
    cyan = "\033[96m"
    green = "\033[32m"
    reset = "\033[0m"
    
    # Content
    content_lines = [
        "",
        f"{yellow}GENERATING SEPARATE AUDIO FILES{reset}",
        "",
        f"Content Type: {green}{content_type}{reset}",
        f"TTS Service: {cyan}{service}{reset}",
        "",
        f"{blue}Processing each text segment into individual audio files...{reset}",
        "",
        "• Post title → title audio file",
        "• Content/Comments → separate audio files", 
        "",
        f"{blue}This allows for flexible video editing and mixing{reset}"
    ]
    
    # Calculate positioning
    content_height = len(content_lines)
    available_lines = height - 2
    start_line = max(0, (available_lines - content_height) // 2)
    
    lines_printed = 1
    
    # Fill empty lines before content
    for i in range(start_line):
        if lines_printed < height - 1:
            print(left_border + " " * (width - 2) + right_border)
            lines_printed += 1
    
    # Display content
    for line in content_lines:
        if lines_printed < height - 1:
            centered_line = center_text(line, width)
            print(left_border + centered_line + right_border)
            lines_printed += 1
    
    # Fill remaining lines
    while lines_printed < height - 1:
        print(left_border + " " * (width - 2) + right_border)
        lines_printed += 1
    
    draw_bottom_border(width)

def show_tts_success_screen(result_data):
    """Show enhanced TTS success screen with detailed file information"""
    clear_screen()
    hide_cursor()
    
    width, height = get_terminal_size()
    left_border, right_border = draw_border(width, height)
    
    # Colors
    green = "\033[32m"
    blue = "\033[34m"
    cyan = "\033[96m"
    yellow = "\033[93m"
    magenta = "\033[35m"
    reset = "\033[0m"
    
    # Calculate total file size
    total_size = 0
    for file_info in result_data['files']:
        try:
            total_size += Path(file_info['filename']).stat().st_size
        except:
            pass
    
    size_mb = total_size / (1024 * 1024)
    size_text = f"{size_mb:.2f} MB" if size_mb >= 1 else f"{total_size / 1024:.1f} KB"
    
    # Content header
    content_lines = [
        "",
        f"{green}✓ SEPARATE AUDIO FILES GENERATED SUCCESSFULLY{reset}",
        "",
        f"Service Used: {cyan}{result_data['service_used']}{reset}",
        f"Generated Files: {yellow}{result_data['total_files']}{reset}",
        f"Total Size: {magenta}{size_text}{reset}",
        f"Base Filename: {result_data['base_filename']}",
        ""
    ]
    
    # Add detailed file information
    content_lines.append(f"{cyan}GENERATED AUDIO FILES:{reset}")
    content_lines.append("")
    
    max_files_to_show = min(8, len(result_data['files']))
    for i, file_info in enumerate(result_data['files'][:max_files_to_show], 1):
        segment_type = file_info['segment_type'].replace('_', ' ').title()
        
        # File header
        content_lines.append(f"{yellow}{i}. {segment_type}{reset} - {file_info['filename_short']}")
        content_lines.append(f"   {file_info['description']}")
        content_lines.append(f"   Size: {file_info['file_size']} • Duration: {file_info['duration_estimate']}")
        content_lines.append(f"   Preview: {file_info['text_preview'][:60]}{'...' if len(file_info['text_preview']) > 60 else ''}")
        content_lines.append("")
    
    # Show remaining count if there are more files
    if len(result_data['files']) > max_files_to_show:
        remaining = len(result_data['files']) - max_files_to_show
        content_lines.append(f"{cyan}... and {remaining} more audio files{reset}")
        content_lines.append("")
    
    # Show warning if some failed
    if result_data.get('failed_count', 0) > 0:
        content_lines.append(f"{yellow}Warning: {result_data['failed_count']} segments failed to generate{reset}")
        content_lines.append("")
    
    # Footer information
    content_lines.extend([
        f"Files saved to: {cyan}output/{reset}",
        "",
        f"{blue}Each segment is a separate audio file for video editing{reset}",
        f"{blue}Press any key to return to main menu{reset}"
    ])
    
    # Calculate positioning for scrollable content
    content_height = len(content_lines)
    available_lines = height - 2
    
    if content_height <= available_lines:
        # Content fits, center it
        start_line = max(0, (available_lines - content_height) // 2)
        lines_printed = 1
        
        # Fill empty lines before content
        for i in range(start_line):
            if lines_printed < height - 1:
                print(left_border + " " * (width - 2) + right_border)
                lines_printed += 1
        
        # Display content
        for line in content_lines:
            if lines_printed < height - 1:
                centered_line = center_text(line, width)
                print(left_border + centered_line + right_border)
                lines_printed += 1
    else:
        # Content doesn't fit, show from top with more files visible
        lines_printed = 1
        for line in content_lines[:available_lines - 2]:  # Leave space for continuation message
            if lines_printed < height - 2:
                centered_line = center_text(line, width)
                print(left_border + centered_line + right_border)
                lines_printed += 1
        
        # Add continuation message
        if lines_printed < height - 1:
            continuation_msg = f"{yellow}... content continues (scroll up to see all){reset}"
            centered_line = center_text(continuation_msg, width)
            print(left_border + centered_line + right_border)
            lines_printed += 1
    
    # Fill remaining lines
    while lines_printed < height - 1:
        print(left_border + " " * (width - 2) + right_border)
        lines_printed += 1
    
    draw_bottom_border(width)
    
    show_cursor()
    msvcrt.getch()

def show_tts_error_screen(error_message):
    """Show enhanced TTS error screen with troubleshooting"""
    clear_screen()
    hide_cursor()
    
    width, height = get_terminal_size()
    left_border, right_border = draw_border(width, height)
    
    # Colors
    red = "\033[31m"
    blue = "\033[34m"
    yellow = "\033[93m"
    cyan = "\033[96m"
    reset = "\033[0m"
    
    # Content
    content_lines = [
        "",
        f"{red}✗ AUDIO FILE GENERATION FAILED{reset}",
        "",
        f"{yellow}Error Details:{reset}",
        error_message[:70] + ("..." if len(error_message) > 70 else ""),
        "",
        f"{cyan}Troubleshooting Steps:{reset}",
        "• Check TTS service configuration in Settings",
        "• Verify required packages are installed:",
        "  - For gTTS: pip install gtts",
        "  - For pyttsx3: pip install pyttsx3",
        "• Check internet connection (required for gTTS)",
        "• Try switching TTS service in Settings",
        "• Ensure output directory is writable",
        "",
        f"{blue}Press any key to return to main menu{reset}"
    ]
    
    # Calculate positioning
    content_height = len(content_lines)
    available_lines = height - 2
    start_line = max(0, (available_lines - content_height) // 2)
    
    lines_printed = 1
    
    # Fill empty lines before content
    for i in range(start_line):
        if lines_printed < height - 1:
            print(left_border + " " * (width - 2) + right_border)
            lines_printed += 1
    
    # Display content
    for line in content_lines:
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
