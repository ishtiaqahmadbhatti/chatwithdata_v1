import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseEbookToolComponent } from '../base-ebook-tool.component';

@Component({
  selector: 'app-mobi-to-epub',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './mobi-to-epub.component.html',
  styleUrl: './mobi-to-epub.component.css',
  standalone: true
})
export class MobiToEpubComponent extends BaseEbookToolComponent {
  toolId = 'mobi-to-epub';
}
