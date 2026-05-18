import { Routes } from '@angular/router';

export const SubtitleConversionRoutes: Routes = [
    {
        path: '',
        loadComponent: () => import('./subtitle-conversion.component').then(c => c.SubtitleConversionComponent)
    },
    {
        path: 'translate-srt',
        loadComponent: () => import('./translate-srt/translate-srt.component').then(c => c.TranslateSrtComponent)
    },
    {
        path: 'srt-to-csv',
        loadComponent: () => import('./srt-to-csv/srt-to-csv.component').then(c => c.SrtToCsvComponent)
    },
    {
        path: 'srt-to-excel',
        loadComponent: () => import('./srt-to-excel/srt-to-excel.component').then(c => c.SrtToExcelComponent)
    },
    {
        path: 'srt-to-text',
        loadComponent: () => import('./srt-to-text/srt-to-text.component').then(c => c.SrtToTextComponent)
    },
    {
        path: 'srt-to-vtt',
        loadComponent: () => import('./srt-to-vtt/srt-to-vtt.component').then(c => c.SrtToVttComponent)
    },
    {
        path: 'vtt-to-text',
        loadComponent: () => import('./vtt-to-text/vtt-to-text.component').then(c => c.VttToTextComponent)
    },
    {
        path: 'vtt-to-srt',
        loadComponent: () => import('./vtt-to-srt/vtt-to-srt.component').then(c => c.VttToSrtComponent)
    },
    {
        path: 'csv-to-srt',
        loadComponent: () => import('./csv-to-srt/csv-to-srt.component').then(c => c.CsvToSrtComponent)
    },
    {
        path: 'excel-to-srt',
        loadComponent: () => import('./excel-to-srt/excel-to-srt.component').then(c => c.ExcelToSrtComponent)
    }
];
