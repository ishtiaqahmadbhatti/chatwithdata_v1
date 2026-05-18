import { ConversionTool } from '../app_models/conversion-tool.model';

export const PDF_CONVERSION_TOOLS: ConversionTool[] = [
    // --- CONVERT FROM PDF ---
    {
        id: 'pdf-to-json',
        title: 'PDF to JSON',
        description: 'Convert PDF to JSON format',
        sourceIcon: 'fas fa-file-pdf',
        targetIcon: 'fas fa-file-code',
        route: '/pdfconversion/pdf-to-json'
    },
    {
        id: 'pdf-to-markdown',
        title: 'PDF to Markdown',
        description: 'Convert PDF to Markdown format',
        sourceIcon: 'fas fa-file-pdf',
        targetIcon: 'fas fa-file-alt',
        route: '/pdfconversion/pdf-to-markdown'
    },
    {
        id: 'pdf-to-csv',
        title: 'PDF to CSV',
        description: 'Convert PDF to CSV format',
        sourceIcon: 'fas fa-file-pdf',
        targetIcon: 'fas fa-file-csv',
        route: '/pdfconversion/pdf-to-csv'
    },
    {
        id: 'pdf-to-excel',
        title: 'PDF to Excel',
        description: 'Convert PDF to Excel format',
        sourceIcon: 'fas fa-file-pdf',
        targetIcon: 'fas fa-file-excel',
        route: '/pdfconversion/pdf-to-excel'
    },
    {
        id: 'pdf-to-word',
        title: 'PDF to Word',
        description: 'Convert PDF to Word format',
        sourceIcon: 'fas fa-file-pdf',
        targetIcon: 'fas fa-file-word',
        route: '/pdfconversion/pdf-to-word'
    },
    {
        id: 'pdf-to-jpg',
        title: 'PDF to JPG',
        description: 'Convert PDF to JPG format',
        sourceIcon: 'fas fa-file-pdf',
        targetIcon: 'fas fa-file-image',
        route: '/pdfconversion/pdf-to-jpg'
    },
    {
        id: 'pdf-to-png',
        title: 'PDF to PNG',
        description: 'Convert PDF to PNG format',
        sourceIcon: 'fas fa-file-pdf',
        targetIcon: 'fas fa-file-image',
        route: '/pdfconversion/pdf-to-png'
    },
    {
        id: 'pdf-to-tiff',
        title: 'PDF to TIFF',
        description: 'Convert PDF to TIFF format',
        sourceIcon: 'fas fa-file-pdf',
        targetIcon: 'fas fa-file-image',
        route: '/pdfconversion/pdf-to-tiff'
    },
    {
        id: 'pdf-to-svg',
        title: 'PDF to SVG',
        description: 'Convert PDF to SVG format',
        sourceIcon: 'fas fa-file-pdf',
        targetIcon: 'fas fa-vector-square',
        route: '/pdfconversion/pdf-to-svg'
    },
    {
        id: 'pdf-to-html',
        title: 'PDF to HTML',
        description: 'Convert PDF to HTML format',
        sourceIcon: 'fas fa-file-pdf',
        targetIcon: 'fas fa-file-code',
        route: '/pdfconversion/pdf-to-html'
    },
    {
        id: 'pdf-to-text',
        title: 'PDF to Text',
        description: 'Convert PDF to Text format',
        sourceIcon: 'fas fa-file-pdf',
        targetIcon: 'fas fa-file-alt',
        route: '/pdfconversion/pdf-to-text'
    },

    // --- CONVERT TO PDF ---
    {
        id: 'html-to-pdf',
        title: 'HTML to PDF',
        description: 'Convert HTML to PDF format',
        sourceIcon: 'fas fa-file-code',
        targetIcon: 'fas fa-file-pdf',
        route: '/pdfconversion/html-to-pdf'
    },
    {
        id: 'word-to-pdf',
        title: 'Word to PDF',
        description: 'Convert Word to PDF format',
        sourceIcon: 'fas fa-file-word',
        targetIcon: 'fas fa-file-pdf',
        route: '/pdfconversion/word-to-pdf'
    },
    {
        id: 'powerpoint-to-pdf',
        title: 'PowerPoint to PDF',
        description: 'Convert PowerPoint to PDF format',
        sourceIcon: 'fas fa-file-powerpoint',
        targetIcon: 'fas fa-file-pdf',
        route: '/pdfconversion/powerpoint-to-pdf'
    },
    {
        id: 'oxps-to-pdf',
        title: 'OXPS to PDF',
        description: 'Convert OXPS to PDF format',
        sourceIcon: 'fas fa-file-alt',
        targetIcon: 'fas fa-file-pdf',
        route: '/pdfconversion/oxps-to-pdf'
    },
    {
        id: 'jpg-to-pdf',
        title: 'JPG to PDF',
        description: 'Convert JPG to PDF format',
        sourceIcon: 'fas fa-file-image',
        targetIcon: 'fas fa-file-pdf',
        route: '/pdfconversion/jpg-to-pdf'
    },
    {
        id: 'png-to-pdf',
        title: 'PNG to PDF',
        description: 'Convert PNG to PDF format',
        sourceIcon: 'fas fa-file-image',
        targetIcon: 'fas fa-file-pdf',
        route: '/pdfconversion/png-to-pdf'
    },
    {
        id: 'markdown-to-pdf',
        title: 'Markdown to PDF',
        description: 'Convert Markdown to PDF format',
        sourceIcon: 'fas fa-file-alt',
        targetIcon: 'fas fa-file-pdf',
        route: '/pdfconversion/markdown-to-pdf'
    },
    {
        id: 'excel-to-pdf',
        title: 'Excel to PDF',
        description: 'Convert Excel to PDF format',
        sourceIcon: 'fas fa-file-excel',
        targetIcon: 'fas fa-file-pdf',
        route: '/pdfconversion/excel-to-pdf'
    },
    {
        id: 'ods-to-pdf',
        title: 'ODS to PDF',
        description: 'Convert ODS to PDF format',
        sourceIcon: 'fas fa-file-excel',
        targetIcon: 'fas fa-file-pdf',
        route: '/pdfconversion/ods-to-pdf'
    },

    // --- PDF MANAGEMENT ---
    {
        id: 'merge',
        title: 'Merge PDFs',
        description: 'Merge multiple PDF files',
        sourceIcon: 'fas fa-copy',
        targetIcon: 'fas fa-file-pdf',
        route: '/pdfconversion/merge'
    },
    {
        id: 'split',
        title: 'Split PDF',
        description: 'Split PDF file into pages',
        sourceIcon: 'fas fa-file-pdf',
        targetIcon: 'fas fa-columns',
        route: '/pdfconversion/split'
    },
    {
        id: 'compress',
        title: 'Compress PDF',
        description: 'Compress PDF file size',
        sourceIcon: 'fas fa-file-pdf',
        targetIcon: 'fas fa-compress',
        route: '/pdfconversion/compress'
    },
    {
        id: 'remove-pages',
        title: 'Remove PDF Pages',
        description: 'Remove pages from PDF',
        sourceIcon: 'fas fa-file-pdf',
        targetIcon: 'fas fa-trash',
        route: '/pdfconversion/remove-pages'
    },
    {
        id: 'extract-pages',
        title: 'Extract PDF Pages',
        description: 'Extract specific pages from PDF',
        sourceIcon: 'fas fa-file-pdf',
        targetIcon: 'fas fa-file-export',
        route: '/pdfconversion/extract-pages'
    },
    {
        id: 'rotate',
        title: 'Rotate PDF',
        description: 'Rotate PDF pages',
        sourceIcon: 'fas fa-sync',
        targetIcon: 'fas fa-file-pdf',
        route: '/pdfconversion/rotate'
    },
    {
        id: 'add-watermark',
        title: 'Add PDF Watermark',
        description: 'Add watermark to PDF',
        sourceIcon: 'fas fa-stamp',
        targetIcon: 'fas fa-file-pdf',
        route: '/pdfconversion/add-watermark'
    },
    {
        id: 'add-page-numbers',
        title: 'Add PDF Page Numbers',
        description: 'Add page numbers to PDF',
        sourceIcon: 'fas fa-list-ol',
        targetIcon: 'fas fa-file-pdf',
        route: '/pdfconversion/add-page-numbers'
    },
    {
        id: 'crop',
        title: 'Crop PDF',
        description: 'Crop PDF pages',
        sourceIcon: 'fas fa-crop',
        targetIcon: 'fas fa-file-pdf',
        route: '/pdfconversion/crop'
    },
    {
        id: 'protect',
        title: 'Protect PDF',
        description: 'Password protect PDF file',
        sourceIcon: 'fas fa-lock',
        targetIcon: 'fas fa-file-pdf',
        route: '/pdfconversion/protect'
    },
    {
        id: 'unlock',
        title: 'Unlock PDF',
        description: 'Remove password from PDF',
        sourceIcon: 'fas fa-unlock',
        targetIcon: 'fas fa-file-pdf',
        route: '/pdfconversion/unlock'
    },
    {
        id: 'repair',
        title: 'Repair PDF',
        description: 'Repair damaged PDF file',
        sourceIcon: 'fas fa-tools',
        targetIcon: 'fas fa-file-pdf',
        route: '/pdfconversion/repair'
    },
    {
        id: 'compare',
        title: 'Compare PDFs',
        description: 'Compare two PDF files',
        sourceIcon: 'fas fa-not-equal',
        targetIcon: 'fas fa-file-pdf',
        route: '/pdfconversion/compare'
    },
    {
        id: 'metadata',
        title: 'PDF Metadata',
        description: 'View and edit PDF metadata',
        sourceIcon: 'fas fa-info-circle',
        targetIcon: 'fas fa-file-pdf',
        route: '/pdfconversion/metadata'
    }
];