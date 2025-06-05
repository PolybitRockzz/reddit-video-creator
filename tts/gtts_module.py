# filepath: c:\Users\KIIT\Documents\GitHub\reddit-video-creator\tts\gtts_module.py
import os
import tempfile
from typing import Optional, Dict, List

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    gTTS = None


def test_gtts_availability() -> bool:
    """Test if gTTS is available and working"""
    return GTTS_AVAILABLE


def get_supported_languages() -> Dict[str, str]:
    """Get supported languages for gTTS"""
    if not GTTS_AVAILABLE:
        return {}
    
    try:
        from gtts.lang import tts_langs
        return tts_langs()
    except Exception:
        # Fallback to common languages
        return {
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'ja': 'Japanese',
            'ko': 'Korean',
            'zh': 'Chinese'
        }


def create_audio_gtts(text: str, output_path: str, language: str = 'en', 
                     slow: bool = False) -> bool:
    """
    Generate audio file using gTTS
    
    Args:
        text: Text to convert to speech
        output_path: Path where to save the audio file
        language: Language code (default: 'en')
        slow: Whether to speak slowly (default: False)
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not GTTS_AVAILABLE:
        print("Error: gTTS is not available. Please install it with: pip install gtts")
        return False
    
    if not text.strip():
        print("Error: No text provided for speech generation")
        return False
    
    try:
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Create gTTS object
        tts = gTTS(text=text, lang=language, slow=slow)
        
        # Save to temporary file first
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            temp_path = tmp_file.name
            tts.save(temp_path)
        
        # Move to final destination
        if os.path.exists(temp_path):
            if os.path.exists(output_path):
                os.remove(output_path)
            os.rename(temp_path, output_path)
            print(f"Audio file created successfully: {output_path}")
            return True
        else:
            print("Error: Failed to create temporary audio file")
            return False
            
    except Exception as e:
        print(f"Error generating audio with gTTS: {str(e)}")
        # Clean up temporary file if it exists
        try:
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.remove(temp_path)
        except:
            pass
        return False


def get_gtts_info() -> Dict[str, any]:
    """Get information about gTTS configuration"""
    return {
        'available': GTTS_AVAILABLE,
        'supported_languages': get_supported_languages(),
        'default_language': 'en',
        'output_format': 'mp3',
        'features': {
            'slow_speech': True,
            'language_selection': True,
            'internet_required': True
        }
    }