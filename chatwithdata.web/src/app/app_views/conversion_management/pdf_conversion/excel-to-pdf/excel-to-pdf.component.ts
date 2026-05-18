import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BasePdfToolComponent } from '../base-pdf-tool.component';

@Component({
  selector: 'app-excel-to-pdf',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './excel-to-pdf.component.html',
  styleUrl: './excel-to-pdf.component.css',
  standalone: true
})
export class ExcelToPdfComponent extends BasePdfToolComponent {
  toolId = 'excel-to-pdf';
}
