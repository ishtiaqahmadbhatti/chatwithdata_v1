import { Routes } from '@angular/router';
import { MarkdownConversionComponent } from './markdown-conversion.component';

export const MARKDOWN_CONVERSION_ROUTES: Routes = [
    { path: '', component: MarkdownConversionComponent },
    {
        path: 'pdf-to-markdown',
        loadComponent: () => import('./pdf-to-markdown/pdf-to-markdown.component').then(m => m.PdfToMarkdownComponent)
    },
    {
        path: 'markdown-to-pdf',
        loadComponent: () => import('./markdown-to-pdf/markdown-to-pdf.component').then(m => m.MarkdownToPdfComponent)
    },
    {
        path: 'markdown-to-html',
        loadComponent: () => import('./markdown-to-html/markdown-to-html.component').then(m => m.MarkdownToHtmlComponent)
    },
    {
        path: 'markdown-to-epub',
        loadComponent: () => import('./markdown-to-epub/markdown-to-epub.component').then(m => m.MarkdownToEpubComponent)
    },
    {
        path: 'markdown-to-word',
        loadComponent: () => import('./markdown-to-word/markdown-to-word.component').then(m => m.MarkdownToWordComponent)
    },
    {
        path: 'markdown-to-latex',
        loadComponent: () => import('./markdown-to-latex/markdown-to-latex.component').then(m => m.MarkdownToLatexComponent)
    },
    {
        path: 'markdown-to-text',
        loadComponent: () => import('./markdown-to-text/markdown-to-text.component').then(m => m.MarkdownToTextComponent)
    },
    {
        path: 'html-to-markdown',
        loadComponent: () => import('./html-to-markdown/html-to-markdown.component').then(m => m.HtmlToMarkdownComponent)
    },
    {
        path: 'word-to-markdown',
        loadComponent: () => import('./word-to-markdown/word-to-markdown.component').then(m => m.WordToMarkdownComponent)
    }
];
