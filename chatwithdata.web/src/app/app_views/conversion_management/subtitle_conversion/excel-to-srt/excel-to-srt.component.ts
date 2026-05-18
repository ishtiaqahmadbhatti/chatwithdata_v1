import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseSubtitleToolComponent } from '../base-subtitle-tool.component';

@Component({
  selector: 'app-excel-to-srt',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './excel-to-srt.component.html',
  styleUrl: './excel-to-srt.component.css',
  standalone: true
})
export class ExcelToSrtComponent extends BaseSubtitleToolComponent {
  toolId = 'excel-to-srt';
}
