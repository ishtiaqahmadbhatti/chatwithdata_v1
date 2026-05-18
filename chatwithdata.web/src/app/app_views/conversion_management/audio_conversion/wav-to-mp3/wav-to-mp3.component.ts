import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseAudioToolComponent } from '../base-audio-tool.component';

@Component({
  selector: 'app-wav-to-mp3',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './wav-to-mp3.component.html',
  styleUrl: './wav-to-mp3.component.css',
  standalone: true
})
export class WavToMp3Component extends BaseAudioToolComponent {
  toolId = 'wav-to-mp3';
}
