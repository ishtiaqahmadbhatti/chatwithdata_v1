import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BasePdfToolComponent } from '../base-pdf-tool.component';

@Component({
  selector: 'app-pdf-to-excel',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './pdf-to-excel.component.html',
  styleUrl: './pdf-to-excel.component.css',
  standalone: true
})
export class PdfToExcelComponent extends BasePdfToolComponent {
  toolId = 'pdf-to-excel';
}
