import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseAudioToolComponent } from '../base-audio-tool.component';

@Component({
  selector: 'app-mp3-to-wav',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './mp3-to-wav.component.html',
  styleUrl: './mp3-to-wav.component.css',
  standalone: true
})
export class Mp3ToWavComponent extends BaseAudioToolComponent {
  toolId = 'mp3-to-wav';
}
