import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseImageToolComponent } from '../base-image-tool.component';

@Component({
  selector: 'app-webp-to-png',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './webp-to-png.component.html',
  styleUrl: './webp-to-png.component.css',
  standalone: true
})
export class WebpToPngComponent extends BaseImageToolComponent {
  toolId = 'webp-to-png';
}
