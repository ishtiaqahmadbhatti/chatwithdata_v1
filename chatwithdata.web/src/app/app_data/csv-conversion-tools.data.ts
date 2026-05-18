import { ConversionTool } from '../app_models/conversion-tool.model';

export const CSV_CONVERSION_TOOLS: ConversionTool[] = [
    {
        id: 'html-table-to-csv',
        title: 'HTML Table to CSV',
        description: 'Convert HTML tables to CSV format',
        sourceIcon: 'fas fa-table',
        targetIcon: 'fas fa-file-csv',
        route: '/csvconversion/html-table-to-csv'
    },
    {
        id: 'excel-to-csv',
        title: 'Excel to CSV',
        description: 'Convert Excel spread sheets to CSV',
        sourceIcon: 'fas fa-file-excel',
        targetIcon: 'fas fa-file-csv',
        route: '/csvconversion/excel-to-csv'
    },
    {
        id: 'ods-to-csv',
        title: 'ODS to CSV',
        description: 'Convert ODS spreadsheets to CSV',
        sourceIcon: 'fas fa-file-excel',
        targetIcon: 'fas fa-file-csv',
        route: '/csvconversion/ods-to-csv'
    },
    {
        id: 'csv-to-excel',
        title: 'CSV to Excel',
        description: 'Convert CSV files to Excel format',
        sourceIcon: 'fas fa-file-csv',
        targetIcon: 'fas fa-file-excel',
        route: '/csvconversion/csv-to-excel'
    },
    {
        id: 'csv-to-xml',
        title: 'CSV to XML',
        description: 'Convert CSV files to XML format',
        sourceIcon: 'fas fa-file-csv',
        targetIcon: 'fas fa-file-code',
        route: '/csvconversion/csv-to-xml'
    },
    {
        id: 'xml-to-csv',
        title: 'XML to CSV',
        description: 'Convert XML files to CSV format',
        sourceIcon: 'fas fa-file-code',
        targetIcon: 'fas fa-file-csv',
        route: '/csvconversion/xml-to-csv'
    },
    {
        id: 'pdf-to-csv',
        title: 'PDF to CSV',
        description: 'Extract tables from PDF to CSV',
        sourceIcon: 'fas fa-file-pdf',
        targetIcon: 'fas fa-file-csv',
        route: '/csvconversion/pdf-to-csv'
    },
    {
        id: 'json-to-csv',
        title: 'JSON to CSV',
        description: 'Convert JSON data to CSV',
        sourceIcon: 'fas fa-file-code',
        targetIcon: 'fas fa-file-csv',
        route: '/csvconversion/json-to-csv'
    },
    {
        id: 'csv-to-json',
        title: 'CSV to JSON',
        description: 'Convert CSV files to JSON format',
        sourceIcon: 'fas fa-file-csv',
        targetIcon: 'fas fa-file-code',
        route: '/csvconversion/csv-to-json'
    },
    {
        id: 'json-objects-to-csv',
        title: 'JSON Objects to CSV',
        description: 'Convert JSON objects to CSV',
        sourceIcon: 'fas fa-file-code',
        targetIcon: 'fas fa-file-csv',
        route: '/csvconversion/json-objects-to-csv'
    },
    {
        id: 'bson-to-csv',
        title: 'BSON to CSV',
        description: 'Convert BSON data to CSV',
        sourceIcon: 'fas fa-database',
        targetIcon: 'fas fa-file-csv',
        route: '/csvconversion/bson-to-csv'
    },
    {
        id: 'srt-to-csv',
        title: 'SRT to CSV',
        description: 'Convert Subtitles (SRT) to CSV',
        sourceIcon: 'fas fa-closed-captioning',
        targetIcon: 'fas fa-file-csv',
        route: '/csvconversion/srt-to-csv'
    },
    {
        id: 'csv-to-srt',
        title: 'CSV to SRT',
        description: 'Convert CSV to Subtitles (SRT)',
        sourceIcon: 'fas fa-file-csv',
        targetIcon: 'fas fa-closed-captioning',
        route: '/csvconversion/csv-to-srt'
    }
];
