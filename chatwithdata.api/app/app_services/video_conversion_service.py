import os
import tempfile
from typing import Optional, Dict, Any, List, Tuple
try:
    import moviepy as mp
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    mp = None
import ffmpeg
from app.app_core.exceptions import FileProcessingError
from app.app_services.file_service import FileService


class VideoConversionService:
    """Service for handling video conversions between various formats."""
    
    # Supported input formats
    SUPPORTED_INPUT_FORMATS = {
        'MOV', 'MKV', 'AVI', 'MP4', 'WMV', 'FLV', 'WEBM', 'M4V', '3GP', 'OGV'
    }
    
    # Supported output formats
    SUPPORTED_OUTPUT_FORMATS = {
        'MP4', 'MP3', 'AVI', 'MOV', 'MKV', 'WMV', 'FLV', 'WEBM', 'M4V', '3GP', 'OGV'
    }
    
    @staticmethod
    def mov_to_mp4(input_path: str, quality: str = "medium") -> str:
        """Convert MOV file to MP4 format."""
        try:
            if not MOVIEPY_AVAILABLE:
                raise FileProcessingError("MoviePy is not available. Please install moviepy package.")
            
            if not os.path.exists(input_path):
                raise FileProcessingError(f"Input MOV file not found: {input_path}")
            
            # Generate output path
            output_path = FileService.get_output_path(input_path, ".mp4")
            
            # Load video
            video = mp.VideoFileClip(input_path)
            
            # Set quality parameters
            quality_settings = VideoConversionService._get_quality_settings(quality)
            
            # Write MP4 file
            video.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                bitrate=quality_settings['bitrate'],
                fps=quality_settings['fps'],
                preset=quality_settings['preset']
            )
            
            # Close video to free memory
            video.close()
            
            return output_path
            
        except Exception as e:
            raise FileProcessingError(f"MOV to MP4 conversion failed: {str(e)}")
    
    @staticmethod
    def mkv_to_mp4(input_path: str, quality: str = "medium") -> str:
        """Convert MKV file to MP4 format."""
        try:
            if not MOVIEPY_AVAILABLE:
                raise FileProcessingError("MoviePy is not available. Please install moviepy package.")
            
            if not os.path.exists(input_path):
                raise FileProcessingError(f"Input MKV file not found: {input_path}")
            
            # Generate output path
            output_path = FileService.get_output_path(input_path, ".mp4")
            
            # Load video
            video = mp.VideoFileClip(input_path)
            
            # Set quality parameters
            quality_settings = VideoConversionService._get_quality_settings(quality)
            
            # Write MP4 file
            video.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                bitrate=quality_settings['bitrate'],
                fps=quality_settings['fps'],
                preset=quality_settings['preset']
            )
            
            # Close video to free memory
            video.close()
            
            return output_path
            
        except Exception as e:
            raise FileProcessingError(f"MKV to MP4 conversion failed: {str(e)}")
    
    @staticmethod
    def avi_to_mp4(input_path: str, quality: str = "medium") -> str:
        """Convert AVI file to MP4 format."""
        try:
            if not MOVIEPY_AVAILABLE:
                raise FileProcessingError("MoviePy is not available. Please install moviepy package.")
            
            if not os.path.exists(input_path):
                raise FileProcessingError(f"Input AVI file not found: {input_path}")
            
            # Generate output path
            output_path = FileService.get_output_path(input_path, ".mp4")
            
            # Load video
            video = mp.VideoFileClip(input_path)
            
            # Set quality parameters
            quality_settings = VideoConversionService._get_quality_settings(quality)
            
            # Write MP4 file
            video.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                bitrate=quality_settings['bitrate'],
                fps=quality_settings['fps'],
                preset=quality_settings['preset']
            )
            
            # Close video to free memory
            video.close()
            
            return output_path
            
        except Exception as e:
            raise FileProcessingError(f"AVI to MP4 conversion failed: {str(e)}")
    
    @staticmethod
    def mp4_to_mp3(input_path: str, bitrate: str = "192k") -> str:
        """Convert MP4 file to MP3 audio format."""
        try:
            if not MOVIEPY_AVAILABLE:
                raise FileProcessingError("MoviePy is not available. Please install moviepy package.")
            
            if not os.path.exists(input_path):
                raise FileProcessingError(f"Input MP4 file not found: {input_path}")
            
            # Generate output path
            output_path = FileService.get_output_path(input_path, ".mp3")
            
            # Load video
            video = mp.VideoFileClip(input_path)
            
            # Extract audio
            audio = video.audio
            
            if audio is None:
                raise FileProcessingError("No audio track found in the video file")
            
            # Write MP3 file
            audio.write_audiofile(
                output_path,
                bitrate=bitrate,
                logger=None
            )
            
            # Close video and audio to free memory
            audio.close()
            video.close()
            
            return output_path
            
        except Exception as e:
            raise FileProcessingError(f"MP4 to MP3 conversion failed: {str(e)}")
    

    

    

    

    

    

    
    @staticmethod
    def _get_quality_settings(quality: str) -> Dict[str, Any]:
        """Get quality settings based on quality level."""
        quality_presets = {
            "low": {
                "bitrate": "500k",
                "fps": 24,
                "preset": "ultrafast"
            },
            "medium": {
                "bitrate": "1000k",
                "fps": 30,
                "preset": "medium"
            },
            "high": {
                "bitrate": "2000k",
                "fps": 60,
                "preset": "slow"
            },
            "ultra": {
                "bitrate": "4000k",
                "fps": 60,
                "preset": "veryslow"
            }
        }
        
        return quality_presets.get(quality, quality_presets["medium"])
    

    

    
    @staticmethod
    def get_supported_formats() -> Dict[str, List[str]]:
        """Get list of supported input and output formats."""
        return {
            "input_formats": list(VideoConversionService.SUPPORTED_INPUT_FORMATS),
            "output_formats": list(VideoConversionService.SUPPORTED_OUTPUT_FORMATS)
        }
    
    @staticmethod
    def cleanup_temp_files(*file_paths: str) -> None:
        """Clean up temporary files."""
        for file_path in file_paths:
            FileService.cleanup_file(file_path)
