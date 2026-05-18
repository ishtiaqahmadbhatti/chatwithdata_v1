import { ConversionTool } from '../app_models/conversion-tool.model';

export const AUDIO_CONVERSION_TOOLS: ConversionTool[] = [
    {
        id: 'mp4-to-mp3',
        title: 'MP4 to MP3',
        description: 'Convert MP4 files to MP3 format',
        sourceIcon: 'fas fa-video',
        targetIcon: 'fas fa-music',
        route: '/audioconversion/mp4-to-mp3'
    },
    {
        id: 'wav-to-mp3',
        title: 'WAV to MP3',
        description: 'Convert WAV audio files to MP3 format',
        sourceIcon: 'fas fa-music',
        targetIcon: 'fas fa-music',
        route: '/audioconversion/wav-to-mp3'
    },
    {
        id: 'flac-to-mp3',
        title: 'FLAC to MP3',
        description: 'Convert FLAC audio files to MP3 format',
        sourceIcon: 'fas fa-music',
        targetIcon: 'fas fa-music',
        route: '/audioconversion/flac-to-mp3'
    },
    {
        id: 'mp3-to-wav',
        title: 'MP3 to WAV',
        description: 'Convert MP3 audio files to WAV format',
        sourceIcon: 'fas fa-music',
        targetIcon: 'fas fa-music',
        route: '/audioconversion/mp3-to-wav'
    },
    {
        id: 'flac-to-wav',
        title: 'FLAC to WAV',
        description: 'Convert FLAC audio files to WAV format',
        sourceIcon: 'fas fa-music',
        targetIcon: 'fas fa-music',
        route: '/audioconversion/flac-to-wav'
    },
    {
        id: 'wav-to-flac',
        title: 'WAV to FLAC',
        description: 'Convert WAV audio files to FLAC format',
        sourceIcon: 'fas fa-music',
        targetIcon: 'fas fa-music',
        route: '/audioconversion/wav-to-flac'
    },


    {
        id: 'trim-audio',
        title: 'Trim Audio',
        description: 'Trim or cut audio files',
        sourceIcon: 'fas fa-music',
        targetIcon: 'fas fa-cut',
        route: '/audioconversion/trim-audio'
    },
    {
        id: 'audio-to-text',
        title: 'Audio to Text',
        description: 'Convert speech from audio files to text',
        sourceIcon: 'fas fa-microphone',
        targetIcon: 'fas fa-file-alt',
        route: '/audioconversion/audio-to-text'
    },

];
