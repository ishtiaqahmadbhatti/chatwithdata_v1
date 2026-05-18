import { ConversionTool } from '../app_models/conversion-tool.model';

export const WEBSITE_CONVERSION_TOOLS: ConversionTool[] = [
    {
        id: 'html-to-pdf',
        title: 'HTML to PDF',
        description: 'Convert HTML content to PDF format',
        sourceIcon: 'fas fa-file-code',
        targetIcon: 'fas fa-file-pdf',
        route: '/websiteconversion/html-to-pdf'
    },
    {
        id: 'website-to-pdf',
        title: 'Website to PDF',
        description: 'Convert website URLs to PDF format',
        sourceIcon: 'fas fa-globe',
        targetIcon: 'fas fa-file-pdf',
        route: '/websiteconversion/website-to-pdf'
    },
    {
        id: 'word-to-html',
        title: 'Word to HTML',
        description: 'Convert Word documents to HTML',
        sourceIcon: 'fas fa-file-word',
        targetIcon: 'fas fa-file-code',
        route: '/websiteconversion/word-to-html'
    },
    {
        id: 'powerpoint-to-html',
        title: 'PowerPoint to HTML',
        description: 'Convert PowerPoint presentations to HTML',
        sourceIcon: 'fas fa-file-powerpoint',
        targetIcon: 'fas fa-file-code',
        route: '/websiteconversion/powerpoint-to-html'
    },
    {
        id: 'markdown-to-html',
        title: 'Markdown to HTML',
        description: 'Convert Markdown files to HTML',
        sourceIcon: 'fas fa-file-alt',
        targetIcon: 'fas fa-file-code',
        route: '/websiteconversion/markdown-to-html'
    },
    {
        id: 'website-to-jpg',
        title: 'Website to JPG',
        description: 'Convert website URLs to JPG image',
        sourceIcon: 'fas fa-globe',
        targetIcon: 'fas fa-file-image',
        route: '/websiteconversion/website-to-jpg'
    },
    {
        id: 'html-to-jpg',
        title: 'HTML to JPG',
        description: 'Convert HTML content to JPG image',
        sourceIcon: 'fas fa-file-code',
        targetIcon: 'fas fa-file-image',
        route: '/websiteconversion/html-to-jpg'
    },
    {
        id: 'website-to-png',
        title: 'Website to PNG',
        description: 'Convert website URLs to PNG image',
        sourceIcon: 'fas fa-globe',
        targetIcon: 'fas fa-file-image',
        route: '/websiteconversion/website-to-png'
    },
    {
        id: 'html-to-png',
        title: 'HTML to PNG',
        description: 'Convert HTML content to PNG image',
        sourceIcon: 'fas fa-file-code',
        targetIcon: 'fas fa-file-image',
        route: '/websiteconversion/html-to-png'
    },
    {
        id: 'html-table-to-csv',
        title: 'HTML Table to CSV',
        description: 'Extract HTML tables to CSV format',
        sourceIcon: 'fas fa-table',
        targetIcon: 'fas fa-file-csv',
        route: '/websiteconversion/html-table-to-csv'
    },
    {
        id: 'excel-to-html',
        title: 'Excel to HTML',
        description: 'Convert Excel spreadsheets to HTML',
        sourceIcon: 'fas fa-file-excel',
        targetIcon: 'fas fa-file-code',
        route: '/websiteconversion/excel-to-html'
    },
    {
        id: 'pdf-to-html',
        title: 'PDF to HTML',
        description: 'Convert PDF documents to HTML format',
        sourceIcon: 'fas fa-file-pdf',
        targetIcon: 'fas fa-file-code',
        route: '/websiteconversion/pdf-to-html'
    }
];
