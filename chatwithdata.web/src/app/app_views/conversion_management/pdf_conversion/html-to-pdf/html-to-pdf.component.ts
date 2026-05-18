import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BasePdfToolComponent } from '../base-pdf-tool.component';

@Component({
  selector: 'app-html-to-pdf',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './html-to-pdf.component.html',
  styleUrl: './html-to-pdf.component.css',
  standalone: true
})
export class HtmlToPdfComponent extends BasePdfToolComponent {
  toolId = 'html-to-pdf';
}
