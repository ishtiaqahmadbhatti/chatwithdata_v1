import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseEbookToolComponent } from '../base-ebook-tool.component';

@Component({
  selector: 'app-pdf-to-fbz',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './pdf-to-fbz.component.html',
  styleUrl: './pdf-to-fbz.component.css',
  standalone: true
})
export class PdfToFbzComponent extends BaseEbookToolComponent {
  toolId = 'pdf-to-fbz';
}
