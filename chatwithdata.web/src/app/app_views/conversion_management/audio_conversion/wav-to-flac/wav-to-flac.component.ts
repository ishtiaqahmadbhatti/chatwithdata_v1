import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseAudioToolComponent } from '../base-audio-tool.component';

@Component({
  selector: 'app-wav-to-flac',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './wav-to-flac.component.html',
  styleUrl: './wav-to-flac.component.css',
  standalone: true
})
export class WavToFlacComponent extends BaseAudioToolComponent {
  toolId = 'wav-to-flac';
}
