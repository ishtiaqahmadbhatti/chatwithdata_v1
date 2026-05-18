import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BasePdfToolComponent } from '../base-pdf-tool.component';

@Component({
  selector: 'app-markdown-to-pdf',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './markdown-to-pdf.component.html',
  styleUrl: './markdown-to-pdf.component.css',
  standalone: true
})
export class MarkdownToPdfComponent extends BasePdfToolComponent {
  toolId = 'markdown-to-pdf';
}
