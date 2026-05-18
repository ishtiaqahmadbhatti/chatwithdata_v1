import { Routes } from '@angular/router';

export const XMLConversionRoutes: Routes = [
    {
        path: '',
        loadComponent: () => import('./xml-conversion.component').then(c => c.XmlConversionComponent)
    },
    {
        path: 'csv-to-xml',
        loadComponent: () => import('./csv-to-xml/csv-to-xml.component').then(c => c.CsvToXmlComponent)
    },
    {
        path: 'excel-to-xml',
        loadComponent: () => import('./excel-to-xml/excel-to-xml.component').then(c => c.ExcelToXmlComponent)
    },
    {
        path: 'xml-to-json',
        loadComponent: () => import('./xml-to-json/xml-to-json.component').then(c => c.XmlToJsonComponent)
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
        path: 'fix-xml-escaping',
        loadComponent: () => import('./fix-xml-escaping/fix-xml-escaping.component').then(c => c.FixXmlEscapingComponent)
    },
    {
        path: 'xml-xsd-validator',
        loadComponent: () => import('./xml-xsd-validator/xml-xsd-validator.component').then(c => c.XmlXsdValidatorComponent)
    },
    {
        path: 'json-to-xml',
        loadComponent: () => import('./json-to-xml/json-to-xml.component').then(c => c.JsonToXmlComponent)
    }
];
