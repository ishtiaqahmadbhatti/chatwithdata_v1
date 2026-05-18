import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseImageToolComponent } from '../base-image-tool.component';

@Component({
  selector: 'app-pdf-to-jpg',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './pdf-to-jpg.component.html',
  styleUrl: './pdf-to-jpg.component.css',
  standalone: true
})
export class PdfToJpgComponent extends BaseImageToolComponent {
  toolId = 'pdf-to-jpg';
}
