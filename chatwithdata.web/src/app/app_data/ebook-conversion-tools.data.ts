import { ConversionTool } from '../app_models/conversion-tool.model';

export const EBOOK_CONVERSION_TOOLS: ConversionTool[] = [
    {
        id: 'markdown-to-epub',
        title: 'Markdown to EPUB',
        description: 'Convert Markdown files to EPUB format',
        sourceIcon: 'fas fa-file-alt',
        targetIcon: 'fas fa-book',
        route: '/ebookconversion/markdown-to-epub'
    },
    {
        id: 'epub-to-mobi',
        title: 'EPUB to MOBI',
        description: 'Convert EPUB ebook to MOBI format',
        sourceIcon: 'fas fa-book',
        targetIcon: 'fas fa-book',
        route: '/ebookconversion/epub-to-mobi'
    },
    {
        id: 'epub-to-azw',
        title: 'EPUB to AZW',
        description: 'Convert EPUB ebook to AZW format',
        sourceIcon: 'fas fa-book',
        targetIcon: 'fas fa-book',
        route: '/ebookconversion/epub-to-azw'
    },
    {
        id: 'mobi-to-epub',
        title: 'MOBI to EPUB',
        description: 'Convert MOBI ebook to EPUB format',
        sourceIcon: 'fas fa-book',
        targetIcon: 'fas fa-book',
        route: '/ebookconversion/mobi-to-epub'
    },
    {
        id: 'mobi-to-azw',
        title: 'MOBI to AZW',
        description: 'Convert MOBI ebook to AZW format',
        sourceIcon: 'fas fa-book',
        targetIcon: 'fas fa-book',
        route: '/ebookconversion/mobi-to-azw'
    },
    {
        id: 'azw-to-epub',
        title: 'AZW to EPUB',
        description: 'Convert AZW ebook to EPUB format',
        sourceIcon: 'fas fa-book',
        targetIcon: 'fas fa-book',
        route: '/ebookconversion/azw-to-epub'
    },
    {
        id: 'azw-to-mobi',
        title: 'AZW to MOBI',
        description: 'Convert AZW ebook to MOBI format',
        sourceIcon: 'fas fa-book',
        targetIcon: 'fas fa-book',
        route: '/ebookconversion/azw-to-mobi'
    },
    {
        id: 'epub-to-pdf',
        title: 'EPUB to PDF',
        description: 'Convert EPUB ebook to PDF format',
        sourceIcon: 'fas fa-book',
        targetIcon: 'fas fa-file-pdf',
        route: '/ebookconversion/epub-to-pdf'
    },
    {
        id: 'mobi-to-pdf',
        title: 'MOBI to PDF',
        description: 'Convert MOBI ebook to PDF format',
        sourceIcon: 'fas fa-book',
        targetIcon: 'fas fa-file-pdf',
        route: '/ebookconversion/mobi-to-pdf'
    },
    {
        id: 'azw-to-pdf',
        title: 'AZW to PDF',
        description: 'Convert AZW ebook to PDF format',
        sourceIcon: 'fas fa-book',
        targetIcon: 'fas fa-file-pdf',
        route: '/ebookconversion/azw-to-pdf'
    },
    {
        id: 'azw3-to-pdf',
        title: 'AZW3 to PDF',
        description: 'Convert AZW3 ebook to PDF format',
        sourceIcon: 'fas fa-book',
        targetIcon: 'fas fa-file-pdf',
        route: '/ebookconversion/azw3-to-pdf'
    },
    {
        id: 'fb2-to-pdf',
        title: 'FB2 to PDF',
        description: 'Convert FB2 ebook to PDF format',
        sourceIcon: 'fas fa-book',
        targetIcon: 'fas fa-file-pdf',
        route: '/ebookconversion/fb2-to-pdf'
    },
    {
        id: 'fbz-to-pdf',
        title: 'FBZ to PDF',
        description: 'Convert FBZ ebook to PDF format',
        sourceIcon: 'fas fa-book',
        targetIcon: 'fas fa-file-pdf',
        route: '/ebookconversion/fbz-to-pdf'
    },
    {
        id: 'pdf-to-epub',
        title: 'PDF to EPUB',
        description: 'Convert PDF document to EPUB format',
        sourceIcon: 'fas fa-file-pdf',
        targetIcon: 'fas fa-book',
        route: '/ebookconversion/pdf-to-epub'
    },
    {
        id: 'pdf-to-mobi',
        title: 'PDF to MOBI',
        description: 'Convert PDF document to MOBI format',
        sourceIcon: 'fas fa-file-pdf',
        targetIcon: 'fas fa-book',
        route: '/ebookconversion/pdf-to-mobi'
    },
    {
        id: 'pdf-to-azw',
        title: 'PDF to AZW',
        description: 'Convert PDF document to AZW format',
        sourceIcon: 'fas fa-file-pdf',
        targetIcon: 'fas fa-book',
        route: '/ebookconversion/pdf-to-azw'
    },
    {
        id: 'pdf-to-azw3',
        title: 'PDF to AZW3',
        description: 'Convert PDF document to AZW3 format',
        sourceIcon: 'fas fa-file-pdf',
        targetIcon: 'fas fa-book',
        route: '/ebookconversion/pdf-to-azw3'
    },
    {
        id: 'pdf-to-fb2',
        title: 'PDF to FB2',
        description: 'Convert PDF document to FB2 format',
        sourceIcon: 'fas fa-file-pdf',
        targetIcon: 'fas fa-book',
        route: '/ebookconversion/pdf-to-fb2'
    },
    {
        id: 'pdf-to-fbz',
        title: 'PDF to FBZ',
        description: 'Convert PDF document to FBZ format',
        sourceIcon: 'fas fa-file-pdf',
        targetIcon: 'fas fa-book',
        route: '/ebookconversion/pdf-to-fbz'
    }
];
