import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseImageToolComponent } from '../base-image-tool.component';

@Component({
  selector: 'app-jpeg-to-ppm',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './jpeg-to-ppm.component.html',
  styleUrl: './jpeg-to-ppm.component.css',
  standalone: true
})
export class JpegToPpmComponent extends BaseImageToolComponent {
  toolId = 'jpeg-to-ppm';
}
