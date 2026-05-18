import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseWebsiteToolComponent } from '../base-website-tool.component';

@Component({
  selector: 'app-html-table-to-csv',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './html-table-to-csv.component.html',
  styleUrl: './html-table-to-csv.component.css',
  standalone: true
})
export class HtmlTableToCsvComponent extends BaseWebsiteToolComponent {
  toolId = 'html-table-to-csv';
}
