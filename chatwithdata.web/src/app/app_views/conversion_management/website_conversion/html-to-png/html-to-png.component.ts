import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseWebsiteToolComponent } from '../base-website-tool.component';

@Component({
  selector: 'app-html-to-png',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './html-to-png.component.html',
  styleUrl: './html-to-png.component.css',
  standalone: true
})
export class HtmlToPngComponent extends BaseWebsiteToolComponent {
  toolId = 'html-to-png';
}
