import { ConversionTool } from '../app_models/conversion-tool.model';

export const JSON_CONVERSION_TOOLS: ConversionTool[] = [
    {
        id: 'pdf-to-json-ai',
        title: 'AI PDF to JSON',
        description: 'Convert PDF documents to JSON format using AI',
        sourceIcon: 'fas fa-file-pdf',
        targetIcon: 'fas fa-file-code',
        route: '/jsonconversion/pdf-to-json-ai'
    },
    {
        id: 'png-to-json-ai',
        title: 'AI PNG to JSON',
        description: 'Convert PNG images to JSON format using AI',
        sourceIcon: 'fas fa-file-image',
        targetIcon: 'fas fa-file-code',
        route: '/jsonconversion/png-to-json-ai'
    },
    {
        id: 'jpg-to-json-ai',
        title: 'AI JPG to JSON',
        description: 'Convert JPG images to JSON format using AI',
        sourceIcon: 'fas fa-file-image',
        targetIcon: 'fas fa-file-code',
        route: '/jsonconversion/jpg-to-json-ai'
    },
    {
        id: 'xml-to-json',
        title: 'XML to JSON',
        description: 'Convert XML files to JSON format',
        sourceIcon: 'fas fa-file-code',
        targetIcon: 'fas fa-file-code',
        route: '/jsonconversion/xml-to-json'
    },
    {
        id: 'json-formatter',
        title: 'JSON Formatter',
        description: 'Format and beautify your JSON data',
        sourceIcon: 'fas fa-file-code',
        targetIcon: 'fas fa-indent',
        route: '/jsonconversion/json-formatter'
    },
    {
        id: 'json-validator',
        title: 'JSON Validator',
        description: 'Validate your JSON data',
        sourceIcon: 'fas fa-file-code',
        targetIcon: 'fas fa-check-circle',
        route: '/jsonconversion/json-validator'
    },
    {
        id: 'json-to-xml',
        title: 'JSON to XML',
        description: 'Convert JSON files to XML format',
        sourceIcon: 'fas fa-file-code',
        targetIcon: 'fas fa-file-code',
        route: '/jsonconversion/json-to-xml'
    },
    {
        id: 'json-to-csv',
        title: 'JSON to CSV',
        description: 'Convert JSON data to CSV format',
        sourceIcon: 'fas fa-file-code',
        targetIcon: 'fas fa-file-csv',
        route: '/jsonconversion/json-to-csv'
    },
    {
        id: 'json-to-excel',
        title: 'JSON to Excel',
        description: 'Convert JSON data to Excel format',
        sourceIcon: 'fas fa-file-code',
        targetIcon: 'fas fa-file-excel',
        route: '/jsonconversion/json-to-excel'
    },
    {
        id: 'excel-to-json',
        title: 'Excel to JSON',
        description: 'Convert Excel files to JSON format',
        sourceIcon: 'fas fa-file-excel',
        targetIcon: 'fas fa-file-code',
        route: '/jsonconversion/excel-to-json'
    },
    {
        id: 'csv-to-json',
        title: 'CSV to JSON',
        description: 'Convert CSV files to JSON format',
        sourceIcon: 'fas fa-file-csv',
        targetIcon: 'fas fa-file-code',
        route: '/jsonconversion/csv-to-json'
    },
    {
        id: 'json-to-yaml',
        title: 'JSON to YAML',
        description: 'Convert JSON data to YAML format',
        sourceIcon: 'fas fa-file-code',
        targetIcon: 'fas fa-file-code',
        route: '/jsonconversion/json-to-yaml'
    },
    {
        id: 'json-objects-to-csv',
        title: 'JSON Objects to CSV',
        description: 'Convert array of JSON objects to CSV',
        sourceIcon: 'fas fa-file-code',
        targetIcon: 'fas fa-file-csv',
        route: '/jsonconversion/json-objects-to-csv'
    },
    {
        id: 'json-objects-to-excel',
        title: 'JSON Objects to Excel',
        description: 'Convert array of JSON objects to Excel',
        sourceIcon: 'fas fa-file-code',
        targetIcon: 'fas fa-file-excel',
        route: '/jsonconversion/json-objects-to-excel'
    },
    {
        id: 'yaml-to-json',
        title: 'YAML to JSON',
        description: 'Convert YAML files to JSON format',
        sourceIcon: 'fas fa-file-code',
        targetIcon: 'fas fa-file-code',
        route: '/jsonconversion/yaml-to-json'
    }
];
