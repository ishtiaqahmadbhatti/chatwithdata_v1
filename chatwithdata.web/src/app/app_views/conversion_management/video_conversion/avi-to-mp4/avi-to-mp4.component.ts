import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseVideoToolComponent } from '../base-video-tool.component';

@Component({
  selector: 'app-avi-to-mp4',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './avi-to-mp4.component.html',
  styleUrl: './avi-to-mp4.component.css',
  standalone: true
})
export class AviToMp4Component extends BaseVideoToolComponent {
  toolId = 'avi-to-mp4';
}
