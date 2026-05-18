import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseCsvToolComponent } from '../base-csv-tool.component';

@Component({
  selector: 'app-bson-to-csv',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './bson-to-csv.component.html',
  styleUrl: './bson-to-csv.component.css',
  standalone: true
})
export class BsonToCsvComponent extends BaseCsvToolComponent {
  toolId = 'bson-to-csv';
}
