import { Routes } from '@angular/router';

export const AudioConversionRoutes: Routes = [
    {
        path: '',
        loadComponent: () => import('./audio-conversion.component').then(c => c.AudioConversionComponent)
    },
    {
        path: 'mp4-to-mp3',
        loadComponent: () => import('./mp4-to-mp3/mp4-to-mp3.component').then(c => c.Mp4ToMp3Component)
    },
    {
        path: 'wav-to-mp3',
        loadComponent: () => import('./wav-to-mp3/wav-to-mp3.component').then(c => c.WavToMp3Component)
    },
    {
        path: 'flac-to-mp3',
        loadComponent: () => import('./flac-to-mp3/flac-to-mp3.component').then(c => c.FlacToMp3Component)
    },
    {
        path: 'mp3-to-wav',
        loadComponent: () => import('./mp3-to-wav/mp3-to-wav.component').then(c => c.Mp3ToWavComponent)
    },
    {
        path: 'flac-to-wav',
        loadComponent: () => import('./flac-to-wav/flac-to-wav.component').then(c => c.FlacToWavComponent)
    },
    {
        path: 'wav-to-flac',
        loadComponent: () => import('./wav-to-flac/wav-to-flac.component').then(c => c.WavToFlacComponent)
    },
    {


        path: 'trim-audio',
        loadComponent: () => import('./trim-audio/trim-audio.component').then(c => c.TrimAudioComponent)
    },
    {
        path: 'audio-to-text',
        loadComponent: () => import('./audio-to-text/audio-to-text.component').then(c => c.AudioToTextComponent)
    },

];
