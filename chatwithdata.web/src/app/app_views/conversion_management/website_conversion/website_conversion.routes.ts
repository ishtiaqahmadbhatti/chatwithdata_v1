import { Routes } from '@angular/router';

export const WebsiteConversionRoutes: Routes = [
    {
        path: '',
        loadComponent: () => import('./website-conversion.component').then(c => c.WebsiteConversionComponent)
    },
    {
        path: 'html-to-pdf',
        loadComponent: () => import('./html-to-pdf/html-to-pdf.component').then(c => c.HtmlToPdfComponent)
    },
    {
        path: 'website-to-pdf',
        loadComponent: () => import('./website-to-pdf/website-to-pdf.component').then(c => c.WebsiteToPdfComponent)
    },
    {
        path: 'word-to-html',
        loadComponent: () => import('./word-to-html/word-to-html.component').then(c => c.WordToHtmlComponent)
    },
    {
        path: 'powerpoint-to-html',
        loadComponent: () => import('./powerpoint-to-html/powerpoint-to-html.component').then(c => c.PowerpointToHtmlComponent)
    },
    {
        path: 'markdown-to-html',
        loadComponent: () => import('./markdown-to-html/markdown-to-html.component').then(c => c.MarkdownToHtmlComponent)
    },
    {
        path: 'website-to-jpg',
        loadComponent: () => import('./website-to-jpg/website-to-jpg.component').then(c => c.WebsiteToJpgComponent)
    },
    {
        path: 'html-to-jpg',
        loadComponent: () => import('./html-to-jpg/html-to-jpg.component').then(c => c.HtmlToJpgComponent)
    },
    {
        path: 'website-to-png',
        loadComponent: () => import('./website-to-png/website-to-png.component').then(c => c.WebsiteToPngComponent)
    },
    {
        path: 'html-to-png',
        loadComponent: () => import('./html-to-png/html-to-png.component').then(c => c.HtmlToPngComponent)
    },
    {
        path: 'html-table-to-csv',
        loadComponent: () => import('./html-table-to-csv/html-table-to-csv.component').then(c => c.HtmlTableToCsvComponent)
    },
    {
        path: 'excel-to-html',
        loadComponent: () => import('./excel-to-html/excel-to-html.component').then(c => c.ExcelToHtmlComponent)
    },
    {
        path: 'pdf-to-html',
        loadComponent: () => import('./pdf-to-html/pdf-to-html.component').then(c => c.PdfToHtmlComponent)
    }
];
