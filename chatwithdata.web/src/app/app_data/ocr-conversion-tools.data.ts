import { ConversionTool } from '../app_models/conversion-tool.model';

export const OCR_CONVERSION_TOOLS: ConversionTool[] = [
    {
        id: 'png-to-text',
        title: 'PNG to Text',
        description: 'Extract text from PNG images using OCR',
        sourceIcon: 'fas fa-file-image',
        targetIcon: 'fas fa-file-alt',
        route: '/ocrconversion/png-to-text'
    },
    {
        id: 'jpg-to-text',
        title: 'JPG to Text',
        description: 'Extract text from JPG images using OCR',
        sourceIcon: 'fas fa-file-image',
        targetIcon: 'fas fa-file-alt',
        route: '/ocrconversion/jpg-to-text'
    },
    {
        id: 'png-to-pdf',
        title: 'PNG to PDF (OCR)',
        description: 'Convert PNG to searchable PDF using OCR',
        sourceIcon: 'fas fa-file-image',
        targetIcon: 'fas fa-file-pdf',
        route: '/ocrconversion/png-to-pdf'
    },
    {
        id: 'jpg-to-pdf',
        title: 'JPG to PDF (OCR)',
        description: 'Convert JPG to searchable PDF using OCR',
        sourceIcon: 'fas fa-file-image',
        targetIcon: 'fas fa-file-pdf',
        route: '/ocrconversion/jpg-to-pdf'
    },
    {
        id: 'pdf-to-text',
        title: 'PDF to Text (OCR)',
        description: 'Extract text from scanned PDF using OCR',
        sourceIcon: 'fas fa-file-pdf',
        targetIcon: 'fas fa-file-alt',
        route: '/ocrconversion/pdf-to-text'
    },
    {
        id: 'pdf-image-to-pdf-text',
        title: 'PDF Image to PDF Text',
        description: 'Convert scanned PDF to searchable PDF',
        sourceIcon: 'fas fa-file-pdf',
        targetIcon: 'fas fa-file-pdf',
        route: '/ocrconversion/pdf-image-to-pdf-text'
    }
];
