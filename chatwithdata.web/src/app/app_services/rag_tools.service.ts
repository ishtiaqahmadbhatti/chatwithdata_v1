import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ApplicationConfiguration } from '../app.config';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class RagToolsService {
    private apiUrl: string;

    constructor(private http: HttpClient) {
        const config = ApplicationConfiguration.Get();
        this.apiUrl = config.ApiServiceLink;
    }

    ingestVideo(videoData: any): Observable<any> {
        return this.http.post(`${this.apiUrl}/ragtools/ingest`, videoData);
    }

    queryVideo(videoId: string, query: string): Observable<any> {
        return this.http.post(`${this.apiUrl}/ragtools/query`, {
            video_id: videoId,
            question: query
        });
    }

    getSessions(): Observable<any> {
        return this.http.get(`${this.apiUrl}/ragtools/sessions`);
    }

    removeSession(videoId: string): Observable<any> {
        return this.http.delete(`${this.apiUrl}/ragtools/sessions/${videoId}`);
    }
}
