import { ConversionTool } from '../app_models/conversion-tool.model';

export const MARKDOWN_CONVERSION_TOOLS: ConversionTool[] = [
    {
        id: 'pdf-to-markdown',
        title: 'PDF to Markdown',
        description: 'Convert PDF documents to Markdown format',
        sourceIcon: 'fas fa-file-pdf',
        targetIcon: 'fab fa-markdown',
        route: '/markdownconversion/pdf-to-markdown'
    },
    {
        id: 'markdown-to-pdf',
        title: 'Markdown to PDF',
        description: 'Convert Markdown to professional PDF documents',
        sourceIcon: 'fab fa-markdown',
        targetIcon: 'fas fa-file-pdf',
        route: '/markdownconversion/markdown-to-pdf'
    },
    {
        id: 'markdown-to-html',
        title: 'Markdown to HTML',
        description: 'Convert Markdown to clean HTML code',
        sourceIcon: 'fab fa-markdown',
        targetIcon: 'fas fa-file-code',
        route: '/markdownconversion/markdown-to-html'
    },
    {
        id: 'markdown-to-epub',
        title: 'Markdown to ePUB',
        description: 'Convert Markdown to ePUB eBook format',
        sourceIcon: 'fab fa-markdown',
        targetIcon: 'fas fa-book',
        route: '/markdownconversion/markdown-to-epub'
    },
    {
        id: 'markdown-to-word',
        title: 'Markdown to Word',
        description: 'Convert Markdown to Microsoft Word documents',
        sourceIcon: 'fab fa-markdown',
        targetIcon: 'fas fa-file-word',
        route: '/markdownconversion/markdown-to-word'
    },
    {
        id: 'markdown-to-latex',
        title: 'Markdown to LaTeX',
        description: 'Convert Markdown to LaTeX academic format',
        sourceIcon: 'fab fa-markdown',
        targetIcon: 'fas fa-square-root-alt',
        route: '/markdownconversion/markdown-to-latex'
    },
    {
        id: 'markdown-to-text',
        title: 'Markdown to Text',
        description: 'Extract plain text from Markdown files',
        sourceIcon: 'fab fa-markdown',
        targetIcon: 'fas fa-file-alt',
        route: '/markdownconversion/markdown-to-text'
    },
    {
        id: 'html-to-markdown',
        title: 'HTML to Markdown',
        description: 'Convert HTML code back to Markdown',
        sourceIcon: 'fas fa-file-code',
        targetIcon: 'fab fa-markdown',
        route: '/markdownconversion/html-to-markdown'
    },
    {
        id: 'word-to-markdown',
        title: 'Word to Markdown',
        description: 'Convert Microsoft Word documents to Markdown',
        sourceIcon: 'fas fa-file-word',
        targetIcon: 'fab fa-markdown',
        route: '/markdownconversion/word-to-markdown'
    }
];
