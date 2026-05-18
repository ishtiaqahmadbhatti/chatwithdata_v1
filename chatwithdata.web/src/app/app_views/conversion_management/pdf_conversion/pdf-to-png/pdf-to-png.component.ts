import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BasePdfToolComponent } from '../base-pdf-tool.component';

@Component({
  selector: 'app-pdf-to-png',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './pdf-to-png.component.html',
  styleUrl: './pdf-to-png.component.css',
  standalone: true
})
export class PdfToPngComponent extends BasePdfToolComponent {
  toolId = 'pdf-to-png';
}
