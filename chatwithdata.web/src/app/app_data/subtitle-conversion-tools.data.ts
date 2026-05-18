import { ConversionTool } from '../app_models/conversion-tool.model';

export const SUBTITLE_CONVERSION_TOOLS: ConversionTool[] = [
    {
        id: 'translate-srt',
        title: 'Translate SRT',
        description: 'Translate SRT subtitles to another language',
        sourceIcon: 'fas fa-closed-captioning',
        targetIcon: 'fas fa-language',
        route: '/subtitleconversion/translate-srt'
    },
    {
        id: 'srt-to-csv',
        title: 'SRT to CSV',
        description: 'Convert SRT subtitles to CSV format',
        sourceIcon: 'fas fa-closed-captioning',
        targetIcon: 'fas fa-file-csv',
        route: '/subtitleconversion/srt-to-csv'
    },
    {
        id: 'srt-to-excel',
        title: 'SRT to Excel',
        description: 'Convert SRT subtitles to Excel format',
        sourceIcon: 'fas fa-closed-captioning',
        targetIcon: 'fas fa-file-excel',
        route: '/subtitleconversion/srt-to-excel'
    },
    {
        id: 'srt-to-text',
        title: 'SRT to Text',
        description: 'Convert SRT subtitles to plain text',
        sourceIcon: 'fas fa-closed-captioning',
        targetIcon: 'fas fa-file-alt',
        route: '/subtitleconversion/srt-to-text'
    },
    {
        id: 'srt-to-vtt',
        title: 'SRT to VTT',
        description: 'Convert SRT subtitles to VTT format',
        sourceIcon: 'fas fa-closed-captioning',
        targetIcon: 'fas fa-file-code',
        route: '/subtitleconversion/srt-to-vtt'
    },
    {
        id: 'vtt-to-text',
        title: 'VTT to Text',
        description: 'Convert VTT subtitles to plain text',
        sourceIcon: 'fas fa-file-code',
        targetIcon: 'fas fa-file-alt',
        route: '/subtitleconversion/vtt-to-text'
    },
    {
        id: 'vtt-to-srt',
        title: 'VTT to SRT',
        description: 'Convert VTT subtitles to SRT format',
        sourceIcon: 'fas fa-file-code',
        targetIcon: 'fas fa-closed-captioning',
        route: '/subtitleconversion/vtt-to-srt'
    },
    {
        id: 'csv-to-srt',
        title: 'CSV to SRT',
        description: 'Convert CSV to SRT subtitles',
        sourceIcon: 'fas fa-file-csv',
        targetIcon: 'fas fa-closed-captioning',
        route: '/subtitleconversion/csv-to-srt'
    },
    {
        id: 'excel-to-srt',
        title: 'Excel to SRT',
        description: 'Convert Excel to SRT subtitles',
        sourceIcon: 'fas fa-file-excel',
        targetIcon: 'fas fa-closed-captioning',
        route: '/subtitleconversion/excel-to-srt'
    }
];
