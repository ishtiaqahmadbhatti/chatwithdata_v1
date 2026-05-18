import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseOfficeToolComponent } from '../base-office-tool.component';

@Component({
  selector: 'app-xlsx-to-srt',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './xlsx-to-srt.component.html',
  styleUrl: './xlsx-to-srt.component.css',
  standalone: true
})
export class XlsxToSrtComponent extends BaseOfficeToolComponent {
  toolId = 'xlsx-to-srt';
}
