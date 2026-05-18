import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseEbookToolComponent } from '../base-ebook-tool.component';

@Component({
  selector: 'app-mobi-to-pdf',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './mobi-to-pdf.component.html',
  styleUrl: './mobi-to-pdf.component.css',
  standalone: true
})
export class MobiToPdfComponent extends BaseEbookToolComponent {
  toolId = 'mobi-to-pdf';
}
