import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BasePdfToolComponent } from '../base-pdf-tool.component';

@Component({
  selector: 'app-pdf-to-word',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './pdf-to-word.component.html',
  styleUrl: './pdf-to-word.component.css',
  standalone: true
})
export class PdfToWordComponent extends BasePdfToolComponent {
  toolId = 'pdf-to-word';
}
