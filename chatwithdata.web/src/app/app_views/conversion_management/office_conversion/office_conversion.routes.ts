import { Routes } from '@angular/router';

export const OfficeConversionRoutes: Routes = [
    {
        path: '',
        loadComponent: () => import('./office-conversion.component').then(c => c.OfficeConversionComponent)
    },
    {
        path: 'pdf-to-csv',
        loadComponent: () => import('./pdf-to-csv/pdf-to-csv.component').then(c => c.PdfToCsvComponent)
    },
    {
        path: 'pdf-to-excel',
        loadComponent: () => import('./pdf-to-excel/pdf-to-excel.component').then(c => c.PdfToExcelComponent)
    },
    {
        path: 'pdf-to-word',
        loadComponent: () => import('./pdf-to-word/pdf-to-word.component').then(c => c.PdfToWordComponent)
    },
    {
        path: 'word-to-pdf',
        loadComponent: () => import('./word-to-pdf/word-to-pdf.component').then(c => c.WordToPdfComponent)
    },
    {
        path: 'word-to-html',
        loadComponent: () => import('./word-to-html/word-to-html.component').then(c => c.WordToHtmlComponent)
    },
    {
        path: 'word-to-text',
        loadComponent: () => import('./word-to-text/word-to-text.component').then(c => c.WordToTextComponent)
    },
    {
        path: 'powerpoint-to-pdf',
        loadComponent: () => import('./powerpoint-to-pdf/powerpoint-to-pdf.component').then(c => c.PowerpointToPdfComponent)
    },
    {
        path: 'powerpoint-to-html',
        loadComponent: () => import('./powerpoint-to-html/powerpoint-to-html.component').then(c => c.PowerpointToHtmlComponent)
    },
    {
        path: 'powerpoint-to-text',
        loadComponent: () => import('./powerpoint-to-text/powerpoint-to-text.component').then(c => c.PowerpointToTextComponent)
    },
    {
        path: 'excel-to-pdf',
        loadComponent: () => import('./excel-to-pdf/excel-to-pdf.component').then(c => c.ExcelToPdfComponent)
    },
    {
        path: 'excel-to-xps',
        loadComponent: () => import('./excel-to-xps/excel-to-xps.component').then(c => c.ExcelToXpsComponent)
    },
    {
        path: 'excel-to-html',
        loadComponent: () => import('./excel-to-html/excel-to-html.component').then(c => c.ExcelToHtmlComponent)
    },
    {
        path: 'excel-to-csv',
        loadComponent: () => import('./excel-to-csv/excel-to-csv.component').then(c => c.ExcelToCsvComponent)
    },
    {
        path: 'excel-to-ods',
        loadComponent: () => import('./excel-to-ods/excel-to-ods.component').then(c => c.ExcelToOdsComponent)
    },
    {
        path: 'ods-to-csv',
        loadComponent: () => import('./ods-to-csv/ods-to-csv.component').then(c => c.OdsToCsvComponent)
    },
    {
        path: 'ods-to-pdf',
        loadComponent: () => import('./ods-to-pdf/ods-to-pdf.component').then(c => c.OdsToPdfComponent)
    },
    {
        path: 'ods-to-excel',
        loadComponent: () => import('./ods-to-excel/ods-to-excel.component').then(c => c.OdsToExcelComponent)
    },
    {
        path: 'csv-to-excel',
        loadComponent: () => import('./csv-to-excel/csv-to-excel.component').then(c => c.CsvToExcelComponent)
    },
    {
        path: 'excel-to-xml',
        loadComponent: () => import('./excel-to-xml/excel-to-xml.component').then(c => c.ExcelToXmlComponent)
    },
    {
        path: 'xml-to-csv',
        loadComponent: () => import('./xml-to-csv/xml-to-csv.component').then(c => c.XmlToCsvComponent)
    },
    {
        path: 'xml-to-excel',
        loadComponent: () => import('./xml-to-excel/xml-to-excel.component').then(c => c.XmlToExcelComponent)
    },
    {
        path: 'json-to-excel',
        loadComponent: () => import('./json-to-excel/json-to-excel.component').then(c => c.JsonToExcelComponent)
    },
    {
        path: 'excel-to-json',
        loadComponent: () => import('./excel-to-json/excel-to-json.component').then(c => c.ExcelToJsonComponent)
    },
    {
        path: 'json-objects-to-excel',
        loadComponent: () => import('./json-objects-to-excel/json-objects-to-excel.component').then(c => c.JsonObjectsToExcelComponent)
    },
    {
        path: 'bson-to-excel',
        loadComponent: () => import('./bson-to-excel/bson-to-excel.component').then(c => c.BsonToExcelComponent)
    },
    {
        path: 'srt-to-excel',
        loadComponent: () => import('./srt-to-excel/srt-to-excel.component').then(c => c.SrtToExcelComponent)
    },
    {
        path: 'srt-to-xlsx',
        loadComponent: () => import('./srt-to-xlsx/srt-to-xlsx.component').then(c => c.SrtToXlsxComponent)
    },
    {
        path: 'srt-to-xls',
        loadComponent: () => import('./srt-to-xls/srt-to-xls.component').then(c => c.SrtToXlsComponent)
    },
    {
        path: 'excel-to-srt',
        loadComponent: () => import('./excel-to-srt/excel-to-srt.component').then(c => c.ExcelToSrtComponent)
    },
    {
        path: 'xlsx-to-srt',
        loadComponent: () => import('./xlsx-to-srt/xlsx-to-srt.component').then(c => c.XlsxToSrtComponent)
    },
    {
        path: 'xls-to-srt',
        loadComponent: () => import('./xls-to-srt/xls-to-srt.component').then(c => c.XlsToSrtComponent)
    }
];
