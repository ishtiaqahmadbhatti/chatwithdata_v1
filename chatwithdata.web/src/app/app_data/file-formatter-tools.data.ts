import { ConversionTool } from '../app_models/conversion-tool.model';

export const FILE_FORMATTER_TOOLS: ConversionTool[] = [
    {
        id: 'format-json',
        title: 'Format JSON',
        description: 'Format and beautify JSON files',
        sourceIcon: 'fas fa-file-code',
        targetIcon: 'fas fa-indent',
        route: '/fileformatter/format-json'
    },
    {
        id: 'validate-json',
        title: 'Validate JSON',
        description: 'Validate JSON files for errors',
        sourceIcon: 'fas fa-file-code',
        targetIcon: 'fas fa-check-circle',
        route: '/fileformatter/validate-json'
    },
    {
        id: 'validate-xml',
        title: 'Validate XML',
        description: 'Validate XML files for errors',
        sourceIcon: 'fas fa-file-code',
        targetIcon: 'fas fa-check-circle',
        route: '/fileformatter/validate-xml'
    },
    {
        id: 'validate-xsd',
        title: 'Validate XSD',
        description: 'Validate XSD schema files',
        sourceIcon: 'fas fa-file-code',
        targetIcon: 'fas fa-check-circle',
        route: '/fileformatter/validate-xsd'
    },
    {
        id: 'minify-json',
        title: 'Minify JSON',
        description: 'Minify JSON files to reduce size',
        sourceIcon: 'fas fa-file-code',
        targetIcon: 'fas fa-compress',
        route: '/fileformatter/minify-json'
    },
    {
        id: 'format-xml',
        title: 'Format XML',
        description: 'Format and beautify XML files',
        sourceIcon: 'fas fa-file-code',
        targetIcon: 'fas fa-indent',
        route: '/fileformatter/format-xml'
    },
    {
        id: 'json-schema-info',
        title: 'JSON Schema Info',
        description: 'Get information about JSON schema',
        sourceIcon: 'fas fa-file-code',
        targetIcon: 'fas fa-info-circle',
        route: '/fileformatter/json-schema-info'
    }
];
