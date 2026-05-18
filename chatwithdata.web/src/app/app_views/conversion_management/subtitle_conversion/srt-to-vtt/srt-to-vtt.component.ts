import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseSubtitleToolComponent } from '../base-subtitle-tool.component';

@Component({
  selector: 'app-srt-to-vtt',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './srt-to-vtt.component.html',
  styleUrl: './srt-to-vtt.component.css',
  standalone: true
})
export class SrtToVttComponent extends BaseSubtitleToolComponent {
  toolId = 'srt-to-vtt';
}
