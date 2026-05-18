import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseEbookToolComponent } from '../base-ebook-tool.component';

@Component({
  selector: 'app-epub-to-pdf',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './epub-to-pdf.component.html',
  styleUrl: './epub-to-pdf.component.css',
  standalone: true
})
export class EpubToPdfComponent extends BaseEbookToolComponent {
  toolId = 'epub-to-pdf';
}
