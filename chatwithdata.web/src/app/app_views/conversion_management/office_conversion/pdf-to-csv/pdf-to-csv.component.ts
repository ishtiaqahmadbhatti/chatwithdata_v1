import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseOfficeToolComponent } from '../base-office-tool.component';

@Component({
  selector: 'app-pdf-to-csv',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './pdf-to-csv.component.html',
  styleUrl: './pdf-to-csv.component.css',
  standalone: true
})
export class PdfToCsvComponent extends BaseOfficeToolComponent {
  toolId = 'pdf-to-csv';
}
