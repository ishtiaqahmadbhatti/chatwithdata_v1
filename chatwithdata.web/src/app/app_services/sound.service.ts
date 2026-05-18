import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class SoundService {
  private successAudio: HTMLAudioElement;
  private errorAudio: HTMLAudioElement;

  constructor() {
    // Using public URLs for now. In production, these should be moved to src/assets/sounds/
    this.successAudio = new Audio('https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3');
    this.errorAudio = new Audio('https://raw.githubusercontent.com/Roahn333singh/Faah..Sound-Extention/main/fahhhhh.mp3');

    // Preload sounds
    this.successAudio.load();
    this.errorAudio.load();
  }

  playSuccess() {
    this.playSound(this.successAudio);
  }

  playError() {
    this.playSound(this.errorAudio);
  }

  private playSound(audio: HTMLAudioElement) {
    audio.currentTime = 0;
    audio.play().catch(error => {
      console.warn('Sound playback failed (possibly blocked by browser):', error);
    });
  }
}
