import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseImageToolComponent } from '../base-image-tool.component';

@Component({
  selector: 'app-webp-to-ppm',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './webp-to-ppm.component.html',
  styleUrl: './webp-to-ppm.component.css',
  standalone: true
})
export class WebpToPpmComponent extends BaseImageToolComponent {
  toolId = 'webp-to-ppm';
}
