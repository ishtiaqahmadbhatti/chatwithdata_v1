import { Routes } from '@angular/router';

export const CSVConversionRoutes: Routes = [
    {
        path: '',
        loadComponent: () => import('./csv-conversion.component').then(c => c.CsvConversionComponent)
    },
    {
        path: 'html-table-to-csv',
        loadComponent: () => import('./html-table-to-csv/html-table-to-csv.component').then(c => c.HtmlTableToCsvComponent)
    },
    {
        path: 'excel-to-csv',
        loadComponent: () => import('./excel-to-csv/excel-to-csv.component').then(c => c.ExcelToCsvComponent)
    },
    {
        path: 'ods-to-csv',
        loadComponent: () => import('./ods-to-csv/ods-to-csv.component').then(c => c.OdsToCsvComponent)
    },
    {
        path: 'csv-to-excel',
        loadComponent: () => import('./csv-to-excel/csv-to-excel.component').then(c => c.CsvToExcelComponent)
    },
    {
        path: 'csv-to-xml',
        loadComponent: () => import('./csv-to-xml/csv-to-xml.component').then(c => c.CsvToXmlComponent)
    },
    {
        path: 'xml-to-csv',
        loadComponent: () => import('./xml-to-csv/xml-to-csv.component').then(c => c.XmlToCsvComponent)
    },
    {
        path: 'pdf-to-csv',
        loadComponent: () => import('./pdf-to-csv/pdf-to-csv.component').then(c => c.PdfToCsvComponent)
    },
    {
        path: 'json-to-csv',
        loadComponent: () => import('./json-to-csv/json-to-csv.component').then(c => c.JsonToCsvComponent)
    },
    {
        path: 'csv-to-json',
        loadComponent: () => import('./csv-to-json/csv-to-json.component').then(c => c.CsvToJsonComponent)
    },
    {
        path: 'json-objects-to-csv',
        loadComponent: () => import('./json-objects-to-csv/json-objects-to-csv.component').then(c => c.JsonObjectsToCsvComponent)
    },
    {
        path: 'bson-to-csv',
        loadComponent: () => import('./bson-to-csv/bson-to-csv.component').then(c => c.BsonToCsvComponent)
    },
    {
        path: 'srt-to-csv',
        loadComponent: () => import('./srt-to-csv/srt-to-csv.component').then(c => c.SrtToCsvComponent)
    },
    {
        path: 'csv-to-srt',
        loadComponent: () => import('./csv-to-srt/csv-to-srt.component').then(c => c.CsvToSrtComponent)
    }
];
