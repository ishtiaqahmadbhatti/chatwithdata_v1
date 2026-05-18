import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseOcrToolComponent } from '../base-ocr-tool.component';

@Component({
  selector: 'app-pdf-image-to-pdf-text',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './pdf-image-to-pdf-text.component.html',
  styleUrl: './pdf-image-to-pdf-text.component.css',
  standalone: true
})
export class PdfImageToPdfTextComponent extends BaseOcrToolComponent {
  toolId = 'pdf-image-to-pdf-text';
}
