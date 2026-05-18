import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseImageToolComponent } from '../base-image-tool.component';

@Component({
  selector: 'app-tiff-to-webp',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './tiff-to-webp.component.html',
  styleUrl: './tiff-to-webp.component.css',
  standalone: true
})
export class TiffToWebpComponent extends BaseImageToolComponent {
  toolId = 'tiff-to-webp';
}
