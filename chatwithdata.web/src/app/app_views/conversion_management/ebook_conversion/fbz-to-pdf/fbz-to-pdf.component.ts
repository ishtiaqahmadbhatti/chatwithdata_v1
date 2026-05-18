import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseEbookToolComponent } from '../base-ebook-tool.component';

@Component({
  selector: 'app-fbz-to-pdf',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './fbz-to-pdf.component.html',
  styleUrl: './fbz-to-pdf.component.css',
  standalone: true
})
export class FbzToPdfComponent extends BaseEbookToolComponent {
  toolId = 'fbz-to-pdf';
}
