import { Routes } from '@angular/router';

export const AGENTIC_RAG_ROUTES: Routes = [
    {
        path: '',
        loadComponent: () => import('./agentic-rag.component').then(c => c.AgenticRagComponent)
    }
];
