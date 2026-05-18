import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseEbookToolComponent } from '../base-ebook-tool.component';

@Component({
  selector: 'app-azw3-to-pdf',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './azw3-to-pdf.component.html',
  styleUrl: './azw3-to-pdf.component.css',
  standalone: true
})
export class Azw3ToPdfComponent extends BaseEbookToolComponent {
  toolId = 'azw3-to-pdf';
}
