import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BasePdfToolComponent } from '../base-pdf-tool.component';

@Component({
  selector: 'app-oxps-to-pdf',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './oxps-to-pdf.component.html',
  styleUrl: './oxps-to-pdf.component.css',
  standalone: true
})
export class OxpsToPdfComponent extends BasePdfToolComponent {
  toolId = 'oxps-to-pdf';
}
