import { Routes } from '@angular/router';

export const OCRConversionRoutes: Routes = [
    {
        path: '',
        loadComponent: () => import('./ocr-conversion.component').then(c => c.OcrConversionComponent)
    },
    {
        path: 'png-to-text',
        loadComponent: () => import('./png-to-text/png-to-text.component').then(c => c.PngToTextComponent)
    },
    {
        path: 'jpg-to-text',
        loadComponent: () => import('./jpg-to-text/jpg-to-text.component').then(c => c.JpgToTextComponent)
    },
    {
        path: 'png-to-pdf',
        loadComponent: () => import('./png-to-pdf/png-to-pdf.component').then(c => c.PngToPdfComponent)
    },
    {
        path: 'jpg-to-pdf',
        loadComponent: () => import('./jpg-to-pdf/jpg-to-pdf.component').then(c => c.JpgToPdfComponent)
    },
    {
        path: 'pdf-to-text',
        loadComponent: () => import('./pdf-to-text/pdf-to-text.component').then(c => c.PdfToTextComponent)
    },
    {
        path: 'pdf-image-to-pdf-text',
        loadComponent: () => import('./pdf-image-to-pdf-text/pdf-image-to-pdf-text.component').then(c => c.PdfImageToPdfTextComponent)
    }
];
