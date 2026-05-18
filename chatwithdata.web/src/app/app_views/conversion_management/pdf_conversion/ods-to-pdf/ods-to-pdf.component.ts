import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BasePdfToolComponent } from '../base-pdf-tool.component';

@Component({
  selector: 'app-ods-to-pdf',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './ods-to-pdf.component.html',
  styleUrl: './ods-to-pdf.component.css',
  standalone: true
})
export class OdsToPdfComponent extends BasePdfToolComponent {
  toolId = 'ods-to-pdf';
}
