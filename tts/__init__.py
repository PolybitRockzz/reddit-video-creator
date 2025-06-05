# filepath: c:\Users\KIIT\Documents\GitHub\reddit-video-creator\tts\__init__.py
# TTS Module
# Contains text-to-speech generation functions

from .gtts_module import (
    create_audio_gtts,
    test_gtts_availability,
    get_supported_languages,
    get_gtts_info
)

from .pyttsx3_module import (
    create_audio_pyttsx3,
    test_pyttsx3_availability,
    get_available_voices,
    get_default_voice,
    set_voice_properties,
    get_pyttsx3_info
)

__all__ = [
    # gTTS functions
    'create_audio_gtts',
    'test_gtts_availability', 
    'get_supported_languages',
    'get_gtts_info',
    
    # pyttsx3 functions
    'create_audio_pyttsx3',
    'test_pyttsx3_availability',
    'get_available_voices',
    'get_default_voice',
    'set_voice_properties',
    'get_pyttsx3_info'
]