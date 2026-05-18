import { Routes } from '@angular/router';

export const TextConversionRoutes: Routes = [
    {
        path: '',
        loadComponent: () => import('./text-conversion.component').then(c => c.TextConversionComponent)
    },
    {
        path: 'word-to-text',
        loadComponent: () => import('./word-to-text/word-to-text.component').then(c => c.WordToTextComponent)
    },
    {
        path: 'powerpoint-to-text',
        loadComponent: () => import('./powerpoint-to-text/powerpoint-to-text.component').then(c => c.PowerpointToTextComponent)
    },
    {
        path: 'pdf-to-text',
        loadComponent: () => import('./pdf-to-text/pdf-to-text.component').then(c => c.PdfToTextComponent)
    },
    {
        path: 'srt-to-text',
        loadComponent: () => import('./srt-to-text/srt-to-text.component').then(c => c.SrtToTextComponent)
    },
    {
        path: 'vtt-to-text',
        loadComponent: () => import('./vtt-to-text/vtt-to-text.component').then(c => c.VttToTextComponent)
    }
];
