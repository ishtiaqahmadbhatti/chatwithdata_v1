import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseEbookToolComponent } from '../base-ebook-tool.component';

@Component({
  selector: 'app-azw-to-mobi',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './azw-to-mobi.component.html',
  styleUrl: './azw-to-mobi.component.css',
  standalone: true
})
export class AzwToMobiComponent extends BaseEbookToolComponent {
  toolId = 'azw-to-mobi';
}
