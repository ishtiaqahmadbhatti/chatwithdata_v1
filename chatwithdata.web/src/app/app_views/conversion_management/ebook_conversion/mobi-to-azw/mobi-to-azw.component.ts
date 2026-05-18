import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseEbookToolComponent } from '../base-ebook-tool.component';

@Component({
  selector: 'app-mobi-to-azw',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './mobi-to-azw.component.html',
  styleUrl: './mobi-to-azw.component.css',
  standalone: true
})
export class MobiToAzwComponent extends BaseEbookToolComponent {
  toolId = 'mobi-to-azw';
}
