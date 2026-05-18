import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

@Component({
    selector: 'app-helpdesk-dashboard',
    standalone: true,
    imports: [CommonModule, RouterLink],
    templateUrl: './helpdesk-dashboard.component.html',
    styleUrl: './helpdesk-dashboard.component.css'
})
export class HelpdeskDashboardComponent {
    helpOptions = [
        {
            title: 'Frequently Asked Questions',
            description: 'Find answers to common questions about accounts, billing, and conversions.',
            icon: 'fas fa-question-circle',
            link: '/helpdesk/frequent-questions',
            color: '#48bb78' // Green
        },
        {
            title: 'Technical Support',
            description: 'Report bugs, conversion failures, or other technical issues.',
            icon: 'fas fa-tools',
            link: '/helpdesk/technical-support',
            color: '#4299e1' // Blue
        },
        {
            title: 'Submit a Query',
            description: 'Have a general question? Send us a message and we will help you out.',
            icon: 'fas fa-envelope-open-text',
            link: '/helpdesk/customer-queries',
            color: '#ed8936' // Orange
        },
        {
            title: 'Share Feedback',
            description: 'We value your suggestions! Let us know how we can improve.',
            icon: 'fas fa-comment-dots',
            link: '/helpdesk/customer-feedback',
            color: '#9f7aea' // Purple
        },
        {
            title: 'Specific Tool Feedback',
            description: 'Rate specific tools like PDF, Image, or Text converters and tell us what you think.',
            icon: 'fas fa-thumbs-up',
            link: '/helpdesk/tool-feedback',
            color: '#f56565' // Red
        }
    ];
}
