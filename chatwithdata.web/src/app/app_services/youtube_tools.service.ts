import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ApplicationConfiguration } from '../app.config';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class YoutubeToolsService {
    private apiUrl: string;
    private serverBaseUrl: string;

    constructor(private http: HttpClient) {
        const config = ApplicationConfiguration.Get();
        this.apiUrl = config.ApiServiceLink;
        this.serverBaseUrl = config.ServerBaseUrl;
    }

    extractData(videoUrl: string): Observable<any> {
        const formData = new FormData();
        formData.append('url', videoUrl);
        return this.http.post(`${this.apiUrl}/youtubetools/extract-data`, formData);
    }

    downloadVideo(videoUrl: string, quality: string = 'highest'): Observable<any> {
        const formData = new FormData();
        formData.append('url', videoUrl);
        
        // Map frontend "highest" to backend "best" requirement
        const mappedQuality = quality === 'highest' ? 'best' : quality;
        formData.append('quality', mappedQuality);
        formData.append('output_format', 'mp4');
        
        return this.http.post(`${this.apiUrl}/youtubetools/download`, formData);
    }

    downloadFile(filename: string): Observable<Blob> {
        return this.http.get(`${this.apiUrl}/youtubetools/download-file/${filename}`, {
            responseType: 'blob'
        });
    }
}
