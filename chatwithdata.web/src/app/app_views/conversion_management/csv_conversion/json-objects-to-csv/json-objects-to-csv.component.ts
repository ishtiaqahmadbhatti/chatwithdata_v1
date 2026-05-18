import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseCsvToolComponent } from '../base-csv-tool.component';

@Component({
  selector: 'app-json-objects-to-csv',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './json-objects-to-csv.component.html',
  styleUrl: './json-objects-to-csv.component.css',
  standalone: true
})
export class JsonObjectsToCsvComponent extends BaseCsvToolComponent {
  toolId = 'json-objects-to-csv';
}
