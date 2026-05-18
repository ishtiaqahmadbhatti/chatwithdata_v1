import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseEbookToolComponent } from '../base-ebook-tool.component';

@Component({
  selector: 'app-azw-to-epub',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './azw-to-epub.component.html',
  styleUrl: './azw-to-epub.component.css',
  standalone: true
})
export class AzwToEpubComponent extends BaseEbookToolComponent {
  toolId = 'azw-to-epub';
}
