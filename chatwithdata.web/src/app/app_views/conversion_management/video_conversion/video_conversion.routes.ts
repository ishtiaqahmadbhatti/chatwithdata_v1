import { Routes } from '@angular/router';

export const VideoConversionRoutes: Routes = [
    {
        path: '',
        loadComponent: () => import('./video-conversion.component').then(c => c.VideoConversionComponent)
    },
    {
        path: 'mov-to-mp4',
        loadComponent: () => import('./mov-to-mp4/mov-to-mp4.component').then(c => c.MovToMp4Component)
    },
    {
        path: 'mkv-to-mp4',
        loadComponent: () => import('./mkv-to-mp4/mkv-to-mp4.component').then(c => c.MkvToMp4Component)
    },
    {
        path: 'avi-to-mp4',
        loadComponent: () => import('./avi-to-mp4/avi-to-mp4.component').then(c => c.AviToMp4Component)
    },
    {
        path: 'mp4-to-mp3',
        loadComponent: () => import('./mp4-to-mp3/mp4-to-mp3.component').then(c => c.Mp4ToMp3Component)
    },

];
