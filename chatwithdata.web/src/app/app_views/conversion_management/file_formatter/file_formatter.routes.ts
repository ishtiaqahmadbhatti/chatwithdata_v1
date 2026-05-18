import { Routes } from '@angular/router';

export const FileFormatterRoutes: Routes = [
    {
        path: '',
        loadComponent: () => import('./file-formatter-formatter.component').then(c => c.FileFormatterComponent)
    },
    {
        path: 'format-json',
        loadComponent: () => import('./format-json/format-json.component').then(c => c.FormatJsonComponent)
    },
    {
        path: 'validate-json',
        loadComponent: () => import('./validate-json/validate-json.component').then(c => c.ValidateJsonComponent)
    },
    {
        path: 'validate-xml',
        loadComponent: () => import('./validate-xml/validate-xml.component').then(c => c.ValidateXmlComponent)
    },
    {
        path: 'validate-xsd',
        loadComponent: () => import('./validate-xsd/validate-xsd.component').then(c => c.ValidateXsdComponent)
    },
    {
        path: 'minify-json',
        loadComponent: () => import('./minify-json/minify-json.component').then(c => c.MinifyJsonComponent)
    },
    {
        path: 'format-xml',
        loadComponent: () => import('./format-xml/format-xml.component').then(c => c.FormatXmlComponent)
    },
    {
        path: 'json-schema-info',
        loadComponent: () => import('./json-schema-info/json-schema-info.component').then(c => c.JsonSchemaInfoComponent)
    }
];
