import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseOfficeToolComponent } from '../base-office-tool.component';

@Component({
  selector: 'app-json-objects-to-excel',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './json-objects-to-excel.component.html',
  styleUrl: './json-objects-to-excel.component.css',
  standalone: true
})
export class JsonObjectsToExcelComponent extends BaseOfficeToolComponent {
  toolId = 'json-objects-to-excel';
}
