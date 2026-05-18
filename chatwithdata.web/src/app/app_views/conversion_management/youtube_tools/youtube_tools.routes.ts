import { Routes } from '@angular/router';

export const YOUTUBE_TOOLS_ROUTES: Routes = [
    {
        path: '',
        loadComponent: () => import('./youtube-tools.component').then(c => c.YoutubeToolsComponent)
    }
];
