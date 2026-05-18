import { Injectable } from '@angular/core';
import { HttpClient, HttpEvent } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ApplicationConfiguration } from '../app.config';

@Injectable({
    providedIn: 'root'
})
export class MarkdownConversionService {
    private apiUrl: string;

    constructor(private http: HttpClient) {
        this.apiUrl = ApplicationConfiguration.Get().ApiServiceLink + '/markdownconversiontools';
    }

    convertFile(endpointSlug: string, file: File | null, outputFilename?: string, fileKey?: string): Observable<HttpEvent<any>> {
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

        return this.http.post(`${this.apiUrl}/${finalEndpoint}`, formData, {
            reportProgress: true,
            observe: 'events'
        });
    }

    downloadFile(filename: string): Observable<Blob> {
        return this.http.get(`${this.apiUrl}/download/${filename}`, {
            responseType: 'blob'
        });
    }
}
