# filepath: c:\Users\KIIT\Documents\GitHub\reddit-video-creator\tts\pyttsx3_module.py
import os
import tempfile
from typing import Optional, Dict, List

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    pyttsx3 = None


def test_pyttsx3_availability() -> bool:
    """Test if pyttsx3 is available and working"""
    if not PYTTSX3_AVAILABLE:
        return False
    
    try:
        engine = pyttsx3.init()
        engine.stop()
        return True
    except Exception:
        return False


def get_available_voices() -> List[Dict[str, str]]:
    """Get available voices for pyttsx3"""
    if not PYTTSX3_AVAILABLE:
        return []
    
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        voice_list = []
        
        if voices:
            for voice in voices:
                voice_info = {
                    'id': voice.id,
                    'name': voice.name,
                    'gender': getattr(voice, 'gender', 'unknown'),
                    'age': getattr(voice, 'age', 'unknown')
                }
                voice_list.append(voice_info)
        
        engine.stop()
        return voice_list
    except Exception as e:
        print(f"Error getting voices: {str(e)}")
        return []


def get_default_voice() -> Optional[str]:
    """Get the default voice ID"""
    voices = get_available_voices()
    if voices:
        return voices[0]['id']
    return None


def create_audio_pyttsx3(text: str, output_path: str, voice_id: Optional[str] = None,
                        rate: int = 200, volume: float = 0.9) -> bool:
    """
    Generate audio file using pyttsx3
    
    Args:
        text: Text to convert to speech
        output_path: Path where to save the audio file
        voice_id: Voice ID to use (optional)
        rate: Speech rate (words per minute, default: 200)
        volume: Volume level (0.0 to 1.0, default: 0.9)
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not PYTTSX3_AVAILABLE:
        print("Error: pyttsx3 is not available. Please install it with: pip install pyttsx3")
        return False
    
    if not text.strip():
        print("Error: No text provided for speech generation")
        return False
    
    try:
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Initialize the TTS engine
        engine = pyttsx3.init()
        
        # Set voice if specified
        if voice_id:
            engine.setProperty('voice', voice_id)
        
        # Set speech rate
        engine.setProperty('rate', rate)
        
        # Set volume
        engine.setProperty('volume', volume)
        
        # Create temporary file with .wav extension
        temp_path = None
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            temp_path = tmp_file.name
        
        # Save audio to temporary file
        engine.save_to_file(text, temp_path)
        engine.runAndWait()
        engine.stop()
        
        # Move to final destination
        if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
            if os.path.exists(output_path):
                os.remove(output_path)
            os.rename(temp_path, output_path)
            print(f"Audio file created successfully: {output_path}")
            return True
        else:
            print("Error: Failed to create audio file")
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
            return False
            
    except Exception as e:
        print(f"Error generating audio with pyttsx3: {str(e)}")
        # Clean up temporary file if it exists
        try:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
        except:
            pass
        return False


def set_voice_properties(voice_id: Optional[str] = None, rate: int = 200, 
                        volume: float = 0.9) -> Dict[str, any]:
    """
    Test and return voice properties
    
    Args:
        voice_id: Voice ID to test
        rate: Speech rate to test
        volume: Volume level to test
    
    Returns:
        Dict with voice properties and test results
    """
    if not PYTTSX3_AVAILABLE:
        return {'available': False, 'error': 'pyttsx3 not available'}
    
    try:
        engine = pyttsx3.init()
        
        # Get current properties
        current_voice = engine.getProperty('voice')
        current_rate = engine.getProperty('rate')
        current_volume = engine.getProperty('volume')
        
        # Test setting new properties
        if voice_id:
            engine.setProperty('voice', voice_id)
        engine.setProperty('rate', rate)
        engine.setProperty('volume', volume)
        
        # Get updated properties
        new_voice = engine.getProperty('voice')
        new_rate = engine.getProperty('rate')
        new_volume = engine.getProperty('volume')
        
        engine.stop()
        
        return {
            'available': True,
            'original': {
                'voice': current_voice,
                'rate': current_rate,
                'volume': current_volume
            },
            'updated': {
                'voice': new_voice,
                'rate': new_rate,
                'volume': new_volume
            }
        }
        
    except Exception as e:
        return {'available': False, 'error': str(e)}


def get_pyttsx3_info() -> Dict[str, any]:
    """Get information about pyttsx3 configuration"""
    return {
        'available': PYTTSX3_AVAILABLE,
        'voices': get_available_voices(),
        'default_voice': get_default_voice(),
        'output_format': 'wav',
        'features': {
            'voice_selection': True,
            'rate_control': True,
            'volume_control': True,
            'offline_capable': True,
            'internet_required': False
        }
    }