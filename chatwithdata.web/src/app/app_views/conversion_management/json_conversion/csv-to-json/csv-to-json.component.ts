import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseJsonToolComponent } from '../base-json-tool.component';

@Component({
  selector: 'app-csv-to-json',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './csv-to-json.component.html',
  styleUrl: './csv-to-json.component.css',
  standalone: true
})
export class CsvToJsonComponent extends BaseJsonToolComponent {
  toolId = 'csv-to-json';
}
