import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseCsvToolComponent } from '../base-csv-tool.component';

@Component({
  selector: 'app-json-to-csv',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './json-to-csv.component.html',
  styleUrl: './json-to-csv.component.css',
  standalone: true
})
export class JsonToCsvComponent extends BaseCsvToolComponent {
  toolId = 'json-to-csv';
}
