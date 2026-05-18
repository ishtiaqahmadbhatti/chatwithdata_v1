import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseOfficeToolComponent } from '../base-office-tool.component';

@Component({
  selector: 'app-bson-to-excel',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './bson-to-excel.component.html',
  styleUrl: './bson-to-excel.component.css',
  standalone: true
})
export class BsonToExcelComponent extends BaseOfficeToolComponent {
  toolId = 'bson-to-excel';
}
