import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseCsvToolComponent } from '../base-csv-tool.component';

@Component({
  selector: 'app-ods-to-csv',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './ods-to-csv.component.html',
  styleUrl: './ods-to-csv.component.css',
  standalone: true
})
export class OdsToCsvComponent extends BaseCsvToolComponent {
  toolId = 'ods-to-csv';
}
