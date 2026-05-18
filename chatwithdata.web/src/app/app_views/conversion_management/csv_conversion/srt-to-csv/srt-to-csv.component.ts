import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseCsvToolComponent } from '../base-csv-tool.component';

@Component({
  selector: 'app-srt-to-csv',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './srt-to-csv.component.html',
  styleUrl: './srt-to-csv.component.css',
  standalone: true
})
export class SrtToCsvComponent extends BaseCsvToolComponent {
  toolId = 'srt-to-csv';
}
