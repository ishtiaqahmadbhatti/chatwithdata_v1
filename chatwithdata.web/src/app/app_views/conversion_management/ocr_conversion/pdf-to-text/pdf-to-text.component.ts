import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseOcrToolComponent } from '../base-ocr-tool.component';

@Component({
  selector: 'app-pdf-to-text',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './pdf-to-text.component.html',
  styleUrl: './pdf-to-text.component.css',
  standalone: true
})
export class PdfToTextComponent extends BaseOcrToolComponent {
  toolId = 'pdf-to-text';
}
