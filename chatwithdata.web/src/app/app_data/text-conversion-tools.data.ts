import { ConversionTool } from '../app_models/conversion-tool.model';

export const TEXT_CONVERSION_TOOLS: ConversionTool[] = [
    {
        id: 'word-to-text',
        title: 'Word to Text',
        description: 'Convert Word documents to plain text',
        sourceIcon: 'fas fa-file-word',
        targetIcon: 'fas fa-file-alt',
        route: '/textconversion/word-to-text'
    },
    {
        id: 'powerpoint-to-text',
        title: 'PowerPoint to Text',
        description: 'Convert PowerPoint presentations to plain text',
        sourceIcon: 'fas fa-file-powerpoint',
        targetIcon: 'fas fa-file-alt',
        route: '/textconversion/powerpoint-to-text'
    },
    {
        id: 'pdf-to-text',
        title: 'PDF to Text',
        description: 'Extract text from PDF documents',
        sourceIcon: 'fas fa-file-pdf',
        targetIcon: 'fas fa-file-alt',
        route: '/textconversion/pdf-to-text'
    },
    {
        id: 'srt-to-text',
        title: 'SRT to Text',
        description: 'Convert SRT subtitles to plain text',
        sourceIcon: 'fas fa-closed-captioning',
        targetIcon: 'fas fa-file-alt',
        route: '/textconversion/srt-to-text'
    },
    {
        id: 'vtt-to-text',
        title: 'VTT to Text',
        description: 'Convert VTT subtitles to plain text',
        sourceIcon: 'fas fa-file-code',
        targetIcon: 'fas fa-file-alt',
        route: '/textconversion/vtt-to-text'
    }
];
