import { Routes } from '@angular/router';

export const JSONConversionRoutes: Routes = [
  {
    path: '',
    loadComponent: () => import('./json-conversion.component').then(c => c.JsonConversionComponent)
  },
  {
    path: 'json-to-csv',
    loadComponent: () => import('./json-to-csv/json-to-csv.component').then(c => c.JsonToCsvComponent)
  },
  {
    path: 'pdf-to-json-ai',
    loadComponent: () => import('./pdf-to-json-ai/pdf-to-json-ai.component').then(c => c.PdfToJsonAiComponent)
  },
  {
    path: 'png-to-json-ai',
    loadComponent: () => import('./png-to-json-ai/png-to-json-ai.component').then(c => c.PngToJsonAiComponent)
  },
  {
    path: 'jpg-to-json-ai',
    loadComponent: () => import('./jpg-to-json-ai/jpg-to-json-ai.component').then(c => c.JpgToJsonAiComponent)
  },
  {
    path: 'xml-to-json',
    loadComponent: () => import('./xml-to-json/xml-to-json.component').then(c => c.XmlToJsonComponent)
  },
  {
    path: 'json-formatter',
    loadComponent: () => import('./json-formatter/json-formatter.component').then(c => c.JsonFormatterComponent)
  },
  {
    path: 'json-validator',
    loadComponent: () => import('./json-validator/json-validator.component').then(c => c.JsonValidatorComponent)
  },
  {
    path: 'json-to-xml',
    loadComponent: () => import('./json-to-xml/json-to-xml.component').then(c => c.JsonToXmlComponent)
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
    path: 'csv-to-json',
    loadComponent: () => import('./csv-to-json/csv-to-json.component').then(c => c.CsvToJsonComponent)
  },
  {
    path: 'json-to-yaml',
    loadComponent: () => import('./json-to-yaml/json-to-yaml.component').then(c => c.JsonToYamlComponent)
  },
  {
    path: 'json-objects-to-csv',
    loadComponent: () => import('./json-objects-to-csv/json-objects-to-csv.component').then(c => c.JsonObjectsToCsvComponent)
  },
  {
    path: 'json-objects-to-excel',
    loadComponent: () => import('./json-objects-to-excel/json-objects-to-excel.component').then(c => c.JsonObjectsToExcelComponent)
  },
  {
    path: 'yaml-to-json',
    loadComponent: () => import('./yaml-to-json/yaml-to-json.component').then(c => c.YamlToJsonComponent)
  }
];
