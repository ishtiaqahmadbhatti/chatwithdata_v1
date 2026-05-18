import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseWebsiteToolComponent } from '../base-website-tool.component';

@Component({
  selector: 'app-excel-to-html',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './excel-to-html.component.html',
  styleUrl: './excel-to-html.component.css',
  standalone: true
})
export class ExcelToHtmlComponent extends BaseWebsiteToolComponent {
  toolId = 'excel-to-html';
}
