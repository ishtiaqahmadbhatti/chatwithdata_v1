import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseVideoToolComponent } from '../base-video-tool.component';

@Component({
  selector: 'app-mkv-to-mp4',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './mkv-to-mp4.component.html',
  styleUrl: './mkv-to-mp4.component.css',
  standalone: true
})
export class MkvToMp4Component extends BaseVideoToolComponent {
  toolId = 'mkv-to-mp4';
}
