import logging
import os
import shutil
import yt_dlp
from typing import Dict, Any, List, Optional
from youtube_transcript_api import YouTubeTranscriptApi
from app.app_core.config import settings
import re

logger = logging.getLogger(__name__)


class YouTubeService:

    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """Extract video ID from various YouTube URL formats."""
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'youtu\.be\/([0-9A-Za-z_-]{11})',
            r'embed\/([0-9A-Za-z_-]{11})',
            r'shorts\/([0-9A-Za-z_-]{11})'
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    @staticmethod
    def _fetch_all_replies(youtube, parent_id: str, max_replies: int = 50) -> List[Dict]:
        """Fetch all replies for a specific comment thread."""
        replies = []
        try:
            request = youtube.comments().list(
                part="snippet",
                parentId=parent_id,
                maxResults=min(max_replies, 100),
                textFormat="plainText"
            )
            while request and len(replies) < max_replies:
                response = request.execute()
                for item in response.get("items", []):
                    snippet = item["snippet"]
                    replies.append({
                        "author": snippet.get("authorDisplayName"),
                        "text": snippet.get("textDisplay"),
                        "like_count": snippet.get("likeCount", 0),
                        "published_at": snippet.get("publishedAt"),
                    })
                
                next_page = response.get("nextPageToken")
                if next_page and len(replies) < max_replies:
                    request = youtube.comments().list(
                        part="snippet",
                        parentId=parent_id,
                        maxResults=min(max_replies - len(replies), 100),
                        textFormat="plainText",
                        pageToken=next_page
                    )
                else:
                    break
        except Exception as e:
            logger.error(f"Error fetching replies for {parent_id}: {e}")
        return replies

    @staticmethod
    def _fetch_comments_via_api(video_id: str, max_results: int = 50) -> List[Dict]:
        """
        Fetch comments using YouTube Data API v3.
        Includes all replies for each top-level comment.
        """
        api_key = settings.youtube_api_key
        if not api_key or api_key == "your-youtube-data-api-v3-key-here":
            logger.warning("YOUTUBE_API_KEY not set — skipping comment fetch via API.")
            return []

        try:
            from googleapiclient.discovery import build
            youtube = build("youtube", "v3", developerKey=api_key)

            comments = []
            request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=min(max_results, 100),
                order="relevance",
                textFormat="plainText"
            )

            while request and len(comments) < max_results:
                response = request.execute()
                for item in response.get("items", []):
                    # 1. Top-level comment
                    top_snippet = item["snippet"]["topLevelComment"]["snippet"]
                    reply_count = item["snippet"].get("totalReplyCount", 0)
                    
                    comment_obj = {
                        "author": top_snippet.get("authorDisplayName"),
                        "text": top_snippet.get("textDisplay"),
                        "like_count": top_snippet.get("likeCount", 0),
                        "published_at": top_snippet.get("publishedAt"),
                        "reply_count": reply_count,
                        "replies": []
                    }

                    # 2. Fetch ALL replies for this thread if they exist
                    if reply_count > 0:
                        comment_obj["replies"] = YouTubeService._fetch_all_replies(youtube, item["id"])

                    comments.append(comment_obj)

                # Paginate if needed
                next_page = response.get("nextPageToken")
                if next_page and len(comments) < max_results:
                    request = youtube.commentThreads().list(
                        part="snippet",
                        videoId=video_id,
                        maxResults=min(max_results - len(comments), 100),
                        order="relevance",
                        textFormat="plainText",
                        pageToken=next_page
                    )
                else:
                    break

            logger.info(f"Fetched {len(comments)} comment threads (with all replies) via YouTube Data API v3 for {video_id}")
            return comments

        except Exception as e:
            logger.error(f"Error fetching comments via YouTube Data API v3 for {video_id}: {e}")
            return []

    @staticmethod
    def get_video_data(url: str, fetch_comments: bool = True, fetch_transcript: bool = True) -> Dict[str, Any]:
        """Fetch comprehensive data for a YouTube video."""
        video_id = YouTubeService.extract_video_id(url)
        if not video_id:
            raise ValueError("Invalid YouTube URL")

        result = {
            "video_id": video_id,
            "url": url,
            "metadata": {},
            "transcript": None,
            "comments": []
        }

        # ── 1. Metadata via yt-dlp ────────────────────────────────────────────
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'skip_download': True,
            'no_check_certificate': True,
            'ignoreerrors': True,
            'http_headers': {
                'User-Agent': (
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/121.0.0.0 Safari/537.36'
                ),
                'Accept-Language': 'en-US,en;q=0.9',
            }
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                result["metadata"] = {
                    "title": info.get("title"),
                    "description": info.get("description"),
                    "view_count": info.get("view_count"),
                    "like_count": info.get("like_count"),
                    "comment_count": info.get("comment_count"),
                    "channel": info.get("uploader"),
                    "channel_id": info.get("uploader_id"),
                    "channel_url": info.get("uploader_url"),
                    "duration": info.get("duration"),
                    "upload_date": info.get("upload_date"),
                    "categories": info.get("categories"),
                    "tags": info.get("tags"),
                    "thumbnail": info.get("thumbnail"),
                }
        except Exception as e:
            logger.error(f"Error fetching YouTube metadata for {url}: {e}")
            result["metadata_error"] = str(e)

        # ── 2. Comments via YouTube Data API v3 ──────────────────────────────
        if fetch_comments:
            result["comments"] = YouTubeService._fetch_comments_via_api(video_id)

        # ── 3. Transcript via youtube-transcript-api ──────────────────────────
        if fetch_transcript:
            try:
                api = YouTubeTranscriptApi()
                transcript_list_obj = api.list(video_id)

                # Prefer en > ur > hi, else take first available
                try:
                    transcript_obj = transcript_list_obj.find_transcript(['en', 'ur', 'hi'])
                except Exception:
                    transcript_obj = next(iter(transcript_list_obj))

                # fetch() returns a FetchedTranscript — call it only if needed
                if not hasattr(transcript_obj, 'to_raw_data'):
                    transcript_obj = transcript_obj.fetch()

                transcript_data = transcript_obj.to_raw_data()
                full_text = " ".join([t['text'] for t in transcript_data])
                result["transcript"] = {
                    "segments": transcript_data,
                    "full_text": full_text,
                    "language": transcript_obj.language,
                    "language_code": transcript_obj.language_code,
                    "is_generated": transcript_obj.is_generated,
                }
            except Exception as e:
                logger.error(f"Error fetching YouTube transcript for {video_id}: {e}")
                result["transcript_error"] = str(e)

        return result

    @staticmethod
    def download_video(
        url: str,
        output_format: str = "mp4",
        quality: str = "best",
        output_filename: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Download a YouTube video or audio.

        Args:
            url: YouTube video URL
            output_format: 'mp4', 'mkv', 'webm', 'mp3', 'wav', 'm4a'
            quality: 'best', 'worst', '1080p', '720p', '480p', '360p'
            output_filename: Optional custom filename (without extension)

        Returns:
            Dict with 'file_path' and 'filename' on success.
        """
        import imageio_ffmpeg
        ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()

        video_id = YouTubeService.extract_video_id(url)
        if not video_id:
            raise ValueError("Invalid YouTube URL")

        output_dir = settings.output_dir
        os.makedirs(output_dir, exist_ok=True)

        # Build a safe temp base name
        temp_base = f"yt_{video_id}_{os.urandom(4).hex()}"
        temp_template = os.path.join(output_dir, f"{temp_base}.%(ext)s")

        # ── Format string ─────────────────────────────────────
        audio_formats = {"mp3", "wav", "m4a", "aac", "flac", "ogg"}
        is_audio = output_format.lower() in audio_formats

        if is_audio:
            format_string = "bestaudio/best"
        elif quality == "best":
            format_string = "bestvideo+bestaudio/best"
        elif quality == "worst":
            format_string = "worstvideo+worstaudio/worst"
        elif quality.endswith("p"):
            height = quality.replace("p", "")
            format_string = f"bestvideo[height<={height}]+bestaudio/best[height<={height}]"
        else:
            format_string = "bestvideo+bestaudio/best"

        ydl_opts: Dict[str, Any] = {
            "format": format_string,
            "outtmpl": temp_template,
            "quiet": True,
            "no_warnings": True,
            "ffmpeg_location": ffmpeg_path,
            "no_check_certificate": True,
            "http_headers": {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/121.0.0.0 Safari/537.36"
                ),
                "Accept-Language": "en-US,en;q=0.9",
            },
        }

        # ── Post-processors ───────────────────────────────────
        if is_audio:
            codec_map = {
                "mp3": "mp3", "wav": "wav", "m4a": "m4a",
                "aac": "aac", "flac": "flac", "ogg": "vorbis",
            }
            ydl_opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": codec_map.get(output_format.lower(), "mp3"),
                "preferredquality": "192",
            }]
        elif output_format.lower() not in ("mp4", "webm", "mkv"):
            ydl_opts["postprocessors"] = [{
                "key": "FFmpegVideoConvertor",
                "preferedformat": output_format.lower(),
            }]

        # ── Download ──────────────────────────────────────────
        downloaded_file: Optional[str] = None
        video_title = "youtube_video"

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_title = info.get("title", "youtube_video")

        # Find the downloaded file (temp_base prefix)
        for f in os.listdir(output_dir):
            if f.startswith(temp_base):
                downloaded_file = os.path.join(output_dir, f)
                break

        if not downloaded_file or not os.path.exists(downloaded_file):
            raise FileNotFoundError("Downloaded file not found after yt-dlp extraction.")

        # ── Rename to final filename ──────────────────────────
        if output_filename and output_filename.strip():
            safe_name = output_filename.strip()
        else:
            safe_name = "".join(
                c for c in video_title if c.isalnum() or c in (" ", "-", "_")
            ).strip()[:60]
            if not safe_name:
                safe_name = f"youtube_{video_id}"

        ext = os.path.splitext(downloaded_file)[1]   # e.g. ".mp4"
        final_filename = f"{safe_name}{ext}"
        final_path = os.path.join(output_dir, final_filename)

        if os.path.exists(final_path):
            os.remove(final_path)
        shutil.move(downloaded_file, final_path)

        logger.info(f"YouTube video downloaded: {final_filename} ({os.path.getsize(final_path)} bytes)")
        return {
            "file_path": final_path,
            "filename": final_filename,
            "video_title": video_title,
            "format": output_format,
            "quality": quality,
        }
