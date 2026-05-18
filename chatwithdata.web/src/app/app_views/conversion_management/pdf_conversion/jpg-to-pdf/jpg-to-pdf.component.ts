import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BasePdfToolComponent } from '../base-pdf-tool.component';

@Component({
  selector: 'app-jpg-to-pdf',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './jpg-to-pdf.component.html',
  styleUrl: './jpg-to-pdf.component.css',
  standalone: true
})
export class JpgToPdfComponent extends BasePdfToolComponent {
  toolId = 'jpg-to-pdf';
}
