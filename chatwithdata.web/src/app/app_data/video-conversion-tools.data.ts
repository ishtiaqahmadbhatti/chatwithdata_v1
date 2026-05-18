import { ConversionTool } from '../app_models/conversion-tool.model';

export const VIDEO_CONVERSION_TOOLS: ConversionTool[] = [
    {
        id: 'mov-to-mp4',
        title: 'MOV to MP4',
        description: 'Convert MOV video files to MP4 format',
        sourceIcon: 'fas fa-video',
        targetIcon: 'fas fa-video',
        route: '/videoconversion/mov-to-mp4'
    },
    {
        id: 'mkv-to-mp4',
        title: 'MKV to MP4',
        description: 'Convert MKV video files to MP4 format',
        sourceIcon: 'fas fa-video',
        targetIcon: 'fas fa-video',
        route: '/videoconversion/mkv-to-mp4'
    },
    {
        id: 'avi-to-mp4',
        title: 'AVI to MP4',
        description: 'Convert AVI video files to MP4 format',
        sourceIcon: 'fas fa-video',
        targetIcon: 'fas fa-video',
        route: '/videoconversion/avi-to-mp4'
    },
    {
        id: 'mp4-to-mp3',
        title: 'MP4 to MP3',
        description: 'Extract audio from MP4 video to MP3',
        sourceIcon: 'fas fa-video',
        targetIcon: 'fas fa-music',
        route: '/videoconversion/mp4-to-mp3'
    },

];
