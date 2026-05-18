import { Routes } from '@angular/router';

export const HelpdeskManagementRoutes: Routes = [
    {
        path: '',
        loadComponent: () => import('./helpdesk-dashboard/helpdesk-dashboard.component').then(c => c.HelpdeskDashboardComponent)
    },
    {
        path: 'customer-feedback',
        loadComponent: () => import('./customer-feedback/customer-feedback.component').then(c => c.CustomerFeedbackComponent)
    },
    {
        path: 'technical-support',
        loadComponent: () => import('./technical-support/technical-support.component').then(c => c.TechnicalSupportComponent)
    },
    {
        path: 'customer-queries',
        loadComponent: () => import('./customer-queries/customer-queries.component').then(c => c.CustomerQueriesComponent)
    },
    {
        path: 'frequent-questions',
        loadComponent: () => import('./frequently-asked-questions/frequently-asked-questions.component').then(c => c.FrequentlyAskedQuestionsComponent)
    },
    {
        path: 'tool-feedback',
        loadComponent: () => import('./tool-feedback/tool-feedback.component').then(c => c.ToolFeedbackComponent)
    }
];
