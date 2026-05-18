import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseOfficeToolComponent } from '../base-office-tool.component';

@Component({
  selector: 'app-ods-to-excel',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './ods-to-excel.component.html',
  styleUrl: './ods-to-excel.component.css',
  standalone: true
})
export class OdsToExcelComponent extends BaseOfficeToolComponent {
  toolId = 'ods-to-excel';
}
