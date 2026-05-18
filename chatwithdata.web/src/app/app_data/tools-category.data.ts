import { ToolCategory } from '../app_models/tool-category.model';
import { PDF_CONVERSION_TOOLS } from './pdf-conversion-tools.data';
import { IMAGE_CONVERSION_TOOLS } from './image-conversion-tools.data';
import { AUDIO_CONVERSION_TOOLS } from './audio-conversion-tools.data';
import { VIDEO_CONVERSION_TOOLS } from './video-conversion-tools.data';
import { OFFICE_CONVERSION_TOOLS } from './office-conversion-tools.data';
import { EBOOK_CONVERSION_TOOLS } from './ebook-conversion-tools.data';
import { JSON_CONVERSION_TOOLS } from './json-conversion-tools.data';
import { XML_CONVERSION_TOOLS } from './xml-conversion-tools.data';
import { CSV_CONVERSION_TOOLS } from './csv-conversion-tools.data';
import { TEXT_CONVERSION_TOOLS } from './text-conversion-tools.data';
import { OCR_CONVERSION_TOOLS } from './ocr-conversion-tools.data';
import { WEBSITE_CONVERSION_TOOLS } from './website-conversion-tools.data';
import { SUBTITLE_CONVERSION_TOOLS } from './subtitle-conversion-tools.data';
import { FILE_FORMATTER_TOOLS } from './file-formatter-tools.data';
import { MARKDOWN_CONVERSION_TOOLS } from './markdown-conversion-tools.data';

export const TOOLS_CATEGORIES: ToolCategory[] = [
    {
        id: 'pdf',
        title: 'PDF Conversion Tools',
        description: 'Convert, merge, split, compress, and edit PDF files effortlessly.',
        icon: 'fas fa-file-pdf',
        route: '/pdfconversion',
        count: PDF_CONVERSION_TOOLS.length,
        colorClass: 'text-red-500'
    },
    {
        id: 'image',
        title: 'Image Conversion Tools',
        description: 'Convert between JPG, PNG, WEBP, SVG, and other image formats.',
        icon: 'fas fa-image',
        route: '/imageconversion',
        count: IMAGE_CONVERSION_TOOLS.length,
        colorClass: 'text-purple-500'
    },
    {
        id: 'audio',
        title: 'Audio Conversion Tools',
        description: 'Convert audio files to MP3, WAV, AAC, and more.',
        icon: 'fas fa-music',
        route: '/audioconversion',
        count: AUDIO_CONVERSION_TOOLS.length,
        colorClass: 'text-pink-500'
    },
    {
        id: 'video',
        title: 'Video Conversion Tools',
        description: 'Convert video files to MP4, AVI, MOV, and optimize for web.',
        icon: 'fas fa-video',
        route: '/videoconversion',
        count: VIDEO_CONVERSION_TOOLS.length,
        colorClass: 'text-blue-500'
    },
    {
        id: 'office',
        title: 'Office Conversion Tools',
        description: 'Convert Word, Excel, and PowerPoint documents.',
        icon: 'fas fa-briefcase',
        route: '/officeconversion',
        count: OFFICE_CONVERSION_TOOLS.length,
        colorClass: 'text-orange-500'
    },
    {
        id: 'ebook',
        title: 'E-Book Conversion Tools',
        description: 'Convert EPUB, MOBI, AZW3 for your favorite e-reader.',
        icon: 'fas fa-book-reader',
        route: '/ebookconversion',
        count: EBOOK_CONVERSION_TOOLS.length,
        colorClass: 'text-green-500'
    },
    {
        id: 'json',
        title: 'JSON Conversion Tools',
        description: 'Format, validate, and convert JSON data.',
        icon: 'fas fa-code',
        route: '/jsonconversion',
        count: JSON_CONVERSION_TOOLS.length,
        colorClass: 'text-yellow-500'
    },
    {
        id: 'xml',
        title: 'XML Conversion Tools',
        description: 'Parse, format, and convert XML files.',
        icon: 'fas fa-file-code',
        route: '/xmlconversion',
        count: XML_CONVERSION_TOOLS.length,
        colorClass: 'text-indigo-500'
    },
    {
        id: 'csv',
        title: 'CSV Conversion Tools',
        description: 'Convert CSV to Excel, JSON, and other formats.',
        icon: 'fas fa-table',
        route: '/csvconversion',
        count: CSV_CONVERSION_TOOLS.length,
        colorClass: 'text-teal-500'
    },
    {
        id: 'text',
        title: 'Text Conversion Tools',
        description: 'Manipulate and convert plain text files.',
        icon: 'fas fa-font',
        route: '/textconversion',
        count: TEXT_CONVERSION_TOOLS.length,
        colorClass: 'text-gray-500'
    },
    {
        id: 'ocr',
        title: 'OCR Conversion Tools',
        description: 'Extract text from images and scanned documents.',
        icon: 'fas fa-eye',
        route: '/ocrconversion',
        count: OCR_CONVERSION_TOOLS.length,
        colorClass: 'text-cyan-500'
    },
    {
        id: 'website',
        title: 'Website Conversion Tools',
        description: 'Convert HTML and web pages to PDF or images.',
        icon: 'fas fa-globe',
        route: '/websiteconversion',
        count: WEBSITE_CONVERSION_TOOLS.length,
        colorClass: 'text-blue-400'
    },
    {
        id: 'subtitle',
        title: 'Subtitle Conversion Tools',
        description: 'Convert between SRT, VTT, and other subtitle formats.',
        icon: 'fas fa-closed-captioning',
        route: '/subtitleconversion',
        count: SUBTITLE_CONVERSION_TOOLS.length,
        colorClass: 'text-yellow-600'
    },
    {
        id: 'formatter',
        title: 'File Formatter Tools',
        description: 'Beautify and minify code and data files.',
        icon: 'fas fa-indent',
        route: '/fileformatter',
        count: FILE_FORMATTER_TOOLS.length,
        colorClass: 'text-emerald-500'
    },
    {
        id: 'markdown',
        title: 'Markdown Conversion Tools',
        description: 'Convert between Markdown and PDF, Word, HTML, and more.',
        icon: 'fab fa-markdown',
        route: '/markdownconversion',
        count: MARKDOWN_CONVERSION_TOOLS.length,
        colorClass: 'text-indigo-600'
    },
    {
        id: 'youtube',
        title: 'YouTube Tools',
        description: 'Extract description, comments, metadata, and download videos in high quality.',
        icon: 'fab fa-youtube',
        route: '/youtubetools',
        count: 2,
        colorClass: 'text-red-600'
    },
    {
        id: 'rag',
        title: 'Agentic RAG',
        description: 'Index YouTube videos and talk directly to transcripts with context-aware AI.',
        icon: 'fas fa-brain',
        route: '/ragtools',
        count: 4,
        colorClass: 'text-indigo-500'
    }
];
