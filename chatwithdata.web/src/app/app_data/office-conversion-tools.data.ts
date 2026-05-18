import { ConversionTool } from '../app_models/conversion-tool.model';

export const OFFICE_CONVERSION_TOOLS: ConversionTool[] = [
    {
        id: 'pdf-to-csv',
        title: 'PDF to CSV',
        description: 'Convert PDF to CSV format',
        sourceIcon: 'fas fa-file-pdf',
        targetIcon: 'fas fa-file-csv',
        route: '/officeconversion/pdf-to-csv'
    },
    {
        id: 'pdf-to-excel',
        title: 'PDF to Excel',
        description: 'Convert PDF to Excel format',
        sourceIcon: 'fas fa-file-pdf',
        targetIcon: 'fas fa-file-excel',
        route: '/officeconversion/pdf-to-excel'
    },
    {
        id: 'pdf-to-word',
        title: 'PDF to Word',
        description: 'Convert PDF to Word format',
        sourceIcon: 'fas fa-file-pdf',
        targetIcon: 'fas fa-file-word',
        route: '/officeconversion/pdf-to-word'
    },
    {
        id: 'word-to-pdf',
        title: 'Word to PDF',
        description: 'Convert Word to PDF format',
        sourceIcon: 'fas fa-file-word',
        targetIcon: 'fas fa-file-pdf',
        route: '/officeconversion/word-to-pdf'
    },
    {
        id: 'word-to-html',
        title: 'Word to HTML',
        description: 'Convert Word to HTML format',
        sourceIcon: 'fas fa-file-word',
        targetIcon: 'fas fa-file-code',
        route: '/officeconversion/word-to-html'
    },
    {
        id: 'word-to-text',
        title: 'Word to Text',
        description: 'Convert Word to Text format',
        sourceIcon: 'fas fa-file-word',
        targetIcon: 'fas fa-file-alt',
        route: '/officeconversion/word-to-text'
    },
    {
        id: 'powerpoint-to-pdf',
        title: 'PowerPoint to PDF',
        description: 'Convert PowerPoint to PDF format',
        sourceIcon: 'fas fa-file-powerpoint',
        targetIcon: 'fas fa-file-pdf',
        route: '/officeconversion/powerpoint-to-pdf'
    },
    {
        id: 'powerpoint-to-html',
        title: 'PowerPoint to HTML',
        description: 'Convert PowerPoint to HTML format',
        sourceIcon: 'fas fa-file-powerpoint',
        targetIcon: 'fas fa-file-code',
        route: '/officeconversion/powerpoint-to-html'
    },
    {
        id: 'powerpoint-to-text',
        title: 'PowerPoint to Text',
        description: 'Convert PowerPoint to Text format',
        sourceIcon: 'fas fa-file-powerpoint',
        targetIcon: 'fas fa-file-alt',
        route: '/officeconversion/powerpoint-to-text'
    },
    {
        id: 'excel-to-pdf',
        title: 'Excel to PDF',
        description: 'Convert Excel to PDF format',
        sourceIcon: 'fas fa-file-excel',
        targetIcon: 'fas fa-file-pdf',
        route: '/officeconversion/excel-to-pdf'
    },
    {
        id: 'excel-to-xps',
        title: 'Excel to XPS',
        description: 'Convert Excel to XPS format',
        sourceIcon: 'fas fa-file-excel',
        targetIcon: 'fas fa-file-word',
        route: '/officeconversion/excel-to-xps'
    },
    {
        id: 'excel-to-html',
        title: 'Excel to HTML',
        description: 'Convert Excel to HTML format',
        sourceIcon: 'fas fa-file-excel',
        targetIcon: 'fas fa-file-code',
        route: '/officeconversion/excel-to-html'
    },
    {
        id: 'excel-to-csv',
        title: 'Excel to CSV',
        description: 'Convert Excel to CSV format',
        sourceIcon: 'fas fa-file-excel',
        targetIcon: 'fas fa-file-csv',
        route: '/officeconversion/excel-to-csv'
    },
    {
        id: 'excel-to-ods',
        title: 'Excel to ODS',
        description: 'Convert Excel to ODS format',
        sourceIcon: 'fas fa-file-excel',
        targetIcon: 'fas fa-file-excel',
        route: '/officeconversion/excel-to-ods'
    },
    {
        id: 'ods-to-csv',
        title: 'ODS to CSV',
        description: 'Convert ODS to CSV format',
        sourceIcon: 'fas fa-file-excel',
        targetIcon: 'fas fa-file-csv',
        route: '/officeconversion/ods-to-csv'
    },
    {
        id: 'ods-to-pdf',
        title: 'ODS to PDF',
        description: 'Convert ODS to PDF format',
        sourceIcon: 'fas fa-file-excel',
        targetIcon: 'fas fa-file-pdf',
        route: '/officeconversion/ods-to-pdf'
    },
    {
        id: 'ods-to-excel',
        title: 'ODS to Excel',
        description: 'Convert ODS to Excel format',
        sourceIcon: 'fas fa-file-excel',
        targetIcon: 'fas fa-file-excel',
        route: '/officeconversion/ods-to-excel'
    },
    {
        id: 'csv-to-excel',
        title: 'CSV to Excel',
        description: 'Convert CSV to Excel format',
        sourceIcon: 'fas fa-file-csv',
        targetIcon: 'fas fa-file-excel',
        route: '/officeconversion/csv-to-excel'
    },
    {
        id: 'excel-to-xml',
        title: 'Excel to XML',
        description: 'Convert Excel to XML format',
        sourceIcon: 'fas fa-file-excel',
        targetIcon: 'fas fa-file-code',
        route: '/officeconversion/excel-to-xml'
    },
    {
        id: 'xml-to-csv',
        title: 'XML to CSV',
        description: 'Convert XML to CSV format',
        sourceIcon: 'fas fa-file-code',
        targetIcon: 'fas fa-file-csv',
        route: '/officeconversion/xml-to-csv'
    },
    {
        id: 'xml-to-excel',
        title: 'XML to Excel',
        description: 'Convert XML to Excel format',
        sourceIcon: 'fas fa-file-code',
        targetIcon: 'fas fa-file-excel',
        route: '/officeconversion/xml-to-excel'
    },
    {
        id: 'json-to-excel',
        title: 'JSON to Excel',
        description: 'Convert JSON to Excel format',
        sourceIcon: 'fas fa-file-code',
        targetIcon: 'fas fa-file-excel',
        route: '/officeconversion/json-to-excel'
    },
    {
        id: 'excel-to-json',
        title: 'Excel to JSON',
        description: 'Convert Excel to JSON format',
        sourceIcon: 'fas fa-file-excel',
        targetIcon: 'fas fa-file-code',
        route: '/officeconversion/excel-to-json'
    },
    {
        id: 'json-objects-to-excel',
        title: 'JSON Objects to Excel',
        description: 'Convert JSON Objects to Excel',
        sourceIcon: 'fas fa-file-code',
        targetIcon: 'fas fa-file-excel',
        route: '/officeconversion/json-objects-to-excel'
    },
    {
        id: 'bson-to-excel',
        title: 'BSON to Excel',
        description: 'Convert BSON to Excel format',
        sourceIcon: 'fas fa-database',
        targetIcon: 'fas fa-file-excel',
        route: '/officeconversion/bson-to-excel'
    },
    {
        id: 'srt-to-excel',
        title: 'SRT to Excel',
        description: 'Convert SRT to Excel format',
        sourceIcon: 'fas fa-closed-captioning',
        targetIcon: 'fas fa-file-excel',
        route: '/officeconversion/srt-to-excel'
    },
    {
        id: 'srt-to-xlsx',
        title: 'SRT to XLSX',
        description: 'Convert SRT to XLSX format',
        sourceIcon: 'fas fa-closed-captioning',
        targetIcon: 'fas fa-file-excel',
        route: '/officeconversion/srt-to-xlsx'
    },
    {
        id: 'srt-to-xls',
        title: 'SRT to XLS',
        description: 'Convert SRT to XLS format',
        sourceIcon: 'fas fa-closed-captioning',
        targetIcon: 'fas fa-file-excel',
        route: '/officeconversion/srt-to-xls'
    },
    {
        id: 'excel-to-srt',
        title: 'Excel to SRT',
        description: 'Convert Excel to SRT format',
        sourceIcon: 'fas fa-file-excel',
        targetIcon: 'fas fa-closed-captioning',
        route: '/officeconversion/excel-to-srt'
    },
    {
        id: 'xlsx-to-srt',
        title: 'XLSX to SRT',
        description: 'Convert XLSX to SRT format',
        sourceIcon: 'fas fa-file-excel',
        targetIcon: 'fas fa-closed-captioning',
        route: '/officeconversion/xlsx-to-srt'
    },
    {
        id: 'xls-to-srt',
        title: 'XLS to SRT',
        description: 'Convert XLS to SRT format',
        sourceIcon: 'fas fa-file-excel',
        targetIcon: 'fas fa-closed-captioning',
        route: '/officeconversion/xls-to-srt'
    }
];
