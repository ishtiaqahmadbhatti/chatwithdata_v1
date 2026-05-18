import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseAudioToolComponent } from '../base-audio-tool.component';

@Component({
  selector: 'app-mp4-to-mp3',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './mp4-to-mp3.component.html',
  styleUrl: './mp4-to-mp3.component.css',
  standalone: true
})
export class Mp4ToMp3Component extends BaseAudioToolComponent {
  toolId = 'mp4-to-mp3';
}
