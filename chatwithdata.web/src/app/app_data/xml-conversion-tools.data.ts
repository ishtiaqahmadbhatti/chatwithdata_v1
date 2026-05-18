import { ConversionTool } from '../app_models/conversion-tool.model';

export const XML_CONVERSION_TOOLS: ConversionTool[] = [
    {
        id: 'csv-to-xml',
        title: 'CSV to XML',
        description: 'Convert CSV files to XML format',
        sourceIcon: 'fas fa-file-csv',
        targetIcon: 'fas fa-file-code',
        route: '/xmlconversion/csv-to-xml'
    },
    {
        id: 'excel-to-xml',
        title: 'Excel to XML',
        description: 'Convert Excel spread sheets to XML',
        sourceIcon: 'fas fa-file-excel',
        targetIcon: 'fas fa-file-code',
        route: '/xmlconversion/excel-to-xml'
    },
    {
        id: 'xml-to-json',
        title: 'XML to JSON',
        description: 'Convert XML files to JSON format',
        sourceIcon: 'fas fa-file-code',
        targetIcon: 'fas fa-file-code',
        route: '/xmlconversion/xml-to-json'
    },
    {
        id: 'xml-to-csv',
        title: 'XML to CSV',
        description: 'Convert XML files to CSV format',
        sourceIcon: 'fas fa-file-code',
        targetIcon: 'fas fa-file-csv',
        route: '/xmlconversion/xml-to-csv'
    },
    {
        id: 'xml-to-excel',
        title: 'XML to Excel',
        description: 'Convert XML files to Excel format',
        sourceIcon: 'fas fa-file-code',
        targetIcon: 'fas fa-file-excel',
        route: '/xmlconversion/xml-to-excel'
    },
    {
        id: 'fix-xml-escaping',
        title: 'Fix XML Escaping',
        description: 'Fix common XML escaping issues',
        sourceIcon: 'fas fa-file-code',
        targetIcon: 'fas fa-check-circle',
        route: '/xmlconversion/fix-xml-escaping'
    },
    {
        id: 'xml-xsd-validator',
        title: 'XML XSD Validator',
        description: 'Validate XML files against XSD schema',
        sourceIcon: 'fas fa-file-code',
        targetIcon: 'fas fa-check-circle',
        route: '/xmlconversion/xml-xsd-validator'
    },
    {
        id: 'json-to-xml',
        title: 'JSON to XML',
        description: 'Convert JSON files to XML format',
        sourceIcon: 'fas fa-file-code',
        targetIcon: 'fas fa-file-code',
        route: '/xmlconversion/json-to-xml'
    }
];
