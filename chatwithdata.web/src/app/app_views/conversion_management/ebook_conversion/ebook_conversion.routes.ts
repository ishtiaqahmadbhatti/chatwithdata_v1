import { Routes } from '@angular/router';

export const EbookConversionRoutes: Routes = [
    {
        path: '',
        loadComponent: () => import('./ebook-conversion.component').then(c => c.EbookConversionComponent)
    },
    {
        path: 'markdown-to-epub',
        loadComponent: () => import('./markdown-to-epub/markdown-to-epub.component').then(c => c.MarkdownToEpubComponent)
    },
    {
        path: 'epub-to-mobi',
        loadComponent: () => import('./epub-to-mobi/epub-to-mobi.component').then(c => c.EpubToMobiComponent)
    },
    {
        path: 'epub-to-azw',
        loadComponent: () => import('./epub-to-azw/epub-to-azw.component').then(c => c.EpubToAzwComponent)
    },
    {
        path: 'mobi-to-epub',
        loadComponent: () => import('./mobi-to-epub/mobi-to-epub.component').then(c => c.MobiToEpubComponent)
    },
    {
        path: 'mobi-to-azw',
        loadComponent: () => import('./mobi-to-azw/mobi-to-azw.component').then(c => c.MobiToAzwComponent)
    },
    {
        path: 'azw-to-epub',
        loadComponent: () => import('./azw-to-epub/azw-to-epub.component').then(c => c.AzwToEpubComponent)
    },
    {
        path: 'azw-to-mobi',
        loadComponent: () => import('./azw-to-mobi/azw-to-mobi.component').then(c => c.AzwToMobiComponent)
    },
    {
        path: 'epub-to-pdf',
        loadComponent: () => import('./epub-to-pdf/epub-to-pdf.component').then(c => c.EpubToPdfComponent)
    },
    {
        path: 'mobi-to-pdf',
        loadComponent: () => import('./mobi-to-pdf/mobi-to-pdf.component').then(c => c.MobiToPdfComponent)
    },
    {
        path: 'azw-to-pdf',
        loadComponent: () => import('./azw-to-pdf/azw-to-pdf.component').then(c => c.AzwToPdfComponent)
    },
    {
        path: 'azw3-to-pdf',
        loadComponent: () => import('./azw3-to-pdf/azw3-to-pdf.component').then(c => c.Azw3ToPdfComponent)
    },
    {
        path: 'fb2-to-pdf',
        loadComponent: () => import('./fb2-to-pdf/fb2-to-pdf.component').then(c => c.Fb2ToPdfComponent)
    },
    {
        path: 'fbz-to-pdf',
        loadComponent: () => import('./fbz-to-pdf/fbz-to-pdf.component').then(c => c.FbzToPdfComponent)
    },
    {
        path: 'pdf-to-epub',
        loadComponent: () => import('./pdf-to-epub/pdf-to-epub.component').then(c => c.PdfToEpubComponent)
    },
    {
        path: 'pdf-to-mobi',
        loadComponent: () => import('./pdf-to-mobi/pdf-to-mobi.component').then(c => c.PdfToMobiComponent)
    },
    {
        path: 'pdf-to-azw',
        loadComponent: () => import('./pdf-to-azw/pdf-to-azw.component').then(c => c.PdfToAzwComponent)
    },
    {
        path: 'pdf-to-azw3',
        loadComponent: () => import('./pdf-to-azw3/pdf-to-azw3.component').then(c => c.PdfToAzw3Component)
    },
    {
        path: 'pdf-to-fb2',
        loadComponent: () => import('./pdf-to-fb2/pdf-to-fb2.component').then(c => c.PdfToFb2Component)
    },
    {
        path: 'pdf-to-fbz',
        loadComponent: () => import('./pdf-to-fbz/pdf-to-fbz.component').then(c => c.PdfToFbzComponent)
    }
];
