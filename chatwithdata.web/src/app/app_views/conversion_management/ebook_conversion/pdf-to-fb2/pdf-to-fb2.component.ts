import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseEbookToolComponent } from '../base-ebook-tool.component';

@Component({
  selector: 'app-pdf-to-fb2',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './pdf-to-fb2.component.html',
  styleUrl: './pdf-to-fb2.component.css',
  standalone: true
})
export class PdfToFb2Component extends BaseEbookToolComponent {
  toolId = 'pdf-to-fb2';
}
