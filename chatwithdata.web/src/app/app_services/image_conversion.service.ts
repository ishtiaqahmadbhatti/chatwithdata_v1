import { Injectable } from '@angular/core';
import { HttpClient, HttpEvent } from '@angular/common/http';
import { ApplicationConfiguration } from '../app.config';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class ImageConversionService {

    private apiUrl: string;
    private serverBaseUrl: string;
    private imageToolsUrl: string;

    constructor(private http: HttpClient) {
        const config = ApplicationConfiguration.Get();
        this.apiUrl = config.ApiServiceLink;
        this.serverBaseUrl = config.ServerBaseUrl;
        this.imageToolsUrl = `${this.apiUrl}/imageconversiontools`;
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

        let baseUrl = this.imageToolsUrl;
        let finalEndpoint = endpointSlug;

        // Handle AI tools mapping
        if (endpointSlug.endsWith('-ai')) {
            const parts = endpointSlug.split('-');
            parts.pop(); // Remove 'ai'
            
            // If it ends in -to-json, it might be in the JSON category
            if (endpointSlug.endsWith('-to-json-ai')) {
                baseUrl = `${this.apiUrl}/jsonconversiontools`;
            }
            
            finalEndpoint = `ai/${parts.join('-')}`;
        }

        return this.http.post(`${baseUrl}/${finalEndpoint}`, formData, {
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
