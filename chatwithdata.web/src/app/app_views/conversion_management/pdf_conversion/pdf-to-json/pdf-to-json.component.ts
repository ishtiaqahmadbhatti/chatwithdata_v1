import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BasePdfToolComponent } from '../base-pdf-tool.component';

@Component({
  selector: 'app-pdf-to-json',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './pdf-to-json.component.html',
  styleUrl: './pdf-to-json.component.css',
  standalone: true
})
export class PdfToJsonComponent extends BasePdfToolComponent {
  toolId = 'pdf-to-json';
}
