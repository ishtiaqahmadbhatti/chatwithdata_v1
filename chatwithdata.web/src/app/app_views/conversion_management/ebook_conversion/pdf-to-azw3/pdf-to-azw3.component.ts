import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseEbookToolComponent } from '../base-ebook-tool.component';

@Component({
  selector: 'app-pdf-to-azw3',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './pdf-to-azw3.component.html',
  styleUrl: './pdf-to-azw3.component.css',
  standalone: true
})
export class PdfToAzw3Component extends BaseEbookToolComponent {
  toolId = 'pdf-to-azw3';
}
