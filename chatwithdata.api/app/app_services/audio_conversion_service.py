import os
import tempfile
from typing import Optional, Dict, Any, List, Tuple
from pydub import AudioSegment
from pydub.utils import which
import soundfile as sf
import numpy as np
from app.app_core.exceptions import FileProcessingError
from app.app_services.file_service import FileService

# Configure ffmpeg path
ffmpeg_path = None
try:
    import imageio_ffmpeg
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    print(f"AudioConversionService: configured ffmpeg from imageio-ffmpeg at {ffmpeg_path}")
    
    # Configure pydub to use this ffmpeg
    if ffmpeg_path:
        AudioSegment.converter = ffmpeg_path
        
except ImportError:
    print("AudioConversionService: imageio-ffmpeg not found. Will rely on system PATH.")

# Helper to run ffmpeg command
import subprocess
def run_ffmpeg(args):
    """Run ffmpeg command with error handling."""
    exe = ffmpeg_path if ffmpeg_path else "ffmpeg"
    cmd = [exe] + args
    try:
        # Check if executable exists or is in path
        if not ffmpeg_path and not which("ffmpeg"):
             raise FileProcessingError("FFmpeg executable not found. Please install ffmpeg or imageio-ffmpeg.")
             
        process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if process.returncode != 0:
            raise FileProcessingError(f"FFmpeg command failed: {process.stderr}")
    except FileNotFoundError:
         raise FileProcessingError("FFmpeg executable not found (FileNotFound).")
    except Exception as e:
         raise FileProcessingError(f"FFmpeg execution error: {str(e)}")

class AudioConversionService:
    """Service for handling audio conversions between various formats."""
    
    # Supported input formats
    SUPPORTED_INPUT_FORMATS = {
        'MP4', 'WAV', 'FLAC', 'MP3', 'AAC', 'OGG', 'M4A', 'WMA', 'AIFF', 'AU'
    }
    
    # Supported output formats
    SUPPORTED_OUTPUT_FORMATS = {
        'MP3', 'WAV', 'FLAC', 'AAC', 'OGG', 'M4A', 'WMA', 'AIFF', 'AU'
    }
    
    @staticmethod
    def mp4_to_mp3(input_path: str, bitrate: str = "192k", quality: str = "medium") -> str:
        """
        Convert MP4 file to MP3 format.
        
        Note: This method delegates to VideoConversionService.mp4_to_mp3() to avoid
        code duplication (DRY principle), as extracting audio from video files is
        better handled by MoviePy library.
        """
        try:
            # Import here to avoid circular dependency
            from app.app_services.video_conversion_service import VideoConversionService
            
            # Delegate to VideoConversionService which uses MoviePy (better for video files)
            # quality parameter is ignored here as VideoConversionService doesn't use it
            return VideoConversionService.mp4_to_mp3(input_path, bitrate)
            
        except Exception as e:
            raise FileProcessingError(f"MP4 to MP3 conversion failed: {str(e)}")
    
    @staticmethod
    def wav_to_mp3(input_path: str, bitrate: str = "192k", quality: str = "medium") -> str:
        """Convert WAV file to MP3 format."""
        try:
            if not os.path.exists(input_path):
                raise FileProcessingError(f"Input WAV file not found: {input_path}")
            
            # Generate output path
            output_path = FileService.get_output_path(input_path, ".mp3")
            
            # Map quality/bitrate to ffmpeg args
            # ffmpeg -i input.wav -b:a 192k output.mp3
            args = [
                '-y',
                '-i', input_path,
                '-b:a', bitrate,
                output_path
            ]
            run_ffmpeg(args)
            
            return output_path
            
        except Exception as e:
            raise FileProcessingError(f"WAV to MP3 conversion failed: {str(e)}")
    
    @staticmethod
    def flac_to_mp3(input_path: str, bitrate: str = "192k", quality: str = "medium") -> str:
        """Convert FLAC file to MP3 format."""
        try:
            if not os.path.exists(input_path):
                raise FileProcessingError(f"Input FLAC file not found: {input_path}")
            
            # Generate output path
            output_path = FileService.get_output_path(input_path, ".mp3")
            
            # ffmpeg -i input.flac -b:a 192k output.mp3
            args = [
                '-y',
                '-i', input_path,
                '-b:a', bitrate,
                output_path
            ]
            run_ffmpeg(args)
            
            return output_path
            
        except Exception as e:
            raise FileProcessingError(f"FLAC to MP3 conversion failed: {str(e)}")
    
    @staticmethod
    def mp3_to_wav(input_path: str, sample_rate: int = 44100, channels: int = 2) -> str:
        """Convert MP3 file to WAV format."""
        try:
            if not os.path.exists(input_path):
                raise FileProcessingError(f"Input MP3 file not found: {input_path}")
            
            # Generate output path
            output_path = FileService.get_output_path(input_path, ".wav")
            
            # Use subprocess to call ffmpeg directly
            # ffmpeg -i input.mp3 -ar 44100 -ac 2 output.wav
            args = [
                '-y', # Overwrite output
                '-i', input_path,
                '-ar', str(sample_rate),
                '-ac', str(channels),
                output_path
            ]
            
            run_ffmpeg(args)
            
            return output_path
            
        except Exception as e:
            raise FileProcessingError(f"MP3 to WAV conversion failed: {str(e)}")
    
    @staticmethod
    def flac_to_wav(input_path: str, sample_rate: int = 44100, channels: int = 2) -> str:
        """Convert FLAC file to WAV format."""
        try:
            if not os.path.exists(input_path):
                raise FileProcessingError(f"Input FLAC file not found: {input_path}")
            
            # Generate output path
            output_path = FileService.get_output_path(input_path, ".wav")
            
            # Use subprocess to call ffmpeg directly
            args = [
                '-y',
                '-i', input_path,
                '-ar', str(sample_rate),
                '-ac', str(channels),
                output_path
            ]
            run_ffmpeg(args)
            
            return output_path
            
        except Exception as e:
            raise FileProcessingError(f"FLAC to WAV conversion failed: {str(e)}")
    
    @staticmethod
    def wav_to_flac(input_path: str, compression_level: int = 5) -> str:
        """Convert WAV file to FLAC format."""
        try:
            if not os.path.exists(input_path):
                raise FileProcessingError(f"Input WAV file not found: {input_path}")
            
            # Generate output path
            output_path = FileService.get_output_path(input_path, ".flac")
            
            # ffmpeg -i input.wav -compression_level 5 output.flac
            args = [
                '-y',
                '-i', input_path,
                '-compression_level', str(compression_level),
                output_path
            ]
            run_ffmpeg(args)
            
            return output_path
            
        except Exception as e:
            raise FileProcessingError(f"WAV to FLAC conversion failed: {str(e)}")
    
    @staticmethod
    def _parse_time_str(time_str: str) -> float:
        """Parse time string (HH:MM:SS, MM:SS, or seconds) to seconds."""
        try:
            parts = list(map(float, str(time_str).split(':')))
            if len(parts) == 1:
                return parts[0]
            elif len(parts) == 2:
                return parts[0] * 60 + parts[1]
            elif len(parts) == 3:
                return parts[0] * 3600 + parts[1] * 60 + parts[2]
            else:
                raise ValueError("Invalid time format")
        except Exception:
             # Try simple float conversion if it's just a number string
             try:
                 return float(time_str)
             except:
                 raise FileProcessingError(f"Invalid time format: {time_str}")

    @staticmethod
    def get_audio_duration(input_path: str) -> float:
        """Get total duration of audio file in seconds."""
        try:
            # Try parsing ffmpeg -i output for Duration
            exe = ffmpeg_path if ffmpeg_path else "ffmpeg"
            cmd = [exe, '-i', input_path]
            # ffmpeg returns non-zero when no output file specified, so we ignore return code
            process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Look for Duration: HH:MM:SS.mm in stderr
            import re
            output = process.stderr
            match = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", output)
            if match:
                hours = float(match.group(1))
                minutes = float(match.group(2))
                seconds = float(match.group(3))
                duration = hours * 3600 + minutes * 60 + seconds
                return duration
        except Exception:
            pass
            
        # Fallback to pydub mediainfo if available (requires ffprobe)
        try:
            from pydub.utils import mediainfo
            info = mediainfo(input_path)
            if info and 'duration' in info:
                return float(info['duration'])
        except Exception:
            pass

        # If everything fails, return -1 (cannot validate duration)
        return -1.0

    @staticmethod
    def trim_audio(input_path: str, segments: List[Dict[str, str]]) -> str:
        """Trim audio to specified segment(s) and merge them if multiple."""
        temp_files = []
        try:
            if not os.path.exists(input_path):
                raise FileProcessingError(f"Input audio file not found: {input_path}")
            
            if not segments:
                raise FileProcessingError("No time segments provided")
            
            # Get total duration for validation
            total_duration = AudioConversionService.get_audio_duration(input_path)
            
            for i, segment in enumerate(segments):
                start_str = str(segment.get("start", "0"))
                end_str = str(segment.get("end", "0"))
                
                start_time = AudioConversionService._parse_time_str(start_str)
                end_time = AudioConversionService._parse_time_str(end_str)
                
                if start_time < 0 or end_time < 0:
                    raise FileProcessingError(f"Negative time values not allowed: {start_str}-{end_str}")

                if end_time <= start_time:
                    # Skip invalid segments where end <= start
                    continue 

                # Validate against total duration if available
                if total_duration > 0:
                    if start_time >= total_duration:
                        raise FileProcessingError(f"Start time {start_str} is beyond audio duration ({total_duration:.2f}s)")
                    if end_time > total_duration:
                        # Clamp end time to duration? Or raise error?
                        # User said "os say agae ki range na dain" -> don't allow range beyond.
                        # I'll raise error to be strict as "range na dain" implies invalid input.
                        raise FileProcessingError(f"End time {end_str} exceeds audio duration ({total_duration:.2f}s)")

                # Generate unique temp output for this segment
                segment_output = FileService.get_output_path(input_path, f"_segment_{i}.wav")
                temp_files.append(segment_output)
                
                # ffmpeg -y -i input -ss start -to end output.wav
                args = [
                    '-y',
                    '-i', input_path,
                    '-ss', str(start_time),
                    '-to', str(end_time),
                    segment_output
                ]
                run_ffmpeg(args)

            if not temp_files:
                raise FileProcessingError("No valid segments created")
            
            # Use WAV for precise merging logic
            if len(temp_files) == 1:
                merged_wav_path = temp_files[0]
            else:
                merged_wav_path = FileService.get_output_path(input_path, "_trimmed_merged_intermediate.wav")
                AudioConversionService.merge_audio_files(temp_files, merged_wav_path)
                # Cleanup segment files
                FileService.cleanup_files(*temp_files)
            
            # Convert final WAV back to original format
            _, input_ext = os.path.splitext(input_path)
            target_ext = input_ext.lower()
            
            if target_ext == '.wav':
                return merged_wav_path
            else:
                final_output = FileService.get_output_path(input_path, f"_trimmed{target_ext}")
                # Convert WAV to Target Format
                args = ['-y', '-i', merged_wav_path, final_output]
                run_ffmpeg(args)
                
                # Cleanup intermediate WAV
                FileService.cleanup_file(merged_wav_path)
                
                return final_output

        except Exception as e:
            # Cleanup all temps on error
            FileService.cleanup_files(*temp_files)
            if 'merged_wav_path' in locals():
                FileService.cleanup_file(merged_wav_path)
            raise FileProcessingError(f"Audio trimming failed: {str(e)}")
    
    @staticmethod
    def merge_audio_files(input_paths: List[str], output_path: str) -> str:
        """Merge multiple audio files into one using ffmpeg concat demuxer."""
        try:
            if not input_paths:
                raise FileProcessingError("No input files provided")
            
            # Create a temporary file list for ffmpeg
            # file 'path1'
            # file 'path2'
            list_path = os.path.join(os.path.dirname(output_path), "concat_list.txt")
            try:
                with open(list_path, 'w', encoding='utf-8') as f:
                    for path in input_paths:
                        # Use absolute paths with forward slashes to avoid relative path issues in ffmpeg
                        abs_path = os.path.abspath(path).replace('\\', '/')
                        # Escape single quotes
                        safe_path = abs_path.replace("'", "'\\''") 
                        f.write(f"file '{safe_path}'\n")
                
                # ffmpeg -f concat -safe 0 -i list.txt -c copy output.wav
                # Re-encoding is safer if formats differ, but copy is faster
                # Let's re-encode to be safe and consistent with previous pydub behavior (which re-encodes)
                args = [
                    '-y',
                    '-f', 'concat',
                    '-safe', '0',
                    '-i', list_path,
                    '-c:a', 'pcm_s16le', # Force generic WAV encoding
                    output_path
                ]
                run_ffmpeg(args)
                
                return output_path
            finally:
                if os.path.exists(list_path):
                    os.remove(list_path)
            
        except Exception as e:
            raise FileProcessingError(f"Audio merging failed: {str(e)}")
    
    @staticmethod
    def split_audio(input_path: str, segment_duration: float) -> List[str]:
        """Split audio into segments of specified duration."""
        try:
            if not os.path.exists(input_path):
                raise FileProcessingError(f"Input audio file not found: {input_path}")
            
            # Use ffmpeg segment muxer
            # ffmpeg -i input.wav -f segment -segment_time 30 -c copy output_%03d.wav
            output_pattern = FileService.get_output_path(input_path, "_segment_%03d.wav")
            # We need to return the list of created files.
            # It's hard to predict exactly what filenames ffmpeg will create without listing dir.
            # But the pattern is predictable.
            
            args = [
                '-y',
                '-i', input_path,
                '-f', 'segment',
                '-segment_time', str(segment_duration),
                '-c', 'copy', # Copy codec for speed if possible
                '-reset_timestamps', '1',
                output_pattern
            ]
            run_ffmpeg(args)
            
            # Collect generated files
            output_dir = os.path.dirname(output_pattern)
            base_name_pattern = os.path.basename(output_pattern).replace("%03d", r"\d{3}")
            generated_files = []
            
            import re
            for f in os.listdir(output_dir):
                if re.match(base_name_pattern, f):
                    generated_files.append(os.path.join(output_dir, f))
            
            return sorted(generated_files)
            
        except Exception as e:
            raise FileProcessingError(f"Audio splitting failed: {str(e)}")
    
    @staticmethod
    def audio_to_text(input_path: str, language: str = "en-US") -> Dict[str, Any]:
        """
        Convert audio file to text using speech recognition with chunking.
        Handles large files by splitting them into smaller chunks.
        """
        try:
            import speech_recognition as sr
            from pydub import AudioSegment
            from pydub.silence import split_on_silence
            
            if not os.path.exists(input_path):
                raise FileProcessingError(f"Input audio file not found: {input_path}")
            
            # Initialize recognizer
            recognizer = sr.Recognizer()
            extracted_text = []
            
            # Convert/Load audio to proper format for processing
            # We use pydub to handle loading and splitting
            try:
                # Load audio file
                sound = AudioSegment.from_file(input_path)
            except Exception as e:
                # If pydub fails loading directly (e.g. missing codec), try converting to WAV first
                wav_path = FileService.get_output_path(input_path, "_temp_load.wav")
                # Standardize to 16k mono for consistency and compatibility
                args = ['-y', '-i', input_path, '-ar', '16000', '-ac', '1', wav_path]
                run_ffmpeg(args)
                sound = AudioSegment.from_file(wav_path)
                if os.path.exists(wav_path):
                    os.remove(wav_path)
            
            # Normalize audio (optional but helps)
            sound = sound.set_frame_rate(16000).set_channels(1)
            
            # Helper to recognize a chunk
            def recognize_chunk(chunk_path):
                try:
                    with sr.AudioFile(chunk_path) as source:
                        # recognizer.adjust_for_ambient_noise(source, duration=0.5) 
                        audio_data = recognizer.record(source)
                        return recognizer.recognize_google(audio_data, language=language)
                except sr.UnknownValueError:
                    return ""
                except sr.RequestError as e:
                    print(f"Request error for chunk {chunk_path}: {e}")
                    return ""
                except Exception as e:
                    print(f"Error processing chunk {chunk_path}: {e}")
                    return ""

            # Check duration. If short (< 1 min), try direct conversion
            if len(sound) < 60000:
                temp_chunk = FileService.get_output_path(input_path, "_temp_short.wav")
                sound.export(temp_chunk, format="wav")
                try:
                    text = recognize_chunk(temp_chunk)
                    if text:
                        extracted_text.append(text)
                finally:
                    if os.path.exists(temp_chunk):
                        os.remove(temp_chunk)
            else:
                # Split audio into chunks
                # Strategy: Split by silence first. If chunks are too long, split by time.
                # However, split_on_silence is slow on large files.
                # Faster strategy: Split by fixed time intervals (e.g. 30s) with overlap
                
                CHUNK_LENGTH_MS = 30000  # 30 seconds
                
                # Simple time-based chunking for reliability and speed
                chunks = []
                for i in range(0, len(sound), CHUNK_LENGTH_MS):
                    chunks.append(sound[i:i + CHUNK_LENGTH_MS])
                
                for i, chunk in enumerate(chunks):
                    chunk_filename = FileService.get_output_path(input_path, f"_chunk_{i}.wav")
                    chunk.export(chunk_filename, format="wav")
                    
                    try:
                        text = recognize_chunk(chunk_filename)
                        if text:
                            extracted_text.append(text)
                    finally:
                        if os.path.exists(chunk_filename):
                            os.remove(chunk_filename)
            
            final_text = " ".join(extracted_text)
            
            # If empty, it might be due to error or silence. 
            # If we really got nothing and threw no major exceptions, return empty result.
            
            return {
                "text": final_text,
                "language": language,
                "confidence": "medium", 
                "word_count": len(final_text.split()),
                "character_count": len(final_text)
            }
                
        except ImportError:
            raise FileProcessingError("speech_recognition or pydub library is not installed.")
        except Exception as e:
            # Re-raise processing errors or wrap generic exceptions
            if isinstance(e, FileProcessingError):
                 raise e
            raise FileProcessingError(f"Audio to text conversion failed: {str(e)}")
    
    @staticmethod
    def _get_quality_settings(quality: str) -> Dict[str, Any]:
        """Get quality settings based on quality level."""
        quality_presets = {
            "low": {
                "parameters": ["-q:a", "9"]
            },
            "medium": {
                "parameters": ["-q:a", "5"]
            },
            "high": {
                "parameters": ["-q:a", "2"]
            },
            "ultra": {
                "parameters": ["-q:a", "0"]
            }
        }
        
        return quality_presets.get(quality, quality_presets["medium"])
        
    @staticmethod
    def cleanup_temp_files(*file_paths: str) -> None:
        """Clean up temporary files."""
        for file_path in file_paths:
            FileService.cleanup_file(file_path)
