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
        return this.http.post(`${this.apiUrl}/youtubetools/extract-data`, {
            video_url: videoUrl
        });
    }

    downloadVideo(videoUrl: string, quality: string = 'highest'): Observable<any> {
        return this.http.post(`${this.apiUrl}/youtubetools/download`, {
            video_url: videoUrl,
            quality: quality
        });
    }

    downloadFile(filename: string): Observable<Blob> {
        return this.http.get(`${this.apiUrl}/youtubetools/download-file/${filename}`, {
            responseType: 'blob'
        });
    }
}
