from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class ExtractDataRequest(BaseModel):
    url: str = Field(
        ..., 
        description="The YouTube video URL to extract data from"
    )
    fetch_comments: bool = Field(
        True, 
        description="Whether to extract video comments from YouTube"
    )
    fetch_transcript: bool = Field(
        True, 
        description="Whether to extract the video transcript/subtitles"
    )


class ExtractDataResponse(BaseModel):
    success: bool = Field(
        ..., 
        description="Indicates whether the data extraction was successful"
    )
    message: str = Field(
        ..., 
        description="A friendly status message detailing the operation result"
    )
    data: Dict[str, Any] = Field(
        ..., 
        description="The dictionary containing metadata, transcript text, and comments list"
    )


class DownloadVideoRequest(BaseModel):
    url: str = Field(
        ..., 
        description="The YouTube video URL to download"
    )
    output_format: str = Field(
        "mp4", 
        description="Output format (mp4 | mkv | webm | mp3 | wav | m4a | aac | flac)"
    )
    quality: str = Field(
        "best", 
        description="Quality preset to download (best | worst | 1080p | 720p | 480p | 360p)"
    )
    output_filename: Optional[str] = Field(
        None, 
        description="Optional custom name for the downloaded file (without extension)"
    )


class DownloadVideoResponse(BaseModel):
    success: bool = Field(
        ..., 
        description="Indicates whether the download request was successful"
    )
    message: str = Field(
        ..., 
        description="A friendly status message detailing the download result"
    )
    video_title: str = Field(
        ..., 
        description="The original title of the downloaded YouTube video"
    )
    output_filename: str = Field(
        ..., 
        description="The actual name of the generated file stored on disk"
    )
    format: str = Field(
        ..., 
        description="The format of the downloaded file (e.g. mp4, mp3)"
    )
    quality: str = Field(
        ..., 
        description="The quality of the downloaded file (e.g. best, 1080p)"
    )
    download_url: str = Field(
        ..., 
        description="The API path to retrieve the binary file stream"
    )
