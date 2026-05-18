import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseCsvToolComponent } from '../base-csv-tool.component';

@Component({
  selector: 'app-csv-to-srt',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './csv-to-srt.component.html',
  styleUrl: './csv-to-srt.component.css',
  standalone: true
})
export class CsvToSrtComponent extends BaseCsvToolComponent {
  toolId = 'csv-to-srt';
}
