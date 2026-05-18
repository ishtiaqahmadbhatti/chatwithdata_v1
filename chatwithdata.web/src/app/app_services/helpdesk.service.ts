import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ApplicationConfiguration } from '../app.config';

@Injectable({
    providedIn: 'root'
})
export class HelpdeskService {
    private apiUrl: string;

    constructor(private http: HttpClient) {
        this.apiUrl = `${ApplicationConfiguration.Get().ApiServiceLink}/helpdesk`;
    }

    contactUs(data: any): Observable<any> {
        // Matches customer_contactus_support_details
        const payload = {
            full_name: data.name,
            email: data.email,
            subject: data.subject,
            message: data.message
        };
        return this.http.post(`${this.apiUrl}/contact-us`, payload);
    }

    submitQuery(data: any, file?: File): Observable<any> {
        // Matches customer_general_inquiries_details
        const formData = new FormData();
        formData.append('full_name', data.name);
        formData.append('email', data.email);
        formData.append('subject', data.subject);
        formData.append('query', data.query);
        if (file) {
            formData.append('file', file);
        }

        return this.http.post(`${this.apiUrl}/submit-query`, formData);
    }

    submitFAQ(data: any): Observable<any> {
        // Matches customer_frequently-asked-questions_details
        const payload = {
            question: data.question,
            category: data.category,
            user_email: data.email
        };
        return this.http.post(`${this.apiUrl}/faq`, payload);
    }

    submitTechnicalSupport(data: any, file?: File): Observable<any> {
        // Matches customer_technical_support_details
        const formData = new FormData();
        formData.append('full_name', data.name);
        formData.append('email', data.email);
        formData.append('issue_type', data.issueType);
        formData.append('description', data.description);
        formData.append('os_info', navigator.platform);
        formData.append('browser_info', navigator.userAgent);

        if (file) {
            formData.append('file', file);
        }

        return this.http.post(`${this.apiUrl}/technical-support`, formData);
    }

    shareFeedback(data: any): Observable<any> {
        // Matches customer_feedback_details
        const payload = {
            full_name: data.name,
            email: data.email,
            feedback: data.feedback,
            rating: data.rating
        };
        return this.http.post(`${this.apiUrl}/share-feedback`, payload);
    }

    submitToolFeedback(data: any): Observable<any> {
        // Matches customer_tool_feedback_details
        const payload = {
            tool_name: data.tool,
            category: data.category,
            rating: data.rating,
            feedback: data.message,
            user_email: data.email
        };
        return this.http.post(`${this.apiUrl}/tool-feedback`, payload);
    }
}
