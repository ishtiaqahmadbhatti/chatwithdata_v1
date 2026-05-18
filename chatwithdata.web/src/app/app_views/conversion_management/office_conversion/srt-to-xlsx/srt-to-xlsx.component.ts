import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseOfficeToolComponent } from '../base-office-tool.component';

@Component({
  selector: 'app-srt-to-xlsx',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './srt-to-xlsx.component.html',
  styleUrl: './srt-to-xlsx.component.css',
  standalone: true
})
export class SrtToXlsxComponent extends BaseOfficeToolComponent {
  toolId = 'srt-to-xlsx';
}
