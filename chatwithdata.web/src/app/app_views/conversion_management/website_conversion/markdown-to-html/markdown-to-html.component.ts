import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseWebsiteToolComponent } from '../base-website-tool.component';

@Component({
  selector: 'app-markdown-to-html',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './markdown-to-html.component.html',
  styleUrl: './markdown-to-html.component.css',
  standalone: true
})
export class MarkdownToHtmlComponent extends BaseWebsiteToolComponent {
  toolId = 'markdown-to-html';
}
