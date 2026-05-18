import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseSubtitleToolComponent } from '../base-subtitle-tool.component';

@Component({
  selector: 'app-vtt-to-srt',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './vtt-to-srt.component.html',
  styleUrl: './vtt-to-srt.component.css',
  standalone: true
})
export class VttToSrtComponent extends BaseSubtitleToolComponent {
  toolId = 'vtt-to-srt';
}
