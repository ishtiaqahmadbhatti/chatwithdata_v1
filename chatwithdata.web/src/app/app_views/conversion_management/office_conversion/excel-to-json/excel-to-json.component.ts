import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseOfficeToolComponent } from '../base-office-tool.component';

@Component({
  selector: 'app-excel-to-json',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './excel-to-json.component.html',
  styleUrl: './excel-to-json.component.css',
  standalone: true
})
export class ExcelToJsonComponent extends BaseOfficeToolComponent {
  toolId = 'excel-to-json';
}
