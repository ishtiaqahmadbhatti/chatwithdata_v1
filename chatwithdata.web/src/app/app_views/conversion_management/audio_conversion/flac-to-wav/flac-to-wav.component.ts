import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseAudioToolComponent } from '../base-audio-tool.component';

@Component({
  selector: 'app-flac-to-wav',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './flac-to-wav.component.html',
  styleUrl: './flac-to-wav.component.css',
  standalone: true
})
export class FlacToWavComponent extends BaseAudioToolComponent {
  toolId = 'flac-to-wav';
}
