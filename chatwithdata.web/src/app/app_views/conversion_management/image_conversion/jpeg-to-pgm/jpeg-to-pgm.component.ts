import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseImageToolComponent } from '../base-image-tool.component';

@Component({
  selector: 'app-jpeg-to-pgm',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './jpeg-to-pgm.component.html',
  styleUrl: './jpeg-to-pgm.component.css',
  standalone: true
})
export class JpegToPgmComponent extends BaseImageToolComponent {
  toolId = 'jpeg-to-pgm';
}
