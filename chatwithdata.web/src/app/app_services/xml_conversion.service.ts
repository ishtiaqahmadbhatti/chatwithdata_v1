import { Injectable } from '@angular/core';
import { HttpClient, HttpEvent } from '@angular/common/http';
import { ApplicationConfiguration } from '../app.config';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class XMLConversionService {

    private apiUrl: string;
    private serverBaseUrl: string;
    private xmlToolsUrl: string;

    constructor(private http: HttpClient) {
        const config = ApplicationConfiguration.Get();
        this.apiUrl = config.ApiServiceLink;
        this.serverBaseUrl = config.ServerBaseUrl;
        this.xmlToolsUrl = `${this.apiUrl}/xmlconversiontools`;
    }

    ConvertFile(endpointSlug: string, file: File | null, outputFilename?: string, fileKey?: string): Observable<HttpEvent<any>> {
        const formData: FormData = new FormData();
        if (file) {
            formData.append('file', file, file.name);
        }
        if (fileKey) {
            formData.append('file_key', fileKey);
        }
        if (outputFilename) {
            formData.append('output_filename', outputFilename);
            formData.append('filename', outputFilename);
        }

        // Handle AI tools mapping
        let finalEndpoint = endpointSlug;
        if (endpointSlug.endsWith('-ai')) {
            const parts = endpointSlug.split('-');
            parts.pop(); // Remove 'ai'
            finalEndpoint = `ai/${parts.join('-')}`;
        }

        return this.http.post(`${this.xmlToolsUrl}/${finalEndpoint}`, formData, {
            reportProgress: true,
            observe: 'events'
        });
    }

    ValidateXmlXsd(xmlFile: File | null, xsdFile: File | null): Observable<HttpEvent<any>> {
        const formData: FormData = new FormData();
        if (xmlFile) {
            formData.append('file_xml', xmlFile, xmlFile.name);
        }
        if (xsdFile) {
            formData.append('file_xsd', xsdFile, xsdFile.name);
        }

        return this.http.post(`${this.xmlToolsUrl}/xml-xsd-validator`, formData, {
            reportProgress: true,
            observe: 'events'
        });
    }

    downloadFile(url: string): Observable<Blob> {
        // Construct full URL if it's a relative path
        let fullUrl = url;
        if (!url.startsWith('http')) {
            // If URL starts with /, append to ServerBaseUrl (Root), not ApiUrl
            if (url.startsWith('/')) {
                fullUrl = `${this.serverBaseUrl}${url}`;
            } else {
                fullUrl = `${this.serverBaseUrl}/${url}`;
            }
        }

        return this.http.get(fullUrl, {
            responseType: 'blob'
        });
    }

}
