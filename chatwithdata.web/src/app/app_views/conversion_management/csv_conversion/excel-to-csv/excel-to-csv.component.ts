import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseCsvToolComponent } from '../base-csv-tool.component';

@Component({
  selector: 'app-excel-to-csv',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './excel-to-csv.component.html',
  styleUrl: './excel-to-csv.component.css',
  standalone: true
})
export class ExcelToCsvComponent extends BaseCsvToolComponent {
  toolId = 'excel-to-csv';
}
