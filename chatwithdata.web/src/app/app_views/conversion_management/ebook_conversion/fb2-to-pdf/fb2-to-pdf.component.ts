import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseEbookToolComponent } from '../base-ebook-tool.component';

@Component({
  selector: 'app-fb2-to-pdf',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './fb2-to-pdf.component.html',
  styleUrl: './fb2-to-pdf.component.css',
  standalone: true
})
export class Fb2ToPdfComponent extends BaseEbookToolComponent {
  toolId = 'fb2-to-pdf';
}
