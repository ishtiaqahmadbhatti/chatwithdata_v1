import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseWebsiteToolComponent } from '../base-website-tool.component';

@Component({
  selector: 'app-pdf-to-html',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './pdf-to-html.component.html',
  styleUrl: './pdf-to-html.component.css',
  standalone: true
})
export class PdfToHtmlComponent extends BaseWebsiteToolComponent {
  toolId = 'pdf-to-html';
}
