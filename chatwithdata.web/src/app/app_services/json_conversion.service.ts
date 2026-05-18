import { Injectable } from '@angular/core';
import { HttpClient, HttpEvent } from '@angular/common/http';
import { ApplicationConfiguration } from '../app.config';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class JSONConversionService {

  private apiUrl: string;
  private serverBaseUrl: string;
  private jsonToolsUrl: string;

  constructor(private http: HttpClient) {
    const config = ApplicationConfiguration.Get();
    this.apiUrl = config.ApiServiceLink;
    this.serverBaseUrl = config.ServerBaseUrl;
    this.jsonToolsUrl = `${this.apiUrl}/jsonconversiontools`;
  }

  convertJsonToCsv(file: File, delimiter?: string, outputFilename?: string): Observable<HttpEvent<any>> {
    const formData: FormData = new FormData();
    formData.append('file', file, file.name);
    if (delimiter) {
      formData.append('delimiter', delimiter);
    }
    if (outputFilename) {
      formData.append('filename', outputFilename);
    }
    return this.http.post(`${this.jsonToolsUrl}/json-to-csv`, formData, {
      reportProgress: true,
      observe: 'events'
    });
  }

  ConvertFile(endpointSlug: string, file: File | null, outputFilename?: string, fileKey?: string, extraParams?: Record<string, string>): Observable<HttpEvent<any>> {
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
    if (extraParams) {
      Object.keys(extraParams).forEach(key => {
        formData.append(key, extraParams[key]);
      });
    }

    // Handle AI tools mapping (e.g., pdf-to-json-ai -> ai/pdf-to-json)
    let finalEndpoint = endpointSlug;
    if (endpointSlug.endsWith('-ai')) {
      const parts = endpointSlug.split('-');
      parts.pop(); // Remove 'ai'
      finalEndpoint = `ai/${parts.join('-')}`;
    }

    return this.http.post(`${this.jsonToolsUrl}/${finalEndpoint}`, formData, {
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

  validateJsonFile(file: File): Observable<any> {
    const formData = new FormData();
    formData.append('file', file, file.name);
    return this.http.post(`${this.jsonToolsUrl}/json-validator`, formData);
  }

  validateJsonText(text: string): Observable<any> {
    const formData = new FormData();
    formData.append('json_text', text);
    return this.http.post(`${this.jsonToolsUrl}/json-validator`, formData);
  }

  formatJsonText(text: string, indent: number, filename?: string): Observable<any> {
    const formData = new FormData();
    formData.append('json_text', text);
    formData.append('indent', indent.toString());
    if (filename) {
      formData.append('filename', filename);
    }
    return this.http.post(`${this.jsonToolsUrl}/json-formatter`, formData);
  }
}
