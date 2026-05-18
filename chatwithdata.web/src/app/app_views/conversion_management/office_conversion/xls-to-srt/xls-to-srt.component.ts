import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseOfficeToolComponent } from '../base-office-tool.component';

@Component({
  selector: 'app-xls-to-srt',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './xls-to-srt.component.html',
  styleUrl: './xls-to-srt.component.css',
  standalone: true
})
export class XlsToSrtComponent extends BaseOfficeToolComponent {
  toolId = 'xls-to-srt';
}
