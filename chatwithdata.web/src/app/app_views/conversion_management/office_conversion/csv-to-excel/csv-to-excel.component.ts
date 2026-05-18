import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseOfficeToolComponent } from '../base-office-tool.component';

@Component({
  selector: 'app-csv-to-excel',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './csv-to-excel.component.html',
  styleUrl: './csv-to-excel.component.css',
  standalone: true
})
export class CsvToExcelComponent extends BaseOfficeToolComponent {
  toolId = 'csv-to-excel';
}
