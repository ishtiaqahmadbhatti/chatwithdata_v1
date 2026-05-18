import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseWebsiteToolComponent } from '../base-website-tool.component';

@Component({
  selector: 'app-word-to-html',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './word-to-html.component.html',
  styleUrl: './word-to-html.component.css',
  standalone: true
})
export class WordToHtmlComponent extends BaseWebsiteToolComponent {
  toolId = 'word-to-html';
}
