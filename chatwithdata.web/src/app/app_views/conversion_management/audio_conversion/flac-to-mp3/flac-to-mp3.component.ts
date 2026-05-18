import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseAudioToolComponent } from '../base-audio-tool.component';

@Component({
  selector: 'app-flac-to-mp3',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './flac-to-mp3.component.html',
  styleUrl: './flac-to-mp3.component.css',
  standalone: true
})
export class FlacToMp3Component extends BaseAudioToolComponent {
  toolId = 'flac-to-mp3';
}
