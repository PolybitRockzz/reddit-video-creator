import sys
import msvcrt
from utils import clear_screen

def show_settings_page():
    """Display the Settings page"""
    clear_screen()
    
    # Header
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                          SETTINGS                           ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()
    
    # Content
    print("⚙️  Application Settings:")
    print()
    print("   🎵 Audio Settings")
    print("      • Voice: English (US) - Male")
    print("      • Speech Rate: Normal")
    print("      • Background Music: Enabled")
    print("      • Music Volume: 30%")
    print()
    print("   🎬 Video Settings")
    print("      • Resolution: 1920x1080 (Full HD)")
    print("      • Frame Rate: 30 FPS")
    print("      • Background: Minecraft Parkour")
    print("      • Text Animation: Typewriter")
    print()
    print("   📁 Output Settings")
    print("      • Output Directory: ./output/")
    print("      • Video Format: MP4")
    print("      • Quality: High")
    print("      • Compression: Balanced")
    print()
    print("   🌐 Reddit Settings")
    print("      • API Key: Not configured")
    print("      • Default Subreddit: r/AskReddit")
    print("      • Post Filter: Hot")
    print("      • Max Comments: 10")
    print()
    print("   🎨 Theme Settings")
    print("      • UI Theme: Dark")
    print("      • Accent Color: Orange")
    print("      • Font Size: Medium")
    print()
    print("🚧 Settings configuration is coming soon!")
    print("These settings will be fully configurable in the next update.")
    print()
    print("Press any key to return to main menu...")
    
    # Wait for user input
    msvcrt.getch()
