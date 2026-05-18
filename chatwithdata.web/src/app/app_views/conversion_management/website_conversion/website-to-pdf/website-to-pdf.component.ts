import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseWebsiteToolComponent } from '../base-website-tool.component';

@Component({
  selector: 'app-website-to-pdf',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './website-to-pdf.component.html',
  styleUrl: './website-to-pdf.component.css',
  standalone: true
})
export class WebsiteToPdfComponent extends BaseWebsiteToolComponent {
  toolId = 'website-to-pdf';
}
