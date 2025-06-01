import sys
import msvcrt
from utils import clear_screen

def show_credits_page():
    """Display the Credits page"""
    clear_screen()
    
    # Header
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                          CREDITS                            ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()
    
    # Content
    print("👨‍💻 Reddit Video Creator v0.1 BETA")
    print()
    print("   🏗️  Development Team:")
    print("      • Lead Developer: Your Name")
    print("      • UI/UX Design: Your Name")
    print("      • Testing: Community Contributors")
    print()
    print("   🛠️  Built With:")
    print("      • Python 3.12+")
    print("      • OpenAI TTS (Text-to-Speech)")
    print("      • MoviePy (Video Processing)")
    print("      • PRAW (Reddit API)")
    print("      • Pillow (Image Processing)")
    print("      • FFmpeg (Media Processing)")
    print()
    print("   🎮 Background Content:")
    print("      • Minecraft: Mojang Studios")
    print("      • Subway Surfers: SYBO")
    print("      • Various gameplay footage from content creators")
    print()
    print("   🎵 Audio Resources:")
    print("      • Background Music: Royalty-free tracks")
    print("      • Sound Effects: Freesound.org contributors")
    print("      • Text-to-Speech: OpenAI & Google Cloud")
    print()
    print("   📄 License:")
    print("      • This project is open source")
    print("      • Licensed under MIT License")
    print("      • See LICENSE file for details")
    print()
    print("   🌟 Special Thanks:")
    print("      • Reddit community for inspiration")
    print("      • Open source contributors")
    print("      • Beta testers and feedback providers")
    print()
    print("   📧 Contact:")
    print("      • GitHub: github.com/yourusername/reddit-video-creator")
    print("      • Email: your.email@example.com")
    print("      • Discord: YourDiscord#1234")
    print()
    print("Made with ❤️  for the content creation community")
    print()
    print("Press any key to return to main menu...")
    
    # Wait for user input
    msvcrt.getch()
