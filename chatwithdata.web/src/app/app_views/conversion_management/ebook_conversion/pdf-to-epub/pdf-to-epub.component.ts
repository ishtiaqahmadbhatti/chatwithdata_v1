import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseEbookToolComponent } from '../base-ebook-tool.component';

@Component({
  selector: 'app-pdf-to-epub',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './pdf-to-epub.component.html',
  styleUrl: './pdf-to-epub.component.css',
  standalone: true
})
export class PdfToEpubComponent extends BaseEbookToolComponent {
  toolId = 'pdf-to-epub';
}
