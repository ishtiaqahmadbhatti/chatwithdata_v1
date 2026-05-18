import { Injectable } from '@angular/core';
import { HttpClient, HttpEvent } from '@angular/common/http';
import { ApplicationConfiguration } from '../app.config';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class SubtitleConversionService {

    private apiUrl: string;
    private serverBaseUrl: string;
    private subtitleToolsUrl: string;

    constructor(private http: HttpClient) {
        const config = ApplicationConfiguration.Get();
        this.apiUrl = config.ApiServiceLink;
        this.serverBaseUrl = config.ServerBaseUrl;
        this.subtitleToolsUrl = `${this.apiUrl}/subtitleconversiontools`;
    }

    ConvertFile(endpointSlug: string, file: File | null, outputFilename?: string, fileKey?: string, options?: Record<string, string>): Observable<HttpEvent<any>> {
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
        if (options) {
            Object.keys(options).forEach(key => {
                if (options[key]) {
                    formData.append(key, options[key]);
                }
            });
        }

        // Handle AI tools mapping
        let finalEndpoint = endpointSlug;
        if (endpointSlug.endsWith('-ai')) {
            const parts = endpointSlug.split('-');
            parts.pop(); // Remove 'ai'
            finalEndpoint = `ai/${parts.join('-')}`;
        }

        return this.http.post(`${this.subtitleToolsUrl}/${finalEndpoint}`, formData, {
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

    getSupportedLanguages(): Observable<any> {
        return this.http.get(`${this.subtitleToolsUrl}/supported-languages`);
    }

}
