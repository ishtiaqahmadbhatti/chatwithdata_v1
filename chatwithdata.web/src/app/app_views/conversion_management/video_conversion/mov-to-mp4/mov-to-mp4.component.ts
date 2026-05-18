import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseVideoToolComponent } from '../base-video-tool.component';

@Component({
  selector: 'app-mov-to-mp4',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './mov-to-mp4.component.html',
  styleUrl: './mov-to-mp4.component.css',
  standalone: true
})
export class MovToMp4Component extends BaseVideoToolComponent {
  toolId = 'mov-to-mp4';
}
