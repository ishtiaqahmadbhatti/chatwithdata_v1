import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseOfficeToolComponent } from '../base-office-tool.component';

@Component({
  selector: 'app-srt-to-excel',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './srt-to-excel.component.html',
  styleUrl: './srt-to-excel.component.css',
  standalone: true
})
export class SrtToExcelComponent extends BaseOfficeToolComponent {
  toolId = 'srt-to-excel';
}
