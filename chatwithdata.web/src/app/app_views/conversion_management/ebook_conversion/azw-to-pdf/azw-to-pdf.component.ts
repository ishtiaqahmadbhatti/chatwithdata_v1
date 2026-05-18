import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseEbookToolComponent } from '../base-ebook-tool.component';

@Component({
  selector: 'app-azw-to-pdf',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './azw-to-pdf.component.html',
  styleUrl: './azw-to-pdf.component.css',
  standalone: true
})
export class AzwToPdfComponent extends BaseEbookToolComponent {
  toolId = 'azw-to-pdf';
}
